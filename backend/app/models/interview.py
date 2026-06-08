from datetime import datetime
from uuid import uuid4
from ..extensions import db

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analysis.id'), nullable=False)
    target_role = db.Column(db.String(255), nullable=True)
    difficulty = db.Column(db.String(20), default='medium')  # easy/medium/hard
    status = db.Column(db.String(20), default='in_progress')  # in_progress/completed/abandoned
    total_questions = db.Column(db.Integer, nullable=False)
    questions_json = db.Column(db.JSON, nullable=False)       # List of generated questions dicts
    overall_score = db.Column(db.Float, nullable=True)
    results_json = db.Column(db.JSON, nullable=True)          # Overall feedback, strengths, weaknesses, etc.
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    answers = db.relationship('InterviewAnswer', backref='session', lazy=True, cascade="all, delete-orphan")

    def to_summary(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "target_role": self.target_role,
            "difficulty": self.difficulty,
            "status": self.status,
            "total_questions": self.total_questions,
            "overall_score": self.overall_score,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class InterviewAnswer(db.Model):
    __tablename__ = 'interview_answers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('interview_sessions.id'), nullable=False)
    question_index = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)        # skill, behavioral, role
    skill = db.Column(db.String(100), nullable=True)           # Python, SQL, etc.
    user_answer = db.Column(db.Text, nullable=False)
    ideal_answer = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=True)                 # 0-10 final normalized score
    tfidf_score = db.Column(db.Float, nullable=True)
    keyword_score = db.Column(db.Float, nullable=True)
    gemini_score = db.Column(db.Float, nullable=True)
    feedback_json = db.Column(db.JSON, nullable=True)          # details (strengths, weaknesses, etc.)
    time_taken_seconds = db.Column(db.Integer, nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question_index": self.question_index,
            "question_text": self.question_text,
            "category": self.category,
            "skill": self.skill,
            "user_answer": self.user_answer,
            "ideal_answer": self.ideal_answer,
            "score": self.score,
            "tfidf_score": self.tfidf_score,
            "keyword_score": self.keyword_score,
            "gemini_score": self.gemini_score,
            "feedback": self.feedback_json,
            "time_taken_seconds": self.time_taken_seconds,
            "answered_at": self.answered_at.isoformat()
        }
