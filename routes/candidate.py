import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from models.user import db
from models.candidate import Candidate, CandidateMatch
from services.resume_parser import ResumeParser
from services.ai_service import AIService

candidate_bp = Blueprint('candidate_bp', __name__)

@candidate_bp.route('/upload/<int:job_id>', methods=['GET', 'POST'])
def upload_resume(job_id):
    if 'user_id' not in session:
        flash('Please log in to upload resumes.', 'warning')
        return redirect(url_for('auth_bp.login'))
        
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        name = request.form.get('name')
        email = request.form.get('email')
        
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # 1. Extract text from PDF/DOCX
                extracted_text = ResumeParser.extract_text(file_path)
                
                # 2. Run AI Analysis
                ai_profile = AIService.analyze_resume(extracted_text)
                
                # 3. Save candidate to database
                new_candidate = Candidate(
                    job_id=job_id,
                    name=name,
                    email=email,
                    resume_path=file_path,
                    extracted_data=json.dumps(ai_profile)
                )
                db.session.add(new_candidate)
                db.session.commit()
                
                flash('Resume uploaded, parsed, and analyzed successfully!', 'success')
                # Redirect straight to the candidate detail page
                return redirect(url_for('candidate_bp.candidate_detail', candidate_id=new_candidate.id))
            except Exception as e:
                flash(f'Error processing resume: {str(e)}', 'danger')
                return redirect(request.url)
                
    return render_template('candidate_upload.html', job_id=job_id)

@candidate_bp.route('/detail/<int:candidate_id>')
def candidate_detail(candidate_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
        
    candidate = Candidate.query.get_or_404(candidate_id)
    extracted_data = json.loads(candidate.extracted_data) if candidate.extracted_data else {}
    
    return render_template('candidate_detail.html', candidate=candidate, extracted_data=extracted_data)