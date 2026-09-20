from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import db
from models.interview import Interview
from models.evaluation import Evaluation
from models.candidate import Candidate
from services.ai_service import AIService
from google.genai import types
import json

interview_bp = Blueprint('interview_bp', __name__)

@interview_bp.route('/session/<int:candidate_id>', methods=['GET', 'POST'])
def interview_session(candidate_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
        
    candidate = Candidate.query.get_or_404(candidate_id)
    
    if request.method == 'POST':
        notes = request.form.get('notes')
        
        # 1. Save interview notes
        new_interview = Interview(
            candidate_id=candidate.id,
            job_id=candidate.job_id,
            notes=notes
        )
        db.session.add(new_interview)
        db.session.commit()
        
        # 2. Call Gemini AI to evaluate the interview notes
        try:
            client = AIService.get_client()
            prompt = f"""
            Evaluate the following interview notes for a candidate and provide:
            - A score out of 100 (integer)
            - Detailed feedback and a clear hiring recommendation (whether to Hire or Not Hire and why).
            
            Interview Notes:
            {notes}
            
            Return strictly in valid JSON format with keys: "score" (integer) and "feedback" (string).
            """
            
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            eval_data = json.loads(response.text)
            score = eval_data.get('score', 70)
            feedback = eval_data.get('feedback', 'Notes saved successfully.')
        except Exception as e:
            print(f"Gemini Evaluation Error: {e}")
            score = 50
            feedback = "Notes saved, but AI evaluation could not be processed automatically."

        # 3. Save evaluation result to Evaluation table
        new_evaluation = Evaluation(
            interview_id=new_interview.id,
            score=score,
            feedback=feedback
        )
        db.session.add(new_evaluation)
        db.session.commit()
        
        flash('Interview notes saved and evaluated successfully!', 'success')
        return redirect(url_for('candidate_bp.candidate_detail', candidate_id=candidate_id))
        
    return render_template('interview.html', candidate=candidate)