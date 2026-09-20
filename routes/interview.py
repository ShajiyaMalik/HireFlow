from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import db
from models.interview import Interview
from models.evaluation import Evaluation
from models.candidate import Candidate
from services.ai_service import AIService

interview_bp = Blueprint('interview_bp', __name__)

@interview_bp.route('/session/<int:candidate_id>', methods=['GET', 'POST'])
def interview_session(candidate_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
        
    candidate = Candidate.query.get_or_404(candidate_id)
    
    if request.method == 'POST':
        notes = request.form.get('notes')
        
        # Save interview notes
        new_interview = Interview(
            candidate_id=candidate.id,
            job_id=candidate.job_id,
            notes=notes
        )
        db.session.add(new_interview)
        db.session.commit()
        
        flash('Interview notes saved successfully!', 'success')
        return redirect(url_for('recruiter_bp.dashboard'))
        
    return render_template('interview.html', candidate=candidate)