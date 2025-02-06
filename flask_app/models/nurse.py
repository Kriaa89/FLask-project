from flask_app.config.mysqlconnection import connectToMySQL

class Nurse:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data['id']
        self.user_id = data['user_id']
        self.specialty = data['specialty']
        self.license_number = data.get('license_number')
        self.education = data.get('education')
        self.experience_years = data.get('experience_years')
        self.hourly_rate = data.get('hourly_rate')
        self.home_care_avail = data.get('home_care_avail')
        self.languages_spoken = data.get('languages_spoken')
        self.skills = data.get('skills')
        self.average_rating = data.get('average_rating', 0)
        self.total_reviews = data.get('total_reviews', 0)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO nurses (user_id, specialty, license_number, education,
                        experience_years, hourly_rate, home_care_avail,
                        languages_spoken, skills, average_rating, total_reviews)
        VALUES (%(user_id)s, %(specialty)s, %(license_number)s, %(education)s,
                %(experience_years)s, %(hourly_rate)s, %(home_care_avail)s,
                %(languages_spoken)s, %(skills)s, %(average_rating)s, %(total_reviews)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_user_id(cls, user_id):
        query = "SELECT * FROM nurses WHERE user_id = %(user_id)s;"
        results = connectToMySQL(cls.db).query_db(query, {'user_id': user_id})
        return cls(results[0]) if results else None
