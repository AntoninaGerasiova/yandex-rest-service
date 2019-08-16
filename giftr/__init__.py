"""
application factory
"""
import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc as sqlalchemy_exc

from .models import db
from .exceptions import SetNotFoundError, BadFormatError, DBError
from . import db_helper

def trace():
    from inspect import currentframe, getframeinfo
    cf = currentframe()
    print('>>>>> TRACE: {}:{}'.format(getframeinfo(cf).filename, cf.f_back.f_lineno))

def create_app(test_config=None):
    """
    create and configure the app
    """
    app = Flask(__name__, instance_relative_config=True)
    
    use_postgress = True
    if use_postgress: 
        # db path for postgres
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///gifts"
    else:
        # db path for sqlite
        db_path  = os.path.join(app.instance_path, 'gifts.sqlite')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    
    # test interface  - init db
    @app.route('/test',  methods=['POST'])
    def test():
        print("TEST_INTERFACE ")
        data = request.get_json()
        action = data.get("action","")
        if action == 'init':
            db.drop_all()
            db.create_all()
            return("Initialized the database.")
        return 'Nothing has been done'
    
        
    @app.route('/imports', methods=['POST'])
    def insert():
        """
        Insert interface
           
        Returns: 
            response: response containing import id,  201: Created -  if insertion was successful
            return_str: error message, 400: Bad Request - if can't make insertion due to some problem with client's data
            return_str: error message, 500: Internal Server Error - if unexpected error occured during insertion (indicator that something is wrong with server)
           
        """
        if request.method == 'POST':
            request_json = request.get_json()
            try:
                import_id = db_helper.insert_citizens_set(request_json)
                response = jsonify({"data": {"import_id": import_id}})
                return response , 201
            except (BadFormatError, DBError) as e:
                return_str = "Insertion failed: {}".format(str(e))
                return return_str, 400
            #non-expected exception
            except Exception as e:
                trace()
                import traceback
                traceback.print_exc()
                return_str = "Insertion failed: {}".format(str(e))
                return return_str, 500

    @app.route('/imports/<int:import_id>/citizens')
    def get_citizens(import_id):
        """
        Get citizens set interface
           
        Args:
            import_id - id of citizens' set
        
        Returns: 
            response: response containing set of citizens,  200: OK -  if query was successful
            return_str: error message, 404: Not Found - if there are no set of citizens with import_id in db
            return_str: error message, 500: Internal Server Error - if unexpected error occured during query (indicator that something is wrong with server)
        """
        try:
            res = db_helper.get_citizens_set(import_id)
            res = jsonify(res)
            return res
        
        except SetNotFoundError as e:
            return_str = "Get failed: {}".format(str(e))
            return return_str, 404
        
        # non-expected exception
        except Exception as e:
            trace()
            import traceback
            traceback.print_exc()
            return_str = "Insertion failed: {}".format(str(e))
            return return_str, 500
        
        
    @app.route('/imports/<int:import_id>/citizens/<int:citizen_id>',methods=['PATCH'])
    def patch(import_id, citizen_id):
        """
        Patch interface
        
        Args:
            import_id - id of citizens' set
            citizen_id - citizen to patch
           
        Returns: 
            response: response containing new information about citizen,  200: OK -  if patch was succesfully performed
            return_str: error message, 404: Not Found - if there is no set of citizens with import_id in db, or there is not citizen with citizen_id in the set
            return_str: error message, 400: Bad Request - if can't perform patch due to some problem with client's data
            return_str: error message, 500: Internal Server Error - if unexpected error occured during patch performance (indicator that something is wrong with server)
        """
        if request.method == 'PATCH':
            request_json = request.get_json()
            try:
                res = db_helper.fix_data(import_id, citizen_id, request_json)
                res = jsonify(res)
                return res
            
            except SetNotFoundError as e:
                return_str = "Patch failed: {}".format(str(e))
                return return_str, 404
            
            except (BadFormatError,  DBError) as e:
                return_str = "Patch failed: {}".format(str(e))
                return return_str, 400
            # non-expected exception
            except Exception as e:
                trace()
                import traceback
                traceback.print_exc()
                return_str = "Patch failed: {}".format(str(e))
                return return_str, 500
    
    @app.route('/imports/<int:import_id>/citizens/birthdays')
    def get_citizens_birthdays(import_id):
        """
        Interface to get information about quantity of presents citizens buy grouped by month
           
        Args:
            import_id - id of citizens' set
        
        Returns: 
            response: response containing information about quantity of presents citizens buy,  200: OK -  if query was successful
            return_str: error message, 404: Not Found - if there are no set of citizens with import_id in db
            return_str: error message, 500: Internal Server Error - if unexpected error occured during query (indicator that something is wrong with server)
        """
        try:
            res = db_helper.get_citizens_birthdays_for_import_id(import_id)
            res = jsonify(res)
            return res
        
        except SetNotFoundError as e:
            return_str = "Get failed: {}".format(str(e))
            return return_str, 404
        
        except Exception as e:
            trace()
            import traceback
            traceback.print_exc()
            return_str = "Get failed: {}".format(str(e))
            return return_str, 500
    
    @app.route('/imports/<import_id>/towns/stat/percentile/age')
    def get_statistic(import_id):
        """
        Interface to get percetiles
           
        Args:
            import_id - id of citizens' set
        
        Returns: 
            response: response containing structure with percentiles,  200: OK -  if query was successful
            return_str: error message, 404: Not Found - if there are no set of citizens with import_id in db
            return_str: error message, 500: Internal Server Error - if unexpected error occured during query (indicator that something is wrong with server code)
        """
        try:
            res = db_helper.get_statistic_for_import_id(import_id)
            res = jsonify(res)
            return res
        
        except SetNotFoundError as e:
            return_str = "Get failed: {}".format(str(e))
            return return_str, 404
        
        # non-expected exception
        except Exception as e:
            trace()
            import traceback
            traceback.print_exc()
            return_str = "Get failed: {}".format(str(e))
            return return_str, 500

    return app

    
