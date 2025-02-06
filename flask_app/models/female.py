from flask_app.config.mysqlconnection import connectToMySQL

class Female:
    db = "homecare_db"
    
    def __init__(self, data):
        self.id = data.get('id')
        self.patient_id = data.get('patient_id')
        self.last_menstrual = data.get('last_menstrual')
        self.mammogram_date = data.get('mammogram_date')
        self.pap_smear_date = data.get('pap_smear_date')
        self.due_date = data.get('due_date')
        self.pregnant = data.get('pregnant')
        self.notes = data.get('notes')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO females (patient_id, last_menstrual, mammogram_date, pap_smear_date,
                        due_date, pregnant, notes)
        VALUES (%(patient_id)s, %(last_menstrual)s, %(mammogram_date)s, %(pap_smear_date)s,
                %(due_date)s, %(pregnant)s, %(notes)s);
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_by_patient_id(cls, patient_id):
        query = "SELECT * FROM females WHERE patient_id = %(patient_id)s;"
        results = connectToMySQL(cls.db).query_db(query, {'patient_id': patient_id})
        return cls(results[0]) if results else None

    @classmethod
    def update(cls, data):
        query = """
        UPDATE females 
        SET last_menstrual = %(last_menstrual)s,
            mammogram_date = %(mammogram_date)s,
            pap_smear_date = %(pap_smear_date)s,
            due_date = %(due_date)s,
            pregnant = %(pregnant)s,
            notes = %(notes)s
        WHERE patient_id = %(patient_id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)
