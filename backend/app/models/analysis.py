from datetime import datetime
from uuid import uuid4
from ..extensions import db

class Analysis(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    resume_filename = db.Column(db.String(255), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    jd_text = db.Column(db.Text, nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    scores_json = db.Column(db.JSON, nullable=False)
    skills_json = db.Column(db.JSON, nullable=False)
    sections_json = db.Column(db.JSON, nullable=False)
    quality_json = db.Column(db.JSON, nullable=False)
    ats_json = db.Column(db.JSON, nullable=False)
    suggestions_json = db.Column(db.JSON, nullable=False)
    parent_analysis_id = db.Column(db.String(36), db.ForeignKey('analysis.id'), nullable=True)
    label = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_summary(self):
        return {
            "id": self.id,
            "resume_filename": self.resume_filename,
            "overall_score": self.overall_score,
            "scores": self.scores_json,
            "created_at": self.created_at.isoformat(),
            "parent_analysis_id": self.parent_analysis_id,
            "label": self.label
        }
    
    def to_full(self):
        return {
            "analysis_id": self.id,
            "timestamp": self.created_at.isoformat(),
            "resume_filename": self.resume_filename,
            "scores": self.scores_json,
            "skills": self.skills_json,
            "sections": self.sections_json,
            "quality": self.quality_json,
            "ats": self.ats_json,
            "suggestions": self.suggestions_json,
            "parent_analysis_id": self.parent_analysis_id,
            "label": self.label
        }
