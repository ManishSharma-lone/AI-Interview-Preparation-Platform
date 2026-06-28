from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field

# --- Auth Schemas ---
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


# --- Interview Schemas ---
class InterviewStart(BaseModel):
    role_type: str
    difficulty: str  # Easy, Medium, Hard
    interview_type: str  # HR, Technical, Coding, Mixed
    num_questions: int = Field(5, ge=1, le=20)

class InterviewResponse(BaseModel):
    id: int
    role_type: str
    difficulty: str
    interview_type: str
    num_questions: int
    total_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    interview_id: int
    text: str
    question_type: str
    difficulty: str
    code_template: Optional[str] = None
    test_cases: Optional[str] = None # JSON string representing sample/hidden test cases for coding questions
    current_index: int
    total_questions: int

    class Config:
        from_attributes = True


# --- Answer & Feedback Schemas ---
class AnswerSubmit(BaseModel):
    interview_id: int
    question_id: int
    candidate_answer: str

class FeedbackResponse(BaseModel):
    id: int
    answer_id: int
    overall_score: float
    communication_score: float
    technical_score: float
    problem_solving_score: float
    confidence_score: float
    grammar_feedback: Optional[str] = None
    fluency_feedback: Optional[str] = None
    suggestions: Optional[str] = None
    weak_topics: List[str] = []
    strong_topics: List[str] = []
    correct_approach: Optional[str] = None
    better_answer: Optional[str] = None

    class Config:
        from_attributes = True


# --- Code Runner Schemas ---
class CodeRunRequest(BaseModel):
    question_id: int
    code: str
    language: Optional[str] = "python"

class TestCaseResult(BaseModel):
    name: str
    passed: bool
    input: str
    expected: str
    actual: str
    error: Optional[str] = None

class CodeRunResult(BaseModel):
    success: bool
    stdout: str
    stderr: str
    run_time: float
    memory_usage: float
    passed_count: int
    total_count: int
    results: List[TestCaseResult]


# --- Voice Schemas ---
class VoiceFeedbackRequest(BaseModel):
    interview_id: int
    question_id: int
    transcript: str


# --- Dashboard & Progress Schemas ---
class DashboardMetrics(BaseModel):
    total_interviews: int
    average_score: float
    best_score: float
    weak_topics: List[str]
    strong_topics: List[str]
    streak_count: int
    today_progress: int  # Number of interviews completed today

class InterviewHistoryItem(BaseModel):
    id: int
    role_type: str
    difficulty: str
    interview_type: str
    total_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class LeaderboardItem(BaseModel):
    username: str
    score: float
    rank: int

    class Config:
        from_attributes = True
