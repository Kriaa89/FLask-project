from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import datetime

class Prescription:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data.get('id')
        self.doctor_id = data.get('doctor_id')
        self.patient_id = data.get('patient_id')
        self.medication_name = data.get('medication_name')
        self.dosage = data.get('dosage')
        self.frequency = data.get('frequency')
        self.duration = data.get('duration')
        self.instructions = data.get('instructions')
        self.date = data.get('date')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        # Join fields
        self.doctor_name = data.get('doctor_name')
        self.patient_name = data.get('patient_name')
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO prescriptions (doctor_id, patient_id, medication_name, dosage,
                            frequency, duration, instructions, date)
        VALUES (%(doctor_id)s, %(patient_id)s, %(medication_name)s, %(dosage)s,
                %(frequency)s, %(duration)s, %(instructions)s, %(date)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_id(cls, prescription_id):
        query = """
            SELECT p.*, 
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                CONCAT(pt.first_name, ' ', pt.last_name) as patient_name
            FROM prescriptions p
            JOIN users d ON d.id = p.doctor_id
            JOIN users pt ON pt.id = p.patient_id
            WHERE p.id = %(prescription_id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, {'prescription_id': prescription_id})
        return cls(results[0]) if results else None
    
    @classmethod
    def get_by_patient_id(cls, patient_id):
        query = """
            SELECT p.*, 
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                CONCAT(pt.first_name, ' ', pt.last_name) as patient_name
            FROM prescriptions p
            JOIN users d ON d.id = p.doctor_id
            JOIN users pt ON pt.id = p.patient_id
            WHERE p.patient_id = %(patient_id)s
            ORDER BY p.date DESC;
        """
        results = connectToMySQL(cls.db).query_db(query, {'patient_id': patient_id})
        return [cls(row) for row in results]
    
    @classmethod
    def get_by_doctor_id(cls, doctor_id):
        query = """
            SELECT p.*, 
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                CONCAT(pt.first_name, ' ', pt.last_name) as patient_name
            FROM prescriptions p
            JOIN users d ON d.id = p.doctor_id
            JOIN users pt ON pt.id = p.patient_id
            WHERE p.doctor_id = %(doctor_id)s
            ORDER BY p.date DESC;
        """
        results = connectToMySQL(cls.db).query_db(query, {'doctor_id': doctor_id})
        return [cls(row) for row in results]
    
    @classmethod
    def update(cls, data):
        query = """
            UPDATE prescriptions 
            SET medication_name = %(medication_name)s,
                dosage = %(dosage)s,
                frequency = %(frequency)s,
                duration = %(duration)s,
                instructions = %(instructions)s,
                date = %(date)s
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def delete(cls, prescription_id):
        query = "DELETE FROM prescriptions WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, {'id': prescription_id})
    
    @staticmethod
    def validate_prescription(data):
        is_valid = True
        
        # Required fields
        required_fields = ['medication_name', 'dosage', 'frequency', 'duration', 'instructions']
        for field in required_fields:
            if field not in data or not data[field]:
                flash(f"{field.replace('_', ' ').title()} is required", "warning")
                is_valid = False
        
        # Validate date is not in the future
        if data.get('date'):
            try:
                prescription_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                if prescription_date > datetime.now().date():
                    flash("Prescription date cannot be in the future", "warning")
                    is_valid = False
            except ValueError:
                flash("Invalid date format", "warning")
                is_valid = False
        
        return is_valid
