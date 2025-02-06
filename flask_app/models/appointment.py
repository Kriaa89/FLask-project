from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import datetime

class Appointment:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data.get('id')
        self.doctor_id = data.get('doctor_id')
        self.nurse_id = data.get('nurse_id')
        self.patient_id = data.get('patient_id')
        self.date = data.get('date')
        self.time = data.get('time')
        self.status = data.get('status')
        self.type = data.get('type')
        self.reason = data.get('reason')
        self.notes = data.get('notes')
        self.prescription = data.get('prescription')
        self.symptoms = data.get('symptoms')
        self.diagnosis = data.get('diagnosis')
        self.patient_address = data.get('patient_address')
        self.reminder_sent = data.get('reminder_sent', False)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        # Join fields
        self.doctor_name = data.get('doctor_name')
        self.nurse_name = data.get('nurse_name')
        self.patient_name = data.get('patient_name')
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO appointments (doctor_id, nurse_id, patient_id, date, time,
                            status, type, reason, notes, prescription, symptoms,
                            diagnosis, patient_address, reminder_sent)
        VALUES (%(doctor_id)s, %(nurse_id)s, %(patient_id)s, %(date)s, %(time)s,
                %(status)s, %(type)s, %(reason)s, %(notes)s, %(prescription)s,
                %(symptoms)s, %(diagnosis)s, %(patient_address)s, %(reminder_sent)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_id(cls, appointment_id):
        query = """
            SELECT a.*, 
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                CONCAT(n.first_name, ' ', n.last_name) as nurse_name,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name
            FROM appointments a
            LEFT JOIN users d ON d.id = a.doctor_id
            LEFT JOIN users n ON n.id = a.nurse_id
            LEFT JOIN users p ON p.id = a.patient_id
            WHERE a.id = %(appointment_id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, {'appointment_id': appointment_id})
        return cls(results[0]) if results else None
    
    @classmethod
    def get_by_patient_id(cls, patient_id):
        query = """
            SELECT a.*, 
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                CONCAT(n.first_name, ' ', n.last_name) as nurse_name,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name
            FROM appointments a
            LEFT JOIN users d ON d.id = a.doctor_id
            LEFT JOIN users n ON n.id = a.nurse_id
            LEFT JOIN users p ON p.id = a.patient_id
            WHERE a.patient_id = %(patient_id)s
            ORDER BY a.date DESC, a.time DESC;
        """
        results = connectToMySQL(cls.db).query_db(query, {'patient_id': patient_id})
        return [cls(row) for row in results]
    
    @classmethod
    def get_by_doctor_id(cls, doctor_id):
        query = """
            SELECT a.*, 
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                CONCAT(n.first_name, ' ', n.last_name) as nurse_name,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name
            FROM appointments a
            LEFT JOIN users d ON d.id = a.doctor_id
            LEFT JOIN users n ON n.id = a.nurse_id
            LEFT JOIN users p ON p.id = a.patient_id
            WHERE a.doctor_id = %(doctor_id)s
            ORDER BY a.date DESC, a.time DESC;
        """
        results = connectToMySQL(cls.db).query_db(query, {'doctor_id': doctor_id})
        return [cls(row) for row in results]
    
    @classmethod
    def get_by_nurse_id(cls, nurse_id):
        query = """
            SELECT a.*, 
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                CONCAT(n.first_name, ' ', n.last_name) as nurse_name,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name
            FROM appointments a
            LEFT JOIN users d ON d.id = a.doctor_id
            LEFT JOIN users n ON n.id = a.nurse_id
            LEFT JOIN users p ON p.id = a.patient_id
            WHERE a.nurse_id = %(nurse_id)s
            ORDER BY a.date DESC, a.time DESC;
        """
        results = connectToMySQL(cls.db).query_db(query, {'nurse_id': nurse_id})
        return [cls(row) for row in results]
    
    @classmethod
    def update(cls, data):
        query = """
            UPDATE appointments 
            SET doctor_id = %(doctor_id)s,
                nurse_id = %(nurse_id)s,
                patient_id = %(patient_id)s,
                date = %(date)s,
                time = %(time)s,
                status = %(status)s,
                type = %(type)s,
                reason = %(reason)s,
                notes = %(notes)s,
                prescription = %(prescription)s,
                symptoms = %(symptoms)s,
                diagnosis = %(diagnosis)s,
                patient_address = %(patient_address)s,
                reminder_sent = %(reminder_sent)s
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def delete(cls, appointment_id):
        query = "DELETE FROM appointments WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, {'id': appointment_id})
    
    @classmethod
    def count_all(cls):
        query = "SELECT COUNT(*) as count FROM appointments;"
        results = connectToMySQL(cls.db).query_db(query)
        return results[0]['count'] if results else 0
    
    @staticmethod
    def validate_appointment(data):
        is_valid = True
        
        # Required fields
        required_fields = ['date', 'time', 'type', 'reason']
        for field in required_fields:
            if field not in data or not data[field]:
                flash(f"{field.replace('_', ' ').title()} is required", "warning")
                is_valid = False
        
        # Validate date is not in the past
        if data.get('date'):
            try:
                appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                if appointment_date < datetime.now().date():
                    flash("Appointment date cannot be in the past", "warning")
                    is_valid = False
            except ValueError:
                flash("Invalid date format", "warning")
                is_valid = False
        
        # Validate time format
        if data.get('time'):
            try:
                datetime.strptime(data['time'], '%H:%M')
            except ValueError:
                flash("Invalid time format", "warning")
                is_valid = False
        
        return is_valid
