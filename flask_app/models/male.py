from flask_app.config.mysqlconnection import connectToMySQL

class Male:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data['id']
        self.patient_id = data['patient_id']
        self.prostate_exam = data['prostate_exam']
        self.psa_level = data['psa_level']
        self.testicular_exam = data['testicular_exam']
        self.cardiac_test = data['cardiac_test']
        self.notes = data['notes']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO males (patient_id, prostate_exam, psa_level, testicular_exam,
                    cardiac_test, notes)
        VALUES (%(patient_id)s, %(prostate_exam)s, %(psa_level)s, %(testicular_exam)s,
                %(cardiac_test)s, %(notes)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_patient_id(cls, patient_id):
        query = "SELECT * FROM males WHERE patient_id = %(patient_id)s;"
        results = connectToMySQL(cls.db).query_db(query, {'patient_id': patient_id})
        return cls(results[0]) if results else None

    @classmethod
    def update(cls, data):
        query = """
        UPDATE males 
        SET prostate_exam = %(prostate_exam)s,
            psa_level = %(psa_level)s,
            testicular_exam = %(testicular_exam)s,
            cardiac_test = %(cardiac_test)s,
            notes = %(notes)s
        WHERE patient_id = %(patient_id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
