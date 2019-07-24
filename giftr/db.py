import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


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
    
    
def insert_citizens_set(request_json):
    citizens_data, kinships_data = get_insert_data(request_json)
    print(citizens_data)
    print(kinships_data)
    sql_get_import_id = '''SELECT max(import_id) as id FROM citizens'''
    
    sql_citizens = ''' INSERT INTO citizens(import_id, citizen_id, town, street, building, appartement, name, birth_date, gender)
              VALUES(?,?,?,?,?,?,?,?,?) '''
              
    sql_kinship = ''' INSERT INTO kinship(import_id, citizen_id, relative_id)
              VALUES(?,?,?) '''
    
    db = get_db()
    
    import_id = db.execute(sql_get_import_id).fetchone()['id']
    
    if import_id == None:
        import_id  = 1
    else:
        import_id += 1
    
    for citizen_data in citizens_data:
        citizen_data = [import_id] + citizen_data
        db.execute(sql_citizens,  citizen_data)
        
    for kinship_data in kinships_data:
        kinship_data = [import_id] + kinship_data
        db.execute(sql_kinship, kinship_data)

    db.commit()
    
    return 1

def get_insert_data(request_json):
    
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
        birth_date = citizen['birth_date']
        gender = citizen['gender']
        relatives = citizen['relatives']
        citizens_data.append([citizen_id, town, street, building, appartement, name, birth_date, gender])
        for relative in relatives:
            kinships_data.append([citizen_id, relative])
    return citizens_data, kinships_data
        
        
    
    
