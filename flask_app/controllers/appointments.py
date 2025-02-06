from flask import render_template, request, redirect, session, flash
from flask_app import app, bcrypt
from flask_app.models.appointment import Appointment
from flask_app.models.user import User
from flask_app.models.doctor import Doctor
from datetime import datetime

@app.route('/appointments/book', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect('/login')
        
    if session['user_role'] != 'patient':
        flash("Only patients can book appointments", "error")
        return redirect('/dashboard')
        
    if request.method == 'POST':
        # Validate appointment data
        if not Appointment.validate_appointment(request.form):
            return redirect('/appointments/book')
            
        data = {
            'patient_id': session['user_id'],
            'doctor_id': request.form['doctor_id'],
            'appointment_date': request.form['appointment_date'],
            'appointment_time': request.form['appointment_time'],
            'reason': request.form['reason'],
            'notes': request.form.get('notes', ''),
            'status': 'pending'
        }
        
        appointment_id = Appointment.save(data)
        flash("Appointment request sent successfully!", "success")
        return redirect('/dashboard')
        
    # Get list of doctors for the form
    doctors = Doctor.get_all()
    return render_template('appointments/book.html', doctors=doctors)

@app.route('/appointments')
def view_appointments():
    if 'user_id' not in session:
        return redirect('/login')
        
    user_id = session['user_id']
    user_role = session['user_role']
    
    if user_role == 'patient':
        appointments = Appointment.get_patient_appointments(user_id)
    elif user_role == 'doctor':
        appointments = Appointment.get_doctor_appointments(user_id)
    else:
        appointments = []
        
    return render_template('appointments/list.html', 
                        appointments=appointments, 
                        user_role=user_role)

@app.route('/appointments/<int:id>')
def view_appointment(id):
    if 'user_id' not in session:
        return redirect('/login')
        
    appointment = Appointment.get_one(id)
    
    if not appointment:
        flash("Appointment not found", "error")
        return redirect('/appointments')
        
    # Check if user has permission to view this appointment
    if (session['user_role'] == 'patient' and appointment.patient_id != session['user_id']) or \
        (session['user_role'] == 'doctor' and appointment.doctor_id != session['user_id']):
        flash("You don't have permission to view this appointment", "error")
        return redirect('/appointments')
        
    return render_template('appointments/view.html', appointment=appointment)

@app.route('/appointments/<int:id>/update', methods=['POST'])
def update_appointment_status(id):
    if 'user_id' not in session or session['user_role'] != 'doctor':
        return redirect('/login')
        
    appointment = Appointment.get_one(id)
    
    if not appointment or appointment.doctor_id != session['user_id']:
        flash("Invalid appointment", "error")
        return redirect('/appointments')
        
    status = request.form.get('status')
    if status not in ['approved', 'rejected', 'completed']:
        flash("Invalid status", "error")
        return redirect(f'/appointments/{id}')
        
    Appointment.update_status(id, status)
    flash("Appointment status updated successfully!", "success")
    return redirect(f'/appointments/{id}')
