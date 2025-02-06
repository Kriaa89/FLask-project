from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Admin:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO admins (first_name, last_name, email, password)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM admins WHERE email = %(email)s;"
        results = connectToMySQL(cls.db).query_db(query, {'email': email})
        return cls(results[0]) if results else None
    
    @staticmethod
    def validate_registration(data):
        is_valid = True
        if len(data['first_name']) < 2:
            flash("First name must be at least 2 characters", "danger")
            is_valid = False
        if len(data['last_name']) < 2:
            flash("Last name must be at least 2 characters", "danger")
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid email address", "danger")
            is_valid = False
        if len(data['password']) < 8:
            flash("Password must be at least 8 characters", "danger")
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash("Passwords do not match", "danger")
            is_valid = False
        return is_valid