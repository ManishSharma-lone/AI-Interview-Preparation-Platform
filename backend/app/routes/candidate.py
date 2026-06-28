import json
from datetime import datetime, date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.database_models import User, Interview, Question, Answer, Feedback, Progress, Achievement, Leaderboard
from backend.app.schemas.api_schemas import (
    InterviewStart, InterviewResponse, QuestionResponse, AnswerSubmit,
    FeedbackResponse, DashboardMetrics, InterviewHistoryItem, LeaderboardItem
)
from backend.app.auth.auth_service import get_current_user
from backend.app.services.ai_service import AIService

router = APIRouter(prefix="/api/candidate", tags=["Candidate Dashboard & Flow"])

@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    progress = db.query(Progress).filter(Progress.user_id == current_user.id).first()
    if not progress:
        # Self-healing fallback if progress row doesn't exist
        progress = Progress(user_id=current_user.id)
        db.add(progress)
        db.commit()
        db.refresh(progress)

    # Calculate today's completed interviews count
    today = date.today()
    today_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "Completed",
        Interview.created_at >= datetime.combine(today, datetime.min.time())
    ).count()

    try:
        weak_list = json.loads(progress.weak_topics or "[]")
    except Exception:
        weak_list = []
        
    try:
        strong_list = json.loads(progress.strong_topics or "[]")
    except Exception:
        strong_list = []

    return DashboardMetrics(
        total_interviews=progress.total_interviews,
        average_score=round(progress.average_score, 1),
        best_score=round(progress.best_score, 1),
        weak_topics=weak_list,
        strong_topics=strong_list,
        streak_count=progress.streak_count,
        today_progress=today_interviews
    )

