import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key')
    
    # TiDB Connection URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Engine options including connect_args for TiDB SSL certificate verification
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "ssl": {
                "ca": r"isrgrootx1.pem" # Path to your downloaded TiDB CA certificate file
            }
        }
    }
    
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads'))
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}