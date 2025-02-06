from flask import render_template, redirect, session, request, flash
from flask_app import app
from flask_app.models.doctor import Doctor
from flask_app.models.user import User
from datetime import datetime

@app.route('/doctor/verify')
def doctor_verify():
    if 'user_id' not in session or session.get('user_role') != 'doctor':
        return redirect('/login')
    
    # Check if doctor profile exists
    doctor = Doctor.get_by_user_id(session['user_id'])
    if not doctor:
        # First time doctor, redirect to complete profile
        return redirect('/doctor/complete-profile')
    
    # If profile exists but pending verification
    if doctor.verification_status == 'pending':
        flash("Your profile is pending verification. An administrator will review your information shortly.", "info")
        return redirect('/doctor/dashboard')
    
    # If profile is rejected
    if doctor.verification_status == 'rejected':
        flash("Your verification was rejected. Please update your information and try again.", "warning")
        return redirect('/doctor/complete-profile')
    
    # If already verified
    return redirect('/doctor/dashboard')

@app.route('/doctor/complete-profile', methods=['GET', 'POST'])
def complete_doctor_profile():
    if 'user_id' not in session or session.get('user_role') != 'doctor':
        return redirect('/login')
    
    if request.method == 'GET':
        doctor = Doctor.get_by_user_id(session['user_id'])
        return render_template('doctor/complete_profile.html', doctor=doctor)
    
    # Validate form data
    if not Doctor.validate_profile(request.form):
        return redirect('/doctor/complete-profile')
    
    # Prepare data for update/insert
    data = {
        'user_id': session['user_id'],
        'specialty': request.form['specialty'],
        'license_number': request.form['license_number'],
        'education': request.form['education'],
        'experience_years': int(request.form['experience_years']),
        'bio': request.form['bio'],
        'consultation_fee': float(request.form['consultation_fee']),
        'languages_spoken': request.form['languages_spoken']
    }
    
    # Check if doctor profile exists
    doctor = Doctor.get_by_user_id(session['user_id'])
    if doctor:
        # Update existing profile
        data['doctor_id'] = doctor.id
        Doctor.update_profile(data)
        flash("Your profile has been updated and will be reviewed by an administrator.", "success")
    else:
        # Create new profile
        Doctor.save(data)
        flash("Your profile has been submitted for verification.", "success")
    
    # Set session variables
    session['doctor_profile_complete'] = True
    
    return redirect('/doctor/dashboard')

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'doctor':
        return redirect('/login')
    
    doctor = Doctor.get_by_user_id(session['user_id'])
    if not doctor:
        return redirect('/doctor/complete-profile')
    
    # Store verification status in session
    session['doctor_verification_status'] = doctor.verification_status
    
    # If not verified, show appropriate message
    if doctor.verification_status != 'approved':
        if doctor.verification_status == 'pending':
            flash("Your account is pending verification. An administrator will review your information shortly.", "info")
        elif doctor.verification_status == 'rejected':
            flash("Your verification was rejected. Please update your information and try again.", "warning")
            return redirect('/doctor/complete-profile')
    
    return render_template('doctor/dashboard.html', doctor=doctor)