@router.post("/start-interview")
def start_interview(payload: InterviewStart, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Create Interview record
    new_interview = Interview(
        user_id=current_user.id,
        role_type=payload.role_type,
        difficulty=payload.difficulty,
        interview_type=payload.interview_type,
        num_questions=payload.num_questions,
        total_score=0.0,
        status="InProgress"
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    # 2. Call AI Service to generate questions
    ai_questions = AIService.generate_questions(
        role_type=payload.role_type,
        difficulty=payload.difficulty,
        interview_type=payload.interview_type,
        num_questions=payload.num_questions
    )

    # 3. Save questions to database
    question_records = []
    for q in ai_questions:
        db_q = Question(
            interview_id=new_interview.id,
            text=q.get("text", "Question text unavailable."),
            question_type=q.get("question_type", "Technical"),
            difficulty=q.get("difficulty", payload.difficulty),
            code_template=q.get("code_template"),
            test_cases=q.get("test_cases")
        )
        db.add(db_q)
        question_records.append(db_q)
    
    db.commit()

    # Refresh interview to link relationships
    db.refresh(new_interview)

    # Return interview details and the first question
    first_q = question_records[0]
    return {
        "interview_id": new_interview.id,
        "role_type": new_interview.role_type,
        "difficulty": new_interview.difficulty,
        "interview_type": new_interview.interview_type,
        "num_questions": new_interview.num_questions,
        "first_question": {
            "id": first_q.id,
            "text": first_q.text,
            "question_type": first_q.question_type,
            "code_template": first_q.code_template,
            "current_index": 1,
            "total_questions": len(question_records)
        }
    }

@router.post("/submit-answer")
def submit_answer(payload: AnswerSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == payload.interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    
    if interview.status == "Completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Interview already completed")

    question = db.query(Question).filter(Question.id == payload.question_id, Question.interview_id == interview.id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this interview")

    # Call AI evaluation
    eval_res = AIService.evaluate_answer(question.text, question.question_type, payload.candidate_answer)

    # Save Answer
    score = float(eval_res.get("overall_score", 0.0))
    new_answer = Answer(
        interview_id=interview.id,
        question_id=question.id,
        candidate_answer=payload.candidate_answer,
        score=score
    )
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    # Save Feedback
    new_feedback = Feedback(
        answer_id=new_answer.id,
        overall_score=score,
        communication_score=float(eval_res.get("communication_score", 0.0)),
        technical_score=float(eval_res.get("technical_score", 0.0)),
        problem_solving_score=float(eval_res.get("problem_solving_score", 0.0)),
        confidence_score=float(eval_res.get("confidence_score", 0.0)),
        grammar_feedback=eval_res.get("grammar_feedback"),
        fluency_feedback=eval_res.get("fluency_feedback"),
        suggestions=eval_res.get("suggestions"),
        weak_topics=json.dumps(eval_res.get("weak_topics", [])),
        strong_topics=json.dumps(eval_res.get("strong_topics", [])),
        correct_approach=eval_res.get("correct_approach"),
        better_answer=eval_res.get("better_answer")
    )
    db.add(new_feedback)
    db.commit()

    # Determine next question
    all_questions = db.query(Question).filter(Question.interview_id == interview.id).order_by(Question.id).all()
    answered_count = db.query(Answer).filter(Answer.interview_id == interview.id).count()

    next_q = None
    if answered_count < len(all_questions):
        next_q = all_questions[answered_count]
        next_q_data = {
            "id": next_q.id,
            "text": next_q.text,
            "question_type": next_q.question_type,
            "code_template": next_q.code_template,
            "current_index": answered_count + 1,
            "total_questions": len(all_questions)
        }
    else:
        next_q_data = None
        # Complete the interview and update statistics
        answers = db.query(Answer).filter(Answer.interview_id == interview.id).all()
        total_score = sum(ans.score for ans in answers)
        avg_score = total_score / len(answers) if answers else 0.0
        
        interview.total_score = round(avg_score, 1)
        interview.status = "Completed"
        db.commit()

        # Update Progress
        progress = db.query(Progress).filter(Progress.user_id == current_user.id).first()
        if progress:
            # Update average
            prev_total = progress.total_interviews
            progress.total_interviews += 1
            progress.average_score = ((progress.average_score * prev_total) + interview.total_score) / progress.total_interviews
            if interview.total_score > progress.best_score:
                progress.best_score = interview.total_score
            
            # Aggregate strong/weak topics
            try:
                current_weak = set(json.loads(progress.weak_topics or "[]"))
                current_strong = set(json.loads(progress.strong_topics or "[]"))
            except Exception:
                current_weak = set()
                current_strong = set()

            for w in eval_res.get("weak_topics", []):
                current_weak.add(w)
            for s in eval_res.get("strong_topics", []):
                current_strong.add(s)

            # Prevent duplication between strong and weak lists
            current_weak = current_weak - current_strong

            progress.weak_topics = json.dumps(list(current_weak)[:5])  # Cap at top 5
            progress.strong_topics = json.dumps(list(current_strong)[:5])
            
            # Update Streak
            days_diff = (datetime.utcnow().date() - progress.last_activity.date()).days
            if days_diff <= 1:
                if days_diff == 1:
                    progress.streak_count += 1
            else:
                progress.streak_count = 1
            progress.last_activity = datetime.utcnow()
            
            db.commit()

        # Update Leaderboard
        lead = db.query(Leaderboard).filter(Leaderboard.user_id == current_user.id).first()
        if lead:
            # Score formula: Total completed interviews count * 10 + Average Score * 5
            lead.score = (progress.total_interviews * 10.0) + (progress.average_score * 5.0)
            db.commit()
            
            # Recalculate Leaderboard Ranks
            all_leads = db.query(Leaderboard).order_by(Leaderboard.score.desc()).all()
            for rk, entry in enumerate(all_leads):
                entry.rank = rk + 1
            db.commit()

        # Achievements unlock system
        _unlock_achievements(current_user.id, progress, db)

    # Format feedback JSON lists back to arrays for API model serialization compatibility
    eval_res["weak_topics"] = eval_res.get("weak_topics", [])
    eval_res["strong_topics"] = eval_res.get("strong_topics", [])
    eval_res["id"] = new_feedback.id
    eval_res["answer_id"] = new_answer.id

    return {
        "feedback": eval_res,
        "next_question": next_q_data,
        "interview_completed": next_q_data is None,
        "interview_summary": {
            "total_score": interview.total_score if next_q_data is None else 0.0,
            "status": interview.status
        } if next_q_data is None else None
    }

def _unlock_achievements(user_id: int, progress: Progress, db: Session):
    existing_titles = [a.title for a in db.query(Achievement).filter(Achievement.user_id == user_id).all()]
    
    # 1. First Interview
    if progress.total_interviews >= 1 and "First Step" not in existing_titles:
        db.add(Achievement(
            user_id=user_id,
            title="First Step",
            description="Completed your first AI interview evaluation.",
            icon="award"
        ))
    
    # 2. Perfect Performance
    if progress.best_score >= 9.0 and "Star Candidate" not in existing_titles:
        db.add(Achievement(
            user_id=user_id,
            title="Star Candidate",
            description="Scored a 9.0+ score on an interview evaluation.",
            icon="star"
        ))
    
    # 3. Streak Champion
    if progress.streak_count >= 3 and "Consistent Scholar" not in existing_titles:
        db.add(Achievement(
            user_id=user_id,
            title="Consistent Scholar",
            description="Maintained a 3-day interview practice streak.",
            icon="zap"
        ))

    # 4. Pro Practitioner
    if progress.total_interviews >= 5 and "Interview Pro" not in existing_titles:
        db.add(Achievement(
            user_id=user_id,
            title="Interview Pro",
            description="Completed 5 full practice evaluations.",
            icon="shield"
        ))

    db.commit()

@router.get("/history", response_model=List[InterviewHistoryItem])
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).all()
    return interviews

@router.get("/achievements")
def get_achievements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    achievements = db.query(Achievement).filter(Achievement.user_id == current_user.id).all()
    return [{
        "title": a.title,
        "description": a.description,
        "icon": a.icon,
        "unlocked_at": a.unlocked_at
    } for a in achievements]

@router.get("/leaderboard", response_model=List[LeaderboardItem])
def get_leaderboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch top 10 candidates ordered by score desc
    entries = db.query(Leaderboard).order_by(Leaderboard.score.desc()).limit(10).all()
    return entries
