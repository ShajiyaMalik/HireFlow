import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import db, User
from services.email_service import EmailService
import bcrypt

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 1. Check if user already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth_bp.login'))
            
        # 2. Hash password securely
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 3. Generate a 6-digit OTP code
        otp = random.randint(100000, 999999)
        
        # 4. Store user details and OTP temporarily in the session (DO NOT create DB record yet)
        session['pending_user'] = {
            'name': name,
            'email': email,
            'password_hash': hashed_password
        }
        session['otp'] = otp
        
        # 5. Send the OTP email
        EmailService.send_otp_email(email, otp)
        flash('Registration initiated! Please check your email for the verification OTP.', 'info')
        return redirect(url_for('auth_bp.verify_otp'))
        
    return render_template('register.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'pending_user' not in session:
        flash('No pending registration found. Please sign up first.', 'warning')
        return redirect(url_for('auth_bp.register'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        
        if 'otp' in session and str(session['otp']) == user_otp:
            pending_data = session['pending_user']
            
            # Now create the user in the database since OTP is correct
            new_user = User(
                name=pending_data['name'],
                email=pending_data['email'],
                password_hash=pending_data['password_hash'],
                is_verified=True
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Clear temporary session data
            session.pop('otp', None)
            session.pop('pending_user', None)
            
            flash('Email verified and account created successfully! You can now log in.', 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')
            
    return render_template('verify_otp.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('auth_bp.login'))
                
            session['user_id'] = user.id
            session['user_name'] = user.name
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