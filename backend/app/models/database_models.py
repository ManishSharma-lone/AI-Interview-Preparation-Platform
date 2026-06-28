from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    leaderboard_entry = relationship("Leaderboard", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_type = Column(String, nullable=False)  # e.g., Software Engineer, Python Developer, etc.
    difficulty = Column(String, nullable=False)  # Easy, Medium, Hard
    interview_type = Column(String, nullable=False)  # HR, Technical, Coding, Mixed
    num_questions = Column(Integer, default=5)
    total_score = Column(Float, default=0.0)
    status = Column(String, default="InProgress")  # InProgress, Completed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="interview", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # HR, Technical, Coding
    difficulty = Column(String, nullable=False)      # Easy, Medium, Hard
    code_template = Column(Text, nullable=True)     # For Coding interviews
    test_cases = Column(Text, nullable=True)        # JSON string containing sample/hidden test cases

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    candidate_answer = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    feedback = relationship("Feedback", back_populates="answer", uselist=False, cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False)
    overall_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    grammar_feedback = Column(Text, nullable=True)
    fluency_feedback = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    weak_topics = Column(Text, nullable=True)      # JSON string / comma-separated list
    strong_topics = Column(Text, nullable=True)    # JSON string / comma-separated list
    correct_approach = Column(Text, nullable=True) # For coding / technical questions
    better_answer = Column(Text, nullable=True)

    # Relationships
    answer = relationship("Answer", back_populates="feedback")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_interviews = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    best_score = Column(Float, default=0.0)
    weak_topics = Column(Text, default="[]")       # JSON list of weak topics
    strong_topics = Column(Text, default="[]")     # JSON list of strong topics
    streak_count = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, nullable=False)  # Badge name or icon identifier
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="achievements")


class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String, nullable=False)
    score = Column(Float, default=0.0)
    rank = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="leaderboard_entry")
