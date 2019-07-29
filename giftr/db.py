import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

from giftr import help_data

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
    
    

#Functions to work with bd
def insert_citizens_set(request_json):
    """ insert set of citizens data to db
    Args:
        crequest_json (dict): data about citizens to insert
    
    Returns:
        int:  import_id if insert is completed
    
    Raises:
        jsonschema.exceptions.ValidationError: if request_json is not valid json
        json.decoder.JSONDecodeError: if request_json is not of required structure or values of request_json are not of valid types
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format
        db.Error: if something went wrong during insertion in db
        
    """
    citizens_data, kinships_data = help_data.get_insert_data(request_json)
    
    citizen_len = len(citizens_data)
    kinship_len = len(kinships_data)
    
    #sql requests
    sql_imports = '''INSERT INTO imports default values'''
    
    sql_citizens = ''' INSERT INTO citizens(import_id, citizen_id, town, street, building, appartement, name, birth_date, gender)
              VALUES(?,?,?,?,?,?,?,?,?) '''
              
    sql_kinship = ''' INSERT INTO kinships(import_id, citizen_id, relative_id)
              VALUES(?,?,?) '''
              
    #work with db
    try:
        db = get_db()
        db.execute("begin")
        #add row into sql_imports table and get unique import_id as responce
        #should be unique even with interleaving
        import_id = db.execute(sql_imports).lastrowid
        #insert citizens data into db using import_id that we have got
        citizen_data_with_import_id = list(map(list.__add__, [[import_id]]*citizen_len, citizens_data))
        kinship_data_with_import_id = list(map(list.__add__, [[import_id]]*kinship_len, kinships_data))
        db.executemany(sql_citizens, citizen_data_with_import_id)
        db.executemany(sql_kinship, kinship_data_with_import_id)
        db.execute("commit")
    except db.Error:
        db.execute("rollback")
        raise
    return import_id


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
        

def fix_data(import_id, citizen_id, request_json):
    print(import_id, citizen_id)
    print(request_json)
    #form all necesary requests
    update_relatives = False
    if "relatives" in request_json:
        update_relatives = True
        sql_delete_kins = '''DELETE FROM kinships WHERE import_id = {} and citizen_id = {}'''.format(import_id, citizen_id)
        kinships_data = get_new_relatives(import_id, citizen_id, request_json)
        sql_insert_relatives = ''' INSERT INTO kinships(import_id, citizen_id, relative_id)
              VALUES(?,?,?) '''
        
    sql_update_citizen = form_request(import_id, citizen_id, request_json)
    sql_get_citizen_by_id = '''SELECT town, street, building, appartement, name, birth_date, gender 
    FROM  citizens
    WHERE import_id = ? and citizen_id = ?
    '''
    sql_get_kins_by_id = '''SELECT relative_id 
    FROM  kinships
    WHERE import_id = ? and citizen_id = ?
    ORDER by citizen_id
    '''
    
    
    #work with db
    try:
        db = get_db()
        db.execute("begin")
        if update_relatives:
            db.execute(sql_delete_kins)
            db.executemany(sql_insert_relatives, kinships_data)
        db.execute(sql_update_citizen)
        db.execute("commit")
    except db.Error:
        print("failed!")
        db.execute("rollback")
        return "Can't update data"
        
    
    row = db.execute(sql_get_citizen_by_id, (import_id, citizen_id)).fetchone()
    res = {
            "data": {"citizen_id": citizen_id,
                    "town": row["town"],
                    "street": row["street"],
                    "building": row["building"],
                    "appartement": row["appartement"],
                    "name": row["name"],
                    "birth_date": date_to_output_format(row["birth_date"]),
                    "gender": row["gender"],
                    "relatives": list()}}
    cur_kins = db.execute(sql_get_kins_by_id, (import_id, citizen_id))
    for row in cur_kins:
        res["data"]["relatives"].append(row["relative_id"])
    return res


def get_new_relatives(import_id, citizen_id, request_json):
    ##TODO: check that we have that relative
    ##TODO: if I add record (citizen, relative) shoulI also add record (relative, citizen) or i have to prhibit such a change
    ##TODO:if I delete  record (citizen, relative) should I also get rid of record   (relative, citizen) or let it go
    
    kinships_data = list()
    for relative in request_json['relatives']:
            kinships_data.append([import_id, citizen_id, relative])
            
    return kinships_data


def form_request(import_id, citizen_id, request_json):
    """
    Make update request to update information about citizen with distinct citizen_id and request_id(except relative field)
    """
    
    #make request to update information (except relative field)
    sql_update_citizen = "UPDATE citizens SET "
    
    #go through keys explicitly
    #TODO: is it bad if there are some other keys, should I answer bad request
    if "town" in request_json:
        town = request_json['town']
        sql_update_citizen += "town = '{}', ".format(town)
        
    if "street" in request_json:
        street = request_json['street']
        sql_update_citizen += "street = '{}', ".format(street)
    
    if "building" in request_json:
        building = request_json['building']
        sql_update_citizen += "building = '{}', ".format(building)
        
    if "appartement" in request_json:
        appartement = request_json['appartement']
        sql_update_citizen += "appartement = {}, ".format(appartement)
        
    if "name" in request_json:
        name = request_json['name']
        sql_update_citizen += "name = '{}', ".format(name)
    
    if "birth_date" in request_json:
        birth_date = date_to_bd_format(request_json['birth_date'])
        sql_update_citizen += "birth_date = {}, ".format(birth_date)
        
    if "gender" in request_json:
        gender = request_json['gender']
        sql_update_citizen += "gender = '{}', ".format(gender)
        
    sql_update_citizen = sql_update_citizen[:-2] + " WHERE import_id = {} and citizen_id = {}".format(import_id, citizen_id)
    return sql_update_citizen
    

    
    
