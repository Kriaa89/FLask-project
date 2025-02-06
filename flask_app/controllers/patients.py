from flask import render_template, redirect, request, session, flash, jsonify
from flask_app import app
from flask_app.models.user import User
from flask_app.models.doctor import Doctor
from flask_app.models.appointment import Appointment
from flask_app.models.male import Male
from flask_app.models.female import Female
from datetime import datetime, timedelta

def patient_login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        if session.get('user_role') != 'patient':
            flash("Unauthorized access", "error")
            return redirect('/')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/patient/dashboard')
@patient_login_required
def patient_dashboard():
    patient = User.get_by_id({'id': session['user_id']})
    if not patient:
        return redirect('/logout')
    
    # Get medical record based on gender
    medical_record = None
    if patient.gender == 'M':
        medical_record = Male.get_by_patient_id({'patient_id': patient.id})
    else:
        medical_record = Female.get_by_patient_id({'patient_id': patient.id})
    
    # Get appointments
    appointments = Appointment.get_by_patient_id({'patient_id': patient.id})
    upcoming_count = sum(1 for a in appointments if a.date >= datetime.now().date() and a.status != 'cancelled')
    past_count = sum(1 for a in appointments if a.date < datetime.now().date() or a.status == 'cancelled')
    
    return render_template('patient/patient_dashboard.html',
                         patient=patient,
                         medical_record=medical_record,
                         appointments=appointments,
                         upcoming_count=upcoming_count,
                         past_count=past_count)

@app.route('/patient/search-doctors')
@patient_login_required
def search_doctors():
    patient = User.get_by_id({'id': session['user_id']})
    if not patient:
        return redirect('/logout')
    
    # Get all specialties and regions
    specialties = Doctor.get_all_specialties()
    regions = Doctor.get_all_regions()
    
    # Get doctors based on patient's region by default
    doctors = Doctor.get_by_region({'region': patient.region})
    
    return render_template('patient/search_doctors.html',
                         specialties=specialties,
                         regions=regions,
                         doctors=doctors)

@app.route('/patient/appointments')
@patient_login_required
def view_appointments():
    patient = User.get_by_id({'id': session['user_id']})
    if not patient:
        return redirect('/logout')
    
    # Get all appointments
    all_appointments = Appointment.get_by_patient_id({'patient_id': patient.id})
    
    # Separate into upcoming and past appointments
    now = datetime.now()
    upcoming_appointments = []
    past_appointments = []
    
    for appt in all_appointments:
        appt_datetime = datetime.combine(appt.date, appt.time)
        if appt_datetime >= now and appt.status != 'cancelled':
            upcoming_appointments.append(appt)
        else:
            past_appointments.append(appt)
    
    return render_template('patient/view_appointments.html',
                         upcoming_appointments=upcoming_appointments,
                         past_appointments=past_appointments)

@app.route('/patient/book-appointment/<int:doctor_id>', methods=['GET', 'POST'])
@patient_login_required
def book_appointment(doctor_id):
    patient = User.get_by_id({'id': session['user_id']})
    if not patient:
        return redirect('/logout')
    
    doctor = Doctor.get_by_id({'id': doctor_id})
    if not doctor:
        flash("Doctor not found", "error")
        return redirect('/patient/search-doctors')
    
    if request.method == 'GET':
        today = datetime.now().date()
        max_date = today + timedelta(days=30)  # Allow booking up to 30 days in advance
        
        return render_template('patient/book_appointment.html',
                             doctor=doctor,
                             today=today.strftime('%Y-%m-%d'),
                             max_date=max_date.strftime('%Y-%m-%d'))
    
    # Handle POST request
    if not request.form.get('date'):
        flash("Please select a date", "error")
        return redirect(request.url)
    
    if not request.form.get('location'):
        flash("Please select a location", "error")
        return redirect(request.url)
    
    # Create appointment
    data = {
        'patient_id': patient.id,
        'doctor_id': doctor_id,
        'date': request.form['date'],
        'location': request.form['location'],
        'symptoms': request.form.get('symptoms', ''),
        'status': 'pending'
    }
    
    appointment_id = Appointment.save(data)
    if not appointment_id:
        flash("Error booking appointment", "error")
        return redirect(request.url)
    
    flash("Appointment booked successfully!", "success")
    return redirect('/patient/appointments')

