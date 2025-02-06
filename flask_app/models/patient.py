from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

class Patient:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.medical_history = data.get('medical_history')
        self.allergies = data.get('allergies')
        self.current_medications = data.get('current_medications')
        self.blood_type = data.get('blood_type')
        self.emergency_contact = data.get('emergency_contact')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        # Join fields from users table
        self.name = data.get('name')  # From CONCAT of first_name and last_name
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO patients (user_id, blood_type, emergency_contact,
                        allergies, current_medications, medical_history)
        VALUES (%(user_id)s, %(blood_type)s, %(emergency_contact)s,
                %(allergies)s, %(current_medications)s, %(medical_history)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_user_id(cls, user_id):
        query = """
            SELECT p.*, CONCAT(u.first_name, ' ', u.last_name) as name 
            FROM patients p
            JOIN users u ON u.id = p.user_id
            WHERE p.user_id = %(user_id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, {'user_id': user_id})
        return cls(results[0]) if results else None
    
    @classmethod
    def get_by_id(cls, patient_id):
        query = """
            SELECT p.*, CONCAT(u.first_name, ' ', u.last_name) as name 
            FROM patients p
            JOIN users u ON u.id = p.user_id
            WHERE p.id = %(patient_id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, {'patient_id': patient_id})
        return cls(results[0]) if results else None
    
    @classmethod
    def update(cls, data):
        query = """
            UPDATE patients 
            SET blood_type = %(blood_type)s,
                emergency_contact = %(emergency_contact)s,
                allergies = %(allergies)s,
                current_medications = %(current_medications)s,
                medical_history = %(medical_history)s
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @staticmethod
    def validate_profile(data):
        is_valid = True
        
        # Required fields
        required_fields = ['blood_type', 'emergency_contact', 'allergies', 'current_medications', 'medical_history']
        for field in required_fields:
            if field not in data or not data[field]:
                flash(f"{field.replace('_', ' ').title()} is required", "warning")
                is_valid = False
        
        return is_valid
