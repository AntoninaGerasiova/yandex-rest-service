import sqlite3
from  numpy import percentile

import click
from flask import current_app, g
from flask.cli import with_appcontext

from . import help_data

"""
Explicitly works with bd
"""
#bd settings and open/close/initialization functions
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
    """ 
    Insert set of citizens data to db
    
    Args:
        crequest_json (dict): data about citizens to insert
    
    Returns:
        import_id (int):  import_id if insert is succesively completed
    
    Raises:
        jsonschema.exceptions.ValidationError: if request_json is not valid json
        json.decoder.JSONDecodeError: if request_json is not of required structure or values of request_json are not of valid types
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format
        db.Error: if something went wrong during insertion in db
        
    """
    #validate json before parse it
    help_data.validate_insert_json(request_json)
    
    #parse json and get data to insert to db
    citizens_data, kinships_data = help_data.get_insert_data(request_json)
    
    citizen_len = len(citizens_data)
    kinship_len = len(kinships_data)
    
    #sql-requests
    sql_imports = '''INSERT INTO imports default values'''
    
    sql_citizens = ''' INSERT INTO citizens(import_id, citizen_id, town, street, building, apartment, name, birth_date, gender)
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
    """
    Get set of citizens with certain import_id
    
    Args:
        import_id (int): import id of set to get
    
    Returns:
        dict: information about citizens of set with import_id
        
    Raises:
        Exception: when there is no set with given import_id in db
    """
    #generate sql requests    
    sql_get_citizens = '''SELECT * 
    FROM  citizens
    WHERE import_id = ?
    '''
    
    sql_get_kins = '''SELECT citizen_id, relative_id 
    FROM  kinships
    WHERE import_id = ?
    ORDER by citizen_id
    '''
    
    #start work with db
    db = get_db()
    cur = db.execute(sql_get_citizens, (import_id,))
    
    #TODO compeled to use fetchall to check if cursor is empty for sqlite. Very annoying. Change this when leave sqlite for good
    rows = cur.fetchall()
    if not rows: 
        raise Exception("import with import_id = {} does not exist".format(import_id))
    #first get all data except relatives connections   - fill in structure  
    citizens_dict = dict()
    for row in rows:
        citizen_id = row["citizen_id"]
        citizens_dict[citizen_id] = {"citizen_id": citizen_id,
                                     "town": row["town"],
                                     "street": row["street"],
                                     "building": row["building"],
                                     "apartment": row["apartment"],
                                     "name": row["name"],
                                     "birth_date": help_data.date_to_output_format(row["birth_date"]),
                                     "gender": row["gender"],
                                     "relatives": list()}
    
    #now get information about relative connections - fill information about relatives
    cur_kins = db.execute(sql_get_kins, (import_id,))
    for row in cur_kins:
        citizen_id = row["citizen_id"]
        relative_id = row["relative_id"]
        citizens_dict[citizen_id]["relatives"].append(relative_id)
    return {"data":list(citizens_dict.values())}
        

def fix_data(import_id, citizen_id, request_json):
    """
    Updete information about citizen with given import_id and citizen_id
        
    Args:
        import_id (int): import id  of set  where citizen is
        citizen_id (int):citizen id whose information to change
        request_json (dict): data to update
    
    Returns:
        res(dict):    Updated information about citizen
    
    Raises:
        jsonschema.exceptions.ValidationError: if request_json is not valid json
        json.decoder.JSONDecodeError: if request_json is of not required structure or values of request_json are of not valid types
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format or if citizen with  given import_id, citizen_id not in base
    """

    #validate request_json
    help_data.validate_patch_json(request_json)
    
    #form all necesary requests
    update_relatives = False
    if "relatives" in request_json:
        update_relatives = True
        sql_delete_kins_for_citizen = '''DELETE FROM kinships WHERE import_id = {} and citizen_id = {}'''.format(import_id, citizen_id)
        sql_delete_mutual_kins = '''DELETE FROM kinships WHERE import_id = {} and relative_id = {}'''.format(import_id, citizen_id)
        kinships_data = help_data.get_new_relatives(import_id, citizen_id, request_json)
        sql_insert_relatives = ''' INSERT INTO kinships(import_id, citizen_id, relative_id)
              VALUES(?,?,?) '''
        
    sql_update_citizen = help_data.form_request(import_id, citizen_id, request_json)
    
    sql_get_citizen_by_id = '''SELECT town, street, building, apartment, name, birth_date, gender 
    FROM  citizens
    WHERE import_id = ? and citizen_id = ?
    '''
    sql_get_kins_by_id = '''SELECT relative_id 
    FROM  kinships
    WHERE import_id = ? and citizen_id = ?
    ORDER by citizen_id
    '''
    
    
    #start work with db
    try:
        db = get_db()
        #check if the requered citizen' record  is in the db - for sqlite only
        #TODO:remove this check when use mysql or postgress cause they throw the proper exeption when update non-existant row
        row = db.execute(sql_get_citizen_by_id, (import_id, citizen_id)).fetchone()
        if row is None:
            raise Exception("citizen's record doesn't exist")
        
        #update citizen data
        db.execute("begin")
        #if there are keys except relatives
        if sql_update_citizen:
            db.execute(sql_update_citizen)
        
        if update_relatives:
            db.execute(sql_delete_kins_for_citizen)
            db.execute(sql_delete_mutual_kins)
            db.executemany(sql_insert_relatives, kinships_data)
        db.execute("commit")
    except db.Error:
        print("Patch failed!")
        db.execute("rollback")
        raise
        
    #Get patched information about citizen back, to return to user
    #TODO: Find out should it exectly be the same as we updated in case of interleaving
    row = db.execute(sql_get_citizen_by_id, (import_id, citizen_id)).fetchone()
    res = {
            "data": {"citizen_id": citizen_id,
                    "town": row["town"],
                    "street": row["street"],
                    "building": row["building"],
                    "apartment": row["apartment"],
                    "name": row["name"],
                    "birth_date": help_data.date_to_output_format(row["birth_date"]),
                    "gender": row["gender"],
                    "relatives": list()}}
    cur_kins = db.execute(sql_get_kins_by_id, (import_id, citizen_id))
    for row in cur_kins:
        res["data"]["relatives"].append(row["relative_id"])
    return res

def get_citizens_birthdays_for_import_id(import_id):
    """
    Get information about relatives' birthdays grouped by mothes
    
    Args:
        import_id (int): import_id for which get such information
    
    Returns:
        (dict):    information about relatives' birthdays grouped by monthes
        
    Raises:
        Exception:  if set with import_id doesn't exist in db
    """
    #generate sql-requests
    sql_get_kins_birtmonth = '''SELECT citizens.citizen_id as citizen_id,
    strftime("%m", (SELECT  birth_date FROM citizens WHERE citizen_id = relative_id and citizens.import_id = ?)) as birth_month,
    count(citizens.citizen_id) as presents
    FROM citizens, kinships  
    WHERE citizens.citizen_id = kinships.citizen_id and citizens.import_id = kinships.import_id and citizens.import_id = ?
    GROUP BY citizens.citizen_id, birth_month
    '''
    
    #start work with bd
    db = get_db()
    cur = db.execute(sql_get_kins_birtmonth, (import_id, import_id))
    #TODO: change this check when work with postgress
    rows = cur.fetchall()
    if not rows: 
        raise Exception("import with import_id = {} does not exist".format(import_id))
    result_dict  = {"1": [], "2": [], "3": [], "4": [],  "5": [], "6": [], "7":[],  "8": [], "9": [], "10": [], "11": [], "12": []}
    for row in rows:
        key = str(int(row["birth_month"]))
        result_dict[key].append({
            "citizen_id": row["citizen_id"],
            "presents": row["presents"]
            })
    return {"data":result_dict}

def get_statistic_for_import_id(import_id):
    """
        Count percentiles for  50%, 75% and 99%  for age for citizens grouped by towns for given import_id (particular import)
        
        Args:
            import_id (int): import_id for which get such information
        
        Returns:
            (dict):   percentiles for  50%, 75% and 99%  for age for citizens grouped by towns formed as requaired structure 
            
        Raises:
            Exception:  if set with import_id doesn't exist in db
    """
    #sql-requests
    sql_get_citizens = '''SELECT town, birth_date
    FROM  citizens
    WHERE import_id = ?
    '''
    
    #start work with bd
    db = get_db()
    cur = db.execute(sql_get_citizens, (import_id,))
    #TODO: change this check when work with postgress
    rows = cur.fetchall()
    if not rows: 
        raise Exception("import with import_id = {} does not exist".format(import_id))
    age_dict = dict()
    for row in rows:
        key = row["town"]
        if key not in age_dict:
            age_dict[key] = [help_data.get_age(row["birth_date"])]
        else:
            age_dict[key].append(help_data.get_age(row["birth_date"]))
    data = list()
    for town in age_dict:
        ages = age_dict[town]
        perc_list = percentile(ages, [50, 75, 99], interpolation='linear')
        data.append({"town": town, "p50": perc_list[0], "p75": perc_list[1], "p99": perc_list[2]})
    return {"data": data}
    
  




    

    
    
