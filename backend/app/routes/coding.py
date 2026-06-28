import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.database_models import User, Question, Interview, Answer, Feedback
from backend.app.schemas.api_schemas import CodeRunRequest, CodeRunResult, AnswerSubmit
from backend.app.auth.auth_service import get_current_user
from backend.app.services.code_runner import CodeRunner
from backend.app.services.ai_service import AIService
from backend.app.routes.candidate import submit_answer

router = APIRouter(prefix="/api/coding", tags=["Coding Sandbox & Evaluation"])

@router.post("/run-code", response_model=CodeRunResult)
def run_code(payload: CodeRunRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coding question not found")
    
    # Run the candidate code against the question's test cases
    test_cases_json = question.test_cases or "[]"
    run_result = CodeRunner.run_code(payload.code, test_cases_json, payload.language)
    return run_result

@router.post("/submit-code")
def submit_code(payload: CodeRunRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coding question not found")

    interview = db.query(Interview).filter(Interview.id == question.interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    if interview.status == "Completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Interview already completed")

    # 1. Run all test cases
    test_cases_json = question.test_cases or "[]"
    run_result = CodeRunner.run_code(payload.code, test_cases_json, payload.language)

    # Calculate functional score based on test cases passed
    tc_ratio = run_result.passed_count / run_result.total_count if run_result.total_count > 0 else 0.0
    functional_score = tc_ratio * 10.0

    # 2. Build answer text combining run results and source code for the AI
    answer_context = f"""
Candidate Source Code ({payload.language}):
```{payload.language}
{payload.code}
```

Execution Run Results:
- Success: {run_result.success}
- Error / Warnings: {run_result.stderr}
- Execution Time: {run_result.run_time} ms
- Test Cases Passed: {run_result.passed_count}/{run_result.total_count}
"""

    # 3. Process candidate submission using standard candidate evaluation route logic
    # We reuse submit_answer logic by passing a modified AnswerSubmit schema
    submit_payload = AnswerSubmit(
        interview_id=interview.id,
        question_id=payload.question_id,
        candidate_answer=answer_context
    )

    result = submit_answer(submit_payload, current_user, db)

    # Inject the runtime stats directly into response for frontend rendering
    result["code_run_result"] = {
        "success": run_result.success,
        "stdout": run_result.stdout,
        "stderr": run_result.stderr,
        "run_time": run_result.run_time,
        "memory_usage": run_result.memory_usage,
        "passed_count": run_result.passed_count,
        "total_count": run_result.total_count,
        "results": [r.__dict__ if hasattr(r, '__dict__') else r for r in run_result.results]
    }

    return result
