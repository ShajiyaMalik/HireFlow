from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import db
from models.job import Job
from models.candidate import Candidate

recruiter_bp = Blueprint('recruiter_bp', __name__)

@recruiter_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('auth_bp.login'))
        
    recruiter_id = session['user_id']
    jobs = Job.query.filter_by(recruiter_id=recruiter_id).all()
    return render_template('dashboard.html', jobs=jobs)

@recruiter_bp.route('/job/create', methods=['GET', 'POST'])
def create_job():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        new_job = Job(
            recruiter_id=session['user_id'],
            title=title,
            description=description
        )
        db.session.add(new_job)
        db.session.commit()
        
        flash('Job posting created successfully!', 'success')
        return redirect(url_for('recruiter_bp.dashboard'))
        
    return render_template('job.html')