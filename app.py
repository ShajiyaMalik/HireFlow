import os
from flask import Flask, render_template
from config import Config
from models.user import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    
    with app.app_context():
        # 1. IMPORT ALL MODELS EXPLICITLY FIRST
        import models.user
        import models.job
        import models.candidate
        import models.interview
        import models.evaluation
        
        # 2. CREATE ALL TABLES
        db.create_all()
        
    # 3. IMPORT AND REGISTER BLUEPRINTS AFTER
    from routes.auth import auth_bp
    from routes.recruiter import recruiter_bp
    from routes.candidate import candidate_bp
    from routes.interview import interview_bp
    from routes.ai import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    app.register_blueprint(candidate_bp, url_prefix='/candidate')
    app.register_blueprint(interview_bp, url_prefix='/interview')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    
    @app.route('/')
    def index():
        return render_template('index.html')
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)