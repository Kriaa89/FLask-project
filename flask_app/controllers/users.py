from flask import render_template, redirect, request, session, flash
from flask_app import app, bcrypt
from flask_app.models.user import User
from flask_app.models.doctor import Doctor
import secrets
from datetime import datetime, timedelta

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    if not User.validate_registration(request.form):
        return redirect('/register')
    
    # Hash password
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    
    # Create user data with all required fields
    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': pw_hash,
        'role': request.form['role'],
        'gender': request.form['gender'],
        'phone_number': request.form['phone'],  # Note: form field is 'phone'
        'profile_picture': request.form.get('profile_picture', None),  # Optional
        'address': request.form.get('address', None),  # Optional
        'date_of_birth': request.form.get('date_of_birth', None)  # Optional
    }
    
    # Insert the user and get the ID
    user_id = User.save(data)
    
    if not user_id:
        flash("Error creating user account", "error")
        return redirect('/register')
    
    # Set session data
    session['user_id'] = user_id
    session['user_role'] = request.form['role']
    session['user_name'] = f"{request.form['first_name']} {request.form['last_name']}"
    
    if request.form['role'] == 'doctor':
        return redirect('/doctor/verify')
    return redirect('/patient/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    if not request.form.get('email') or not request.form.get('password'):
        flash("Both email and password are required", "error")
        return redirect('/login')
    
    user = User.get_by_email({'email': request.form.get('email')})
    if not user:
        flash("Invalid email or password", "error")
        return redirect('/login')
    
    if not bcrypt.check_password_hash(user.password, request.form.get('password')):
        flash("Invalid email or password", "error")
        return redirect('/login')
    
    session['user_id'] = user.id
    session['user_role'] = user.role
    session['user_name'] = f"{user.first_name} {user.last_name}"
    
    if user.role == 'doctor':
        return redirect('/doctor/dashboard')
    return redirect('/patient/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/doctor/verify', methods=['GET', 'POST'])
def verify_doctor():
    if 'user_id' not in session:
        return redirect('/login')
    
    if session.get('user_role') != 'doctor':
        flash("Unauthorized access", "error")
        return redirect('/')
    
    if request.method == 'GET':
        return render_template('auth/doctor_verify.html')
    
    # Verify that the user exists in the database
    user = User.get_by_id({'id': session['user_id']})
    if not user:
        flash("User not found. Please login again.", "error")
        return redirect('/logout')
    
    if not Doctor.validate_profile(request.form):
        return redirect('/doctor/verify')
    
    data = {
        'user_id': session['user_id'],
        'specialty': request.form['specialty'],
        'license_number': request.form['license_number'],
        'education': request.form['education'],
        'experience_years': request.form['experience_years'],
        'consultation_fee': request.form['consultation_fee'],
        'languages_spoken': request.form['languages_spoken'],
        'bio': request.form.get('bio', '')
    }
    
    doctor_id = Doctor.save(data)
    if doctor_id:
        flash("Profile verification submitted successfully", "success")
        return redirect('/doctor/dashboard')
    
    flash("Something went wrong", "error")
    return redirect('/doctor/verify')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('auth/forgot_password.html')
    
    email = request.form.get('email')
    if not User.validate_password_reset_request(email):
        return redirect('/forgot-password')
    
    user = User.get_by_email({'email': email})
    if not user:
        flash("If an account exists with this email, you will receive a password reset link", "info")
        return redirect('/forgot-password')
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expiration = datetime.now() + timedelta(hours=24)
    
    # Save reset token to database
    User.save_reset_token({
        'email': email,
        'reset_token': reset_token,
        'reset_token_expires': expiration
    })
    
    # Send reset email
    reset_url = request.host_url + f"reset-password/{reset_token}"
    # TODO: Implement email sending functionality
    flash("If an account exists with this email, you will receive a password reset link", "info")
    return redirect('/forgot-password')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        user = User.get_by_reset_token({'reset_token': token})
        if not user:
            flash("Invalid or expired password reset link", "danger")
            return redirect('/login')
        return render_template('auth/reset_password.html', token=token)
    
    if not User.validate_password_reset(request.form):
        return redirect(f'/reset-password/{token}')
    
    user = User.get_by_reset_token({'reset_token': token})
    if not user:
        flash("Invalid or expired password reset link", "danger")
        return redirect('/login')
    
    # Hash new password and update user
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    User.update_password({
        'id': user.id,
        'password': pw_hash
    })
    
    flash("Password has been reset successfully. Please login with your new password.", "success")
    return redirect('/login')
