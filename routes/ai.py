from flask import Blueprint, jsonify, request, session
from models.candidate import Candidate
from models.job import Job
from services.ai_service import AIService
import json

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/match/<int:candidate_id>', methods=['GET'])
def analyze_candidate_match(candidate_id):
    """API endpoint to fetch AI requirement matching and interview questions for a candidate."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    candidate = Candidate.query.get_or_404(candidate_id)
    job = Job.query.get_or_404(candidate.job_id)
    
    try:
        # Run AI matching and question generation
        candidate_profile = json.loads(candidate.extracted_data) if candidate.extracted_data else {}
        match_result = AIService.match_candidate(job.description, candidate_profile)
        questions = AIService.generate_interview_questions(candidate_profile, job.description)
        
        return jsonify({
            'success': True,
            'match_data': match_result,
            'questions': questions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500