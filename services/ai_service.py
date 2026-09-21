import os
from google import genai
from google.genai import types

class AIService:
    @staticmethod
    def get_client():
        # Initialize the GenAI client using environment variable
        api_key = os.getenv('AI_API_KEY') or os.getenv('GEMINI_API_KEY')
        return genai.Client(api_key=api_key)

    @staticmethod
    def analyze_resume(resume_text):
        """Sends extracted resume text to Gemini API for structured profile extraction."""
        try:
            client = AIService.get_client()
            prompt = f"""
            Analyze the following resume text and extract key details into a structured format containing:
            - skills (as a list)
            - experience (e.g., '1.5 Years')
            - projects (as a list)
            - education (string)
            
            Resume Text:
            {resume_text}
            
            Return the output strictly in valid JSON format with keys: skills, experience, projects, education.
            """
            
            response = client.models.generate_content(
                model='gemini-3.7-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini API Error (Analyze): {e}")
            # Fallback if API fails
            return {
                "skills": [],
                "experience": "Unknown",
                "projects": [],
                "education": "Unknown"
            }

    @staticmethod
    def match_candidate(job_description, candidate_profile):
        """Compares candidate profile against job requirements using Gemini."""
        try:
            client = AIService.get_client()
            prompt = f"""
            Compare this candidate profile against the job description.
            Job Description: {job_description}
            Candidate Profile: {candidate_profile}
            
            Return a JSON object with:
            - matches (list of matching skills/areas)
            - missing (list of missing skills/areas)
            - validation_areas (list of things to verify during interview)
            """
            response = client.models.generate_content(
                model='gemini-3.7-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini API Error (Match): {e}")
            return {"matches": [], "missing": [], "validation_areas": []}

    @staticmethod
    def generate_interview_questions(candidate_data, job_description):
        """Generates role-specific interview questions using Gemini."""
        try:
            client = AIService.get_client()
            prompt = f"""
            Generate 3 technical interview questions based on this candidate profile and job description.
            Candidate Data: {candidate_data}
            Job Description: {job_description}
            
            Return the output as a JSON array of strings (just the questions).
            """
            response = client.models.generate_content(
                model='gemini-3.7-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini API Error (Questions): {e}")
            return ["Can you walk us through your past projects?"]