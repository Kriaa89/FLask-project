from flask import render_template, redirect, session, request, flash, jsonify, url_for
from flask_app import app, bcrypt
from flask_app.models.user import User
from flask_app.models.patient import Patient
from flask_app.models.doctor import Doctor
from flask_app.models.appointment import Appointment
from flask_app.models.prescription import Prescription
from datetime import datetime


@app.route('/')
def home():
    if 'user_id' in session:
        if session['user_role'] == 'doctor':
            return redirect('/doctor/dashboard')
        return redirect('/patient/dashboard')
    return render_template('index.html')

@app.route('/about')
def about():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('core/about_contact_home.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'user_id' in session:
        return redirect('/dashboard')
        
    if request.method == 'POST':
        # Handle contact form submission here
        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect('/contact')
    return render_template('core/about_contact_home.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    if session.get('user_role') == 'doctor':
        return redirect('/doctor/dashboard')
    elif session.get('user_role') == 'patient':
        return redirect('/patient/dashboard')
    elif session.get('user_role') == 'nurse':
        return redirect('/nurse/dashboard')
    
    return redirect('/')

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session['user_role'] != 'doctor':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    doctor = Doctor.get_by_user_id(session['user_id'])
    
    if not doctor:
        flash("Please complete your doctor profile first", "warning")
        return redirect('/doctor/verify')
    
    # Get doctor's appointments
    today_appointments = Appointment.get_doctor_appointments(doctor.id)
    upcoming_appointments = Appointment.get_doctor_upcoming_appointments(doctor.id)
    
    return render_template('doctor/dashboard.html',
                         user=user,
                         doctor=doctor,
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments)

@app.route('/patient/dashboard')
def patient_dashboard():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    patient = Patient.get_by_user_id(session['user_id'])
    
    # Get upcoming appointments
    upcoming_appointments = []
    if patient:
        upcoming_appointments = Appointment.get_patient_appointments(patient.id)
    
    # Get active prescriptions
    active_prescriptions = []
    if patient:
        active_prescriptions = Prescription.get_active_prescriptions(patient.id)
    
    # Get emergency contacts
    emergency_contacts = []
    if patient:
        emergency_contacts = patient.get_emergency_contacts()
    
    return render_template('patient/patient_dashboard.html',
                         user=user,
                         patient=patient,
                         upcoming_appointments=upcoming_appointments,
                         active_prescriptions=active_prescriptions,
                         emergency_contacts=emergency_contacts)

@app.route('/complete_patient_profile', methods=['POST'])
def complete_patient_profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Validate form data
    data = {
        'user_id': session['user_id'],
        'blood_type': request.form.get('blood_type'),
        'patient_emergency_contact_name': request.form.get('patient_emergency_contact_name'),
        'emergency_contact_phone': request.form.get('emergency_contact_phone'),
        'allergies': request.form.get('allergies'),
        'chronic_conditions': request.form.get('chronic_conditions'),
        'current_medications': request.form.get('current_medications'),
        'medical_history': request.form.get('medical_history')
    }

    # Here you can add validation logic for the data if needed

    # Save the patient profile
    Patient.save(data)
    flash('Patient profile completed successfully!', 'success')
    return redirect('/dashboard')

@app.route('/complete_patient_profile_form', methods=['POST'])
def complete_patient_profile_form():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Validate form data
    data = {
        'user_id': session['user_id'],
        'blood_type': request.form.get('blood_type'),
        'patient_emergency_contact_name': request.form.get('patient_emergency_contact_name'),
        'emergency_contact_phone': request.form.get('emergency_contact_phone'),
        'allergies': request.form.get('allergies'),
        'chronic_conditions': request.form.get('chronic_conditions'),
        'current_medications': request.form.get('current_medications'),
        'medical_history': request.form.get('medical_history')
    }

    # Here you can add validation logic for the data if needed

    # Save the patient profile
    Patient.save(data)
    flash('Patient profile completed successfully!', 'success')
    return redirect('/dashboard')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    if not user:
        return redirect('/logout')
    
    if session.get('user_role') == 'doctor':
        profile_data = Doctor.get_by_user_id(session['user_id'])
        return render_template('doctor/profile.html', user=user, doctor=profile_data)
    elif session.get('user_role') == 'patient':
        profile_data = Patient.get_by_user_id(session['user_id'])
        return render_template('patient/profile.html', user=user, patient=profile_data)
    
    return redirect('/')

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    if not user:
        return redirect('/logout')
    
    return render_template('settings.html', user=user)

@app.route('/check_password_strength', methods=['POST'])
def check_password_strength():
    password = request.json.get('password', '')
    strength = User.validate_password(password)
    class_name = 'text-danger' if strength == 'Weak' else 'text-warning' if strength == 'Moderate' else 'text-success'
    return jsonify({'strength': strength, 'class': class_name})

@app.route('/find-doctors')
def find_doctors():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    doctors = Doctor.get_all_verified()
    specialties = Doctor.get_all_specialties()
    
    return render_template('find_doctors.html',
                         user=user,
                         doctors=doctors,
                         specialties=specialties)

@app.route('/api/find-doctors/search')
def find_doctors_search():
    specialty = request.args.get('specialty')
    name = request.args.get('name')
    
    doctors = Doctor.search(specialty=specialty, name=name)
    return jsonify([{
        'id': doc.id,
        'name': doc.name,
        'specialty': doc.specialty,
        'experience_years': doc.experience_years,
        'consultation_fee': doc.consultation_fee,
        'languages': doc.languages_spoken
    } for doc in doctors])

@app.route('/complete_doctor_profile', methods=['GET', 'POST'])
def complete_doctor_profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    doctor = Doctor.get_by_user_id(session['user_id'])
    if request.method == 'POST':
        # Collect data from the form
        data = {
            'id': doctor.id,
            'user_id': session['user_id'],
            'specialty': request.form.get('specialty'),
            'license_number': request.form.get('license_number'),
            'education': request.form.get('education'),
            'experience_years': request.form.get('experience_years'),
            'bio': request.form.get('bio'),
            'consultation_fee': request.form.get('consultation_fee'),
            'languages_spoken': request.form.get('languages_spoken')
        }
        # Update the doctor's profile
        Doctor.update(data)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('doctor/complete_profile.html', doctor=doctor)

@app.route('/prescriptions')
def prescriptions():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    patient = Patient.get_by_user_id(session['user_id'])
    
    if not user or not patient:
        return redirect('/dashboard')
    
    prescriptions = Prescription.get_all_by_patient_id(patient.id)
    return render_template('patient/prescriptions.html', 
                         user=user,
                         patient=patient,
                         prescriptions=prescriptions)

@app.route('/prescriptions/<int:prescription_id>')
def view_prescription(prescription_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    patient = Patient.get_by_user_id(session['user_id'])
    
    if not user or not patient:
        return redirect('/dashboard')
    
    prescription = Prescription.get_by_id(prescription_id)
    
    if not prescription or prescription.patient_id != patient.id:
        flash('Prescription not found or access denied.', 'error')
        return redirect('/prescriptions')
    
    return render_template('patient/view_prescription.html',
                         user=user,
                         patient=patient,
                         prescription=prescription)

@app.route('/emergency_contacts')
def emergency_contacts():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    patient = Patient.get_by_user_id(session['user_id'])
    
    if not user or not patient:
        return redirect('/dashboard')
    
    return render_template('patient/emergency_contacts.html',
                         user=user,
                         patient=patient)

@app.route('/update_emergency_contact', methods=['POST'])
def update_emergency_contact():
    if 'user_id' not in session:
        return redirect('/login')
    
    patient = Patient.get_by_user_id(session['user_id'])
    if not patient:
        return redirect('/dashboard')
    
    data = {
        'id': patient.id,
        'patient_emergency_contact_name': request.form.get('emergency_contact_name'),
        'emergency_contact_phone': request.form.get('emergency_contact_phone')
    }
    
    Patient.update_emergency_contact(data)
    flash('Emergency contact information updated successfully!', 'success')
    return redirect('/emergency_contacts')

@app.route('/patient/appointments')
def patient_appointments():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    patient = Patient.get_by_user_id(session['user_id'])
    
    if not patient:
        flash("Please complete your profile first", "warning")
        return redirect('/patient/dashboard')
    
    appointments = Appointment.get_patient_appointments(patient.id)
    return render_template('patient/appointments.html',
                         user=user,
                         patient=patient,
                         appointments=appointments)

@app.route('/doctor/appointments')
def doctor_appointments():
    if 'user_id' not in session or session['user_role'] != 'doctor':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    doctor = Doctor.get_by_user_id(session['user_id'])
    
    if not doctor:
        flash("Please complete your profile first", "warning")
        return redirect('/doctor/dashboard')
    
    appointments = Appointment.get_doctor_appointments(doctor.id)
    return render_template('doctor/appointments.html',
                         user=user,
                         doctor=doctor,
                         appointments=appointments)

@app.route('/patient/prescriptions')
def patient_prescriptions():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    patient = Patient.get_by_user_id(session['user_id'])
    
    if not patient:
        flash("Please complete your profile first", "warning")
        return redirect('/patient/dashboard')
    
    prescriptions = Prescription.get_by_patient_id(patient.id)
    return render_template('patient/prescriptions.html',
                         user=user,
                         patient=patient,
                         prescriptions=prescriptions)

@app.route('/doctor/patients')
def doctor_patients():
    if 'user_id' not in session or session['user_role'] != 'doctor':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    doctor = Doctor.get_by_user_id(session['user_id'])
    
    if not doctor:
        flash("Please complete your profile first", "warning")
        return redirect('/doctor/dashboard')
    
    patients = Patient.get_by_doctor_id(doctor.id)
    return render_template('doctor/patients.html',
                         user=user,
                         doctor=doctor,
                         patients=patients)

@app.route('/patient/profile')
def patient_profile():
    if 'user_id' not in session or session['user_role'] != 'patient':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    patient = Patient.get_by_user_id(session['user_id'])
    
    return render_template('patient/profile.html',
                         user=user,
                         patient=patient)

@app.route('/doctor/profile')
def doctor_profile():
    if 'user_id' not in session or session['user_role'] != 'doctor':
        return redirect('/login')
    
    user = User.get_by_id(session['user_id'])
    doctor = Doctor.get_by_user_id(session['user_id'])
    
    return render_template('doctor/profile.html',
                         user=user,
                         doctor=doctor)

@app.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    reason = request.form.get('reason')
    if not reason:
        return jsonify({'error': 'Reason is required'}), 400
    
    appointment = Appointment.get_appointment_by_id(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Verify that the user owns this appointment
    if session['user_role'] == 'patient' and appointment.patient_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    elif session['user_role'] == 'doctor' and appointment.doctor_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    Appointment.cancel_appointment(appointment_id, reason)
    return jsonify({'message': 'Appointment cancelled successfully'})