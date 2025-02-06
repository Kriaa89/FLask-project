from flask import render_template, redirect, session, request, flash
from flask_app import app
from flask_app.models.admin import Admin
from flask_app.models.doctor import Doctor
from datetime import datetime

@app.route('/admin/doctor-verifications')
def admin_doctor_verifications():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect('/login')
    
    # Get all pending doctor verifications
    pending_doctors = Doctor.get_pending_verifications()
    
    return render_template('admin/doctor_verifications.html', pending_doctors=pending_doctors)

@app.route('/admin/update-doctor-verification', methods=['POST'])
def update_doctor_verification():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect('/login')
    
    if not request.form.get('doctor_id') or not request.form.get('status') or not request.form.get('notes'):
        flash("All fields are required", "error")
        return redirect('/admin/doctor-verifications')
    
    data = {
        'doctor_id': request.form['doctor_id'],
        'status': request.form['status'],
        'notes': request.form['notes'],
        'admin_id': session['user_id']
    }
    
    Doctor.update_verification_status(data)
    
    status_message = "approved" if data['status'] == 'approved' else "rejected"
    flash(f"Doctor verification has been {status_message}", "success")
    
    return redirect('/admin/doctor-verifications')
