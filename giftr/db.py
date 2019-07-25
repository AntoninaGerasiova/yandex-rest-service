import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

#bd settings and open/close/initialization function
def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")

def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db) #tells Flask to call that function when cleaning up after returning the response
    app.cli.add_command(init_db_command) #adds a new command that can be called with the flask command
    
    
#help functions
def date_to_bd_format(date):
    """ get data in format suitable for bad format"""
    return  "-".join(reversed(date.split(".")))
    
    
def date_to_output_format(date):
    """get data in format suitable for output"""
    month = date.month if date.month >= 10 else "0" + str(date.month)
    day = date.day if date.day >= 10 else "0" + str(date.day)
    return "{}.{}.{}".format(day, month, date.year)



#work with bd
def insert_citizens_set(request_json):
    """ insert set of citizens data to db"""
    citizens_data, kinships_data = get_insert_data(request_json)
    print(citizens_data)
    print(kinships_data)
    
    #sql requests
    sql_imports = '''INSERT INTO imports default values'''
    
    sql_citizens = ''' INSERT INTO citizens(import_id, citizen_id, town, street, building, appartement, name, birth_date, gender)
              VALUES(?,?,?,?,?,?,?,?,?) '''
              
    sql_kinship = ''' INSERT INTO kinships(import_id, citizen_id, relative_id)
              VALUES(?,?,?) '''
    
    sql_corrupted = "Not even sql command"
    
    #working with db
    try:
        db = get_db()
        db.execute("begin")
        #add row into sql_imports table and get unique import_id as responce
        #should be unique even with interleaving
        import_id = db.execute(sql_imports).lastrowid
        
        #insert citizens data into db using import_id that we have got
        for citizen_data in citizens_data:
            citizen_data = [import_id] + citizen_data
            db.execute(sql_citizens,  citizen_data)
    
        #db.execute(sql_corrupted)
        for kinship_data in kinships_data:
            kinship_data = [import_id] + kinship_data
            db.execute(sql_kinship, kinship_data)


        db.execute("commit")
    except db.Error:
        print("failed!")
        db.execute("rollback")
        import_id = None
    
    return import_id



def get_insert_data(request_json):
    """Unpack data from request_json structure"""
    citizens = request_json["citizens"]
    citizens_data = list()
    kinships_data = list()
    for citizen in citizens:
        citizen_id = citizen['citizen_id']
        town = citizen['town']
        street = citizen['street']
        building = citizen['building']
        appartement = citizen['appartement']
        name = citizen['name']
        birth_date = date_to_bd_format(citizen['birth_date'])
        gender = citizen['gender']
        relatives = citizen['relatives']
        citizens_data.append([citizen_id, town, street, building, appartement, name, birth_date, gender])
        for relative in relatives:
            kinships_data.append([citizen_id, relative])
    return citizens_data, kinships_data
        

def get_citizens_set(import_id):
    #sql requests
    sql_get_citizens_and_kins = '''SELECT citizens.citizen_id as citizen_id, town,street, building, appartement, name, birth_date, gender, relative_id 
    FROM citizens, kinships  
    WHERE citizens.citizen_id = kinships.citizen_id and citizens.import_id = kinships.import_id and citizens.import_id = ?'''
    
    sql_get_citizens = '''SELECT * 
    FROM  citizens
    WHERE import_id = ?
    '''
    
    sql_get_kins = '''SELECT citizen_id, relative_id 
    FROM  kinships
    WHERE import_id = ?
    ORDER by citizen_id
    '''
    
    db = get_db()
    cur = db.execute(sql_get_citizens, (import_id,))
    
    citizens_dict = dict()
    for row in cur:
        citizen_id = row["citizen_id"]
        citizens_dict[citizen_id] = {"citizen_id": citizen_id,
                                     "town": row["town"],
                                     "street": row["street"],
                                     "building": row["building"],
                                     "appartement": row["appartement"],
                                     "name": row["name"],
                                     "birth_date": date_to_output_format(row["birth_date"]),
                                     "gender": row["gender"],
                                     "relatives": list()}
    
    cur_kins = db.execute(sql_get_kins, (import_id,))
    for row in cur_kins:
        #print(row.keys())
        citizen_id = row["citizen_id"]
        relative_id = row["relative_id"]
        citizens_dict[citizen_id]["relatives"].append(relative_id)
    return ({"data":list(citizens_dict.values())})
        
    
    
