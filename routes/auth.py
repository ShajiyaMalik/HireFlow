import random
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import db, User
from services.email_service import EmailService

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store user details & OTP temporarily in session
        session['pending_signup'] = {
            'email': email,
            'password': password,
            'otp': otp
        }
        
        # --- Real Email Sending via EmailService ---
        try:
            EmailService.send_otp_email(email, otp)
            flash('Verification OTP has been sent to your email address.', 'success')
        except Exception as e:
            # Fallback agar email fail ho jaye, tab demo OTP dikha sakte hain debug ke liye
            flash(f'Error sending email. (Demo OTP for testing: {otp})', 'warning')
            
        return redirect(url_for('auth_bp.verify_otp'))
        
    return render_template('register.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_signup' not in session:
        flash('No pending registration found. Please sign up first.', 'warning')
        return redirect(url_for('auth_bp.register'))
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        pending_data = session.get('pending_signup')
        
        if entered_otp == pending_data.get('otp'):
            email = pending_data.get('email')
            raw_password = pending_data.get('password')
            
            # Hash password using bcrypt safely
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Check if user already exists in database (to update or avoid duplicates)
            user = User.query.filter_by(email=email).first()
            if user:
                # Agar user pehle se tha, toh uska password ya status update kar sakte hain
                user.password_hash = hashed_password
                user.is_verified = True
            else:
                # Naya user create karna
                user = User(
                    email=email,
                    password_hash=hashed_password,
                    is_verified=True  # OTP verify ho gaya toh verified mark kar diya
                )
                db.session.add(user)
                
            db.session.commit()
            
            # Clear pending session data
            session.pop('pending_signup', None)
            
            flash('Email verified successfully! Please log in with your credentials.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('verify_otp.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Check if user is verified
            if hasattr(user, 'is_verified') and not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('auth_bp.verify_otp'))
                
            session['user_id'] = user.id
            session['user_name'] = getattr(user, 'name', 'Recruiter')
            flash('Logged in successfully!', 'success')
            return redirect(url_for('recruiter_bp.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth_bp.login'))