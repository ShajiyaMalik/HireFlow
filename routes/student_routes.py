import os
from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename
from pypdf import PdfReader
from docx import Document

student_bp = Blueprint('student_bp', __name__, url_prefix='/student')

def extract_text_from_file(file_path, filename):
    text = ""
    if filename.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif filename.endswith('.docx'):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

@student_bp.route('/analyzer', methods=['GET', 'POST'])
def resume_analyzer():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        target_role = request.form.get('target_role')
        file = request.files.get('resume_file')
        
        extracted_text = ""
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Extract text based on file format
            extracted_text = extract_text_from_file(file_path, filename)
            
        # Dummy AI Analysis (Aap yahan apna Gemini API logic connect kar sakte hain jo extracted_text ko analyze karega)
        result = {
            "score": 82,
            "matching": ["Python", "Problem Solving", "Git"],
            "missing": ["Docker", "Kubernetes", "System Design"],
            "feedback": f"Analyzed uploaded document successfully! For a {target_role} role, your background looks solid, but you should incorporate containerization tools like Docker and system design principles into your portfolio."
        }
        
        return render_template('student_result.html', result=result, role=target_role, name=student_name)
        
    return render_template('student_analyzer.html')