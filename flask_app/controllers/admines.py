from flask import render_template, redirect, request, session, flash
from flask_app import app, bcrypt
from flask_app.models.admin import Admin

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        if not Admin.validate_registration(request.form):
            return redirect('/admin/register')
        
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': pw_hash
        }
        admin_id = Admin.save(data)
        session['admin_id'] = admin_id
        return redirect('/admin/dashboard')
    
    return render_template('admin/register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin = Admin.get_by_email(request.form['email'])
        if not admin or not bcrypt.check_password_hash(admin.password, request.form['password']):
            flash("Invalid email or password", "danger")
            return redirect('/admin/login')
        
        session['admin_id'] = admin.id
        return redirect('/admin/dashboard')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect('/admin/login')
    
    # Fetch counts for dashboard
    male_count = User.count_by_gender('male')
    female_count = User.count_by_gender('female')
    appointment_count = Appointment.count_all()
    doctor_count = Doctor.count_all()
    
    return render_template('admin/dashboard.html',
                        male_count=male_count,
                        female_count=female_count,
                        appointment_count=appointment_count,
                        doctor_count=doctor_count)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')