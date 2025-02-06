from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

class Doctor:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data['id']
        self.user_id = data['user_id']
        self.admin_id = data['admin_id']
        self.specialty = data['specialty']
        self.license_number = data['license_number']
        self.education = data['education']
        self.experience_years = data['experience_years']
        self.bio = data['bio']
        self.consultation_fee = data['consultation_fee']
        self.languages_spoken = data['languages_spoken']
        self.average_rating = data['average_rating']
        self.total_reviews = data['total_reviews']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.verification_status = data['verification_status']
        self.verification_date = data['verification_date']
        self.verification_notes = data['verification_notes']
        # Join fields
        self.first_name = data['first_name'] if 'first_name' in data else None
        self.last_name = data['last_name'] if 'last_name' in data else None
        self.email = data['email'] if 'email' in data else None
        self.phone_number = data['phone_number'] if 'phone_number' in data else None
        self.profile_picture = data['profile_picture'] if 'profile_picture' in data else None
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO doctors (user_id, specialty, license_number, education, 
                        experience_years, bio, consultation_fee, languages_spoken,
                        verification_status, average_rating, total_reviews, created_at, updated_at)
        VALUES (%(user_id)s, %(specialty)s, %(license_number)s, %(education)s,
                %(experience_years)s, %(bio)s, %(consultation_fee)s, %(languages_spoken)s,
                'pending', 0, 0, NOW(), NOW());
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_user_id(cls, user_id):
        query = """
            SELECT d.*, u.first_name, u.last_name, u.email, u.phone_number, u.profile_picture
            FROM doctors d
            JOIN users u ON u.id = d.user_id
            WHERE d.user_id = %(user_id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, {'user_id': user_id})
        return cls(results[0]) if results else None
    
    @classmethod
    def get_pending_verifications(cls):
        query = """
            SELECT d.*, u.first_name, u.last_name, u.email, u.phone_number, u.profile_picture
            FROM doctors d
            JOIN users u ON u.id = d.user_id
            WHERE d.verification_status = 'pending'
            ORDER BY d.created_at;
        """
        results = connectToMySQL(cls.db).query_db(query)
        return [cls(row) for row in results]
    
    @classmethod
    def update_verification_status(cls, data):
        query = """
            UPDATE doctors 
            SET verification_status = %(status)s,
                admin_id = %(admin_id)s,
                verification_date = NOW(),
                verification_notes = %(notes)s,
                updated_at = NOW()
            WHERE id = %(doctor_id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def update_profile(cls, data):
        query = """
            UPDATE doctors 
            SET specialty = %(specialty)s,
                license_number = %(license_number)s,
                education = %(education)s,
                experience_years = %(experience_years)s,
                bio = %(bio)s,
                consultation_fee = %(consultation_fee)s,
                languages_spoken = %(languages_spoken)s,
                verification_status = 'pending',
                updated_at = NOW()
            WHERE id = %(doctor_id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @staticmethod
    def validate_profile(form_data):
        is_valid = True
        
        if not form_data['specialty']:
            flash("Specialty is required", "error")
            is_valid = False
        
        if not form_data['license_number']:
            flash("License number is required", "error")
            is_valid = False
        
        if not form_data['education']:
            flash("Education information is required", "error")
            is_valid = False
        
        if not form_data['experience_years']:
            flash("Years of experience is required", "error")
            is_valid = False
        else:
            try:
                years = int(form_data['experience_years'])
                if years < 0:
                    flash("Years of experience must be a positive number", "error")
                    is_valid = False
            except ValueError:
                flash("Years of experience must be a number", "error")
                is_valid = False
        
        if not form_data['bio']:
            flash("Professional bio is required", "error")
            is_valid = False
        elif len(form_data['bio']) < 50:
            flash("Bio should be at least 50 characters long", "error")
            is_valid = False
        
        if not form_data['consultation_fee']:
            flash("Consultation fee is required", "error")
            is_valid = False
        else:
            try:
                fee = float(form_data['consultation_fee'])
                if fee < 0:
                    flash("Consultation fee must be a positive number", "error")
                    is_valid = False
            except ValueError:
                flash("Consultation fee must be a number", "error")
                is_valid = False
        
        if not form_data['languages_spoken']:
            flash("Languages spoken is required", "error")
            is_valid = False
        
        return is_valid
