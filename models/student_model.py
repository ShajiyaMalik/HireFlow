from datetime import datetime
from models.user import db  # Aapke project ke mutabiq db yahi se import hoga

class StudentResumeAnalysis(db.Model):
    __tablename__ = 'student_resume_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    target_job_role = db.Column(db.String(150), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=True)
    matching_skills = db.Column(db.JSON, nullable=True)
    missing_skills = db.Column(db.JSON, nullable=True)
    improvement_feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StudentResumeAnalysis {self.student_name} - {self.target_job_role}>"