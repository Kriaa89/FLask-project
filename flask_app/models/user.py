from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data['id']
        self.role = data['role']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.gender = data['gender']
        self.email = data['email']
        self.phone_number = data['phone_number']
        self.profile_picture = data['profile_picture']
        self.address = data['address']
        self.date_of_birth = data['date_of_birth']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO users (role, first_name, last_name, gender, email, 
                        phone_number, password, profile_picture, address, date_of_birth) 
        VALUES (%(role)s, %(first_name)s, %(last_name)s, %(gender)s, %(email)s, 
                %(phone_number)s, %(password)s, %(profile_picture)s, %(address)s, %(date_of_birth)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(cls.db).query_db(query, data)
        return cls(results[0]) if results else None
    
    @classmethod
    def get_by_id(cls, user_id):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        if isinstance(user_id, dict) and 'id' in user_id:
            data = user_id
        else:
            data = {'id': int(user_id)}
        results = connectToMySQL(cls.db).query_db(query, data)
        return cls(results[0]) if results else None
    
    @classmethod
    def update(cls, data):
        query = """
            UPDATE users 
            SET first_name = %(first_name)s,
                last_name = %(last_name)s,
                gender = %(gender)s,
                email = %(email)s,
                phone_number = %(phone_number)s,
                profile_picture = %(profile_picture)s,
                address = %(address)s,
                date_of_birth = %(date_of_birth)s
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def update_password(cls, data):
        query = """
            UPDATE users 
            SET password = %(password)s,
                reset_token = NULL,
                reset_token_expires = NULL
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def save_reset_token(cls, data):
        query = """
            UPDATE users 
            SET reset_token = %(reset_token)s,
                reset_token_expires = %(reset_token_expires)s
            WHERE email = %(email)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_reset_token(cls, data):
        query = """
            SELECT * FROM users 
            WHERE reset_token = %(reset_token)s 
            AND reset_token_expires > NOW();
        """
        results = connectToMySQL(cls.db).query_db(query, data)
        return cls(results[0]) if results else None

    @classmethod
    def count_by_gender(cls, gender):
        query = "SELECT COUNT(*) as count FROM users WHERE gender = %(gender)s;"
        results = connectToMySQL(cls.db).query_db(query, {'gender': gender})
        return results[0]['count'] if results else 0
    
    @staticmethod
    def validate_registration(data):
        is_valid = True
        
        # Required fields validation
        required_fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 
                        'role', 'gender', 'phone_number']
        for field in required_fields:
            if field not in data or not data[field]:
                flash(f"{field.replace('_', ' ').title()} is required", "danger")
                is_valid = False
        
        if not is_valid:
            return False
            
        # Validate first name and last name
        if len(data['first_name']) < 2:
            flash("First name must be at least 2 characters", "danger")
            is_valid = False
        if len(data['last_name']) < 2:
            flash("Last name must be at least 2 characters", "danger")
            is_valid = False
            
        # Validate email
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid email address", "danger")
            is_valid = False
        
        # Check if email already exists
        if User.get_by_email({'email': data['email']}):
            flash("Email already registered", "danger")
            is_valid = False
            
        # Validate phone number (Tunisia format)
        phone_regex = re.compile(r'^(\+216|216)?[02-57-9]\d{7}$')
        if not phone_regex.match(data['phone_number'].replace(' ', '')):
            flash("Invalid phone number format. Please use Tunisia phone number format (8 digits, cannot start with 1, 6, or 8)", "danger")
            is_valid = False
            
        # Validate password
        if len(data['password']) < 8:
            flash("Password must be at least 8 characters", "danger")
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash("Passwords do not match", "danger")
            is_valid = False
        if not any(char.isupper() for char in data['password']):
            flash("Password must contain at least one uppercase letter", "danger")
            is_valid = False
        if not any(char.islower() for char in data['password']):
            flash("Password must contain at least one lowercase letter", "danger")
            is_valid = False
        if not any(char.isdigit() for char in data['password']):
            flash("Password must contain at least one number", "danger")
            is_valid = False
        if not any(char in '!@#$%^&*(),.?":{}|<>' for char in data['password']):
            flash("Password must contain at least one special character", "danger")
            is_valid = False
            
        return is_valid

    @staticmethod
    def validate_login(data):
        is_valid = True
        
        if not data['email']:
            flash("Email is required", "danger")
            is_valid = False
            
        if not data['password']:
            flash("Password is required", "danger")
            is_valid = False
            
        return is_valid

    @staticmethod
    def validate_password_reset_request(email):
        is_valid = True
        
        if not email:
            flash("Email is required", "danger")
            is_valid = False
        elif not EMAIL_REGEX.match(email):
            flash("Invalid email address", "danger")
            is_valid = False
        
        return is_valid

    @staticmethod
    def validate_password_reset(data):
        is_valid = True
        
        if not data.get('password'):
            flash("Password is required", "danger")
            is_valid = False
        elif len(data['password']) < 8:
            flash("Password must be at least 8 characters", "danger")
            is_valid = False
        elif not any(char.isupper() for char in data['password']):
            flash("Password must contain at least one uppercase letter", "danger")
            is_valid = False
        elif not any(char.islower() for char in data['password']):
            flash("Password must contain at least one lowercase letter", "danger")
            is_valid = False
        elif not any(char.isdigit() for char in data['password']):
            flash("Password must contain at least one number", "danger")
            is_valid = False
        elif not any(char in '!@#$%^&*(),.?":{}|<>' for char in data['password']):
            flash("Password must contain at least one special character", "danger")
            is_valid = False
            
        if not data.get('confirm_password'):
            flash("Confirm password is required", "danger")
            is_valid = False
        elif data['password'] != data['confirm_password']:
            flash("Passwords do not match", "danger")
            is_valid = False
            
        return is_valid
