from flask_app.config.mysqlconnection import connectToMySQL

class Review:
    DB = "homecare_db"
    
    def __init__(self, data):
        self.id = data['id']
        self.nurse_id = data['nurse_id']
        self.doctor_id = data['doctor_id']
        self.patient_id = data['patient_id']
        self.rating = data['rating']
        self.comment = data['comment']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM reviews;"
        results = connectToMySQL(cls.DB).query_db(query)
        reviews = []
        for review in results:
            reviews.append(cls(review))
        return reviews
    
    @classmethod
    def get_one(cls, review_id):
        query = "SELECT * FROM reviews WHERE id = %(id)s;"
        data = {'id': review_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        return cls(results[0]) if results else None
    
    @classmethod
    def get_by_doctor(cls, doctor_id):
        query = "SELECT * FROM reviews WHERE doctor_id = %(doctor_id)s;"
        data = {'doctor_id': doctor_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        reviews = []
        for review in results:
            reviews.append(cls(review))
        return reviews
    
    @classmethod
    def get_by_patient(cls, patient_id):
        query = "SELECT * FROM reviews WHERE patient_id = %(patient_id)s;"
        data = {'patient_id': patient_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        reviews = []
        for review in results:
            reviews.append(cls(review))
        return reviews
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO reviews (nurse_id, doctor_id, patient_id, rating, comment)
        VALUES (%(nurse_id)s, %(doctor_id)s, %(patient_id)s, %(rating)s, %(comment)s);
        """
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def update(cls, data):
        query = """
        UPDATE reviews 
        SET rating=%(rating)s,
        comment=%(comment)s
        WHERE id = %(id)s;
        """
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete(cls, review_id):
        query = "DELETE FROM reviews WHERE id = %(id)s;"
        data = {'id': review_id}
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_by_doctor_id(cls, doctor_id):
        query = "SELECT * FROM reviews WHERE doctor_id = %(doctor_id)s;"
        results = connectToMySQL(cls.DB).query_db(query, {'doctor_id': doctor_id})
        return [cls(row) for row in results]
    
    @classmethod
    def get_by_nurse_id(cls, nurse_id):
        query = "SELECT * FROM reviews WHERE nurse_id = %(nurse_id)s;"
        results = connectToMySQL(cls.DB).query_db(query, {'nurse_id': nurse_id})
        return [cls(row) for row in results]
