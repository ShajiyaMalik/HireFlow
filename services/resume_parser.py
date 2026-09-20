import os
import fitz  # PyMuPDF
import docx

class ResumeParser:
    @staticmethod
    def extract_text(file_path):
        """Extracts text from PDF or DOCX files."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return ResumeParser._extract_pdf(file_path)
        elif ext == '.docx':
            return ResumeParser._extract_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")

    @staticmethod
    def _extract_pdf(file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    @staticmethod
    def _extract_docx(file_path):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])