@app.route('/patient/medical-record')
@patient_login_required
def view_medical_record():
    patient = User.get_by_id({'id': session['user_id']})
    if not patient:
        return redirect('/logout')
    
    # Get medical record based on gender
    medical_record = None
    if patient.gender == 'M':
        medical_record = Male.get_by_patient_id({'patient_id': patient.id})
    else:
        medical_record = Female.get_by_patient_id({'patient_id': patient.id})
    
    return render_template('patient/medical_record.html',
                         patient=patient,
                         medical_record=medical_record)

@app.route('/patient/medical-record/update', methods=['GET', 'POST'])
@patient_login_required
def update_medical_record():
    patient = User.get_by_id({'id': session['user_id']})
    if not patient:
        return redirect('/logout')
    
    # Get existing medical record
    medical_record = None
    if patient.gender == 'M':
        medical_record = Male.get_by_patient_id({'patient_id': patient.id})
    else:
        medical_record = Female.get_by_patient_id({'patient_id': patient.id})
    
    if request.method == 'GET':
        return render_template('patient/update_medical_record.html',
                             patient=patient,
                             medical_record=medical_record)
    
    # Handle POST request
    data = {
        'patient_id': patient.id,
        'blood_type': request.form.get('blood_type'),
        'height': request.form.get('height'),
        'weight': request.form.get('weight'),
        'allergies': request.form.get('allergies'),
        'chronic_conditions': request.form.get('chronic_conditions'),
        'current_medications': request.form.get('current_medications'),
        'past_surgeries': request.form.get('past_surgeries'),
        'family_history': request.form.get('family_history'),
        'emergency_contact_name': request.form.get('emergency_contact_name'),
        'emergency_contact_phone': request.form.get('emergency_contact_phone'),
        'emergency_contact_relationship': request.form.get('emergency_contact_relationship'),
        'notes': request.form.get('notes')
    }
    
    # Add gender-specific fields
    if patient.gender == 'M':
        data.update({
            'prostate_exam': request.form.get('prostate_exam'),
            'psa_level': request.form.get('psa_level'),
            'testicular_exam': request.form.get('testicular_exam'),
            'cardiac_test': request.form.get('cardiac_test')
        })
        if medical_record:
            Male.update(data)
        else:
            Male.save(data)
    else:
        data.update({
            'last_menstrual': request.form.get('last_menstrual'),
            'mammogram_date': request.form.get('mammogram_date'),
            'pap_smear_date': request.form.get('pap_smear_date'),
            'pregnant': bool(request.form.get('pregnant')),
            'due_date': request.form.get('due_date') if request.form.get('pregnant') else None
        })
        if medical_record:
            Female.update(data)
        else:
            Female.save(data)
    
    flash('Medical record updated successfully!', 'success')
    return redirect('/patient/medical-record')

# API Routes
@app.route('/api/appointments/<int:appointment_id>')
@patient_login_required
def get_appointment(appointment_id):
    appointment = Appointment.get_by_id({'id': appointment_id})
    if not appointment or appointment.patient_id != session['user_id']:
        return jsonify({'error': 'Appointment not found'}), 404
    
    return jsonify(appointment.to_dict())

@app.route('/api/appointments/<int:appointment_id>/cancel', methods=['POST'])
@patient_login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.get_by_id({'id': appointment_id})
    if not appointment or appointment.patient_id != session['user_id']:
        return jsonify({'error': 'Appointment not found'}), 404
    
    if appointment.status == 'cancelled':
        return jsonify({'error': 'Appointment already cancelled'}), 400
    
    if Appointment.cancel({'id': appointment_id}):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to cancel appointment'}), 500

@app.route('/api/appointments/<int:appointment_id>/review', methods=['POST'])
@patient_login_required
def add_appointment_review(appointment_id):
    appointment = Appointment.get_by_id({'id': appointment_id})
    if not appointment or appointment.patient_id != session['user_id']:
        return jsonify({'error': 'Appointment not found'}), 404
    
    if appointment.status != 'completed':
        return jsonify({'error': 'Can only review completed appointments'}), 400
    
    data = request.json
    if not data or 'rating' not in data or 'review' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    review_data = {
        'appointment_id': appointment_id,
        'doctor_id': appointment.doctor_id,
        'patient_id': session['user_id'],
        'rating': data['rating'],
        'review': data['review']
    }
    
    if Appointment.add_review(review_data):
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to add review'}), 500

@app.route('/api/doctors/<int:doctor_id>')
@patient_login_required
def get_doctor_profile(doctor_id):
    doctor = Doctor.get_by_id({'id': doctor_id})
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    return jsonify(doctor.to_dict())
