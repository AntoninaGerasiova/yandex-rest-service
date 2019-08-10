from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
"""

#TODO import_id maybe sould be autoincrement=False
class Citizens(db.Model):
        
    import_id = db.Column(db.Integer, primary_key=True, nullable=False)
    citizen_id = db.Column(db.Integer, primary_key=True, nullable=False)
    town = db.Column(db.String, nullable=False)
    street  = db.Column(db.String, nullable=False)
    building = db.Column(db.String, nullable=False)
    apartment = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.DateTime, nullable=False)
    gender  = db.Column(db.String, db.Enum('male', 'female', name='gender_types'), nullable=False)
    
    def __init__(self, 
                 import_id =None, 
                 citizen_id=None, 
                 town=None, 
                 street=None, 
                 building=None, 
                 apartment=None, 
                 name=None, 
                 birth_date=None, 
                 gender=None):
        super(citizens, self).__init__(**kwargs)
        self.import_id = import_id
        self.citizen_id = citizen_id
        self.town = town
        self.street = street
        self.building = building
        self.apartment = apartment
        self.name = name
        self.birth_date = birth_date
        self.gender = gender
    
    @staticmethod
    def get_output_date(date):
        month = date.month if date.month >= 10 else "0" + str(date.month)
        day = date.day if date.day >= 10 else "0" + str(date.day)
        return "{}.{}.{}".format(day, month, date.year)
    
    def serialize(self):
        return {
            'citizen_id': self.citizen_id,
            'town': self.town,
            'street':self.street,
            'building': self.building, 
            'apartment': self.apartment,
            'name': self.name,
            'birth_date':self.get_output_date(self.birth_date),
            'gender':self.gender,
            'relatives':list()}
    
    
    
    @staticmethod
    def get_keys():
        return ("import_id", "citizen_id", "town", "street", "building", "apartment", "name", "birth_date", "gender")
        


class Kinships(db.Model):
    
    import_id = db.Column(db.Integer, primary_key=True, nullable=False)
    citizen_id = db.Column(db.Integer, primary_key=True, nullable=False)
    relative_id = db.Column(db.Integer, primary_key=True, nullable=False)
    
    def __init__(self, 
                 import_id=None, 
                 citizen_id=None,
                 relative_id=None):
        
        super(kinships, self).__init__(**kwargs)
        self.import_id = import_id
        self.citizen_id = citizen_id
        self.relative_id = relative_id
    
    @staticmethod
    def get_keys():
        return ("import_id", "citizen_id", "relative_id")

class Imports(db.Model):
    import_id = db.Column(db.Integer, primary_key=True)
