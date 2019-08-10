import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from .models import db
from . import db_helper

def trace():
    from inspect import currentframe, getframeinfo
    cf = currentframe()
    print('>>>>> TRACE: {}:{}'.format(getframeinfo(cf).filename, cf.f_back.f_lineno))

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    
    #db path for sqlite
    #db_path  = os.path.join(app.instance_path, 'gifts.sqlite')
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)
    
    #db path for postgres
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///gifts"
    
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
    def imports():
        if request.method == 'POST':
            request_json = request.get_json()
            try:
                import_id = db_helper.insert_citizens_set(request_json)
                response = jsonify({"data": {"import_id": import_id}})
                return response , 201
            except Exception as exc:
                trace()
                import traceback
                traceback.print_exc()
                return_str = "Insertion failed: {}".format(str(exc))
                return return_str, 400
                

    @app.route('/imports/<int:import_id>/citizens')
    def get_citizens(import_id):
        try:
            res = db_helper.get_citizens_set(import_id)
            res = jsonify(res)
            return res
        except Exception as exc:
                trace()
                import traceback
                traceback.print_exc()
                return_str = "Get failed: {}".format(str(exc))
                return return_str, 400
        
    @app.route('/imports/<int:import_id>/citizens/<int:citizen_id>',methods=['PATCH'])
    def change(import_id, citizen_id):
        if request.method == 'PATCH':
            request_json = request.get_json()
            try:
                res = db_helper.fix_data(import_id, citizen_id, request_json)
                res = jsonify(res)
                return res
            
            except Exception as exc:
                trace()
                import traceback
                traceback.print_exc()
                return_str = "Patch failed: {}".format(str(exc))
                return return_str, 400
    
    @app.route('/imports/<int:import_id>/citizens/birthdays')
    def get_citizens_birthdays(import_id):
        try:
            res = db_helper.get_citizens_birthdays_for_import_id(import_id)
            res = jsonify(res)
            return res
        except Exception as exc:
            trace()
            import traceback
            traceback.print_exc()
            return_str = "Get failed: {}".format(str(exc))
            return return_str, 400
    
    @app.route('/imports/<import_id>/towns/stat/percentile/age')
    def get_statistic(import_id):
        try:
            res = db_helper.get_statistic_for_import_id(import_id)
            res = jsonify(res)
            return res
        except Exception as exc:
            trace()
            import traceback
            traceback.print_exc()
            return_str = "Get failed: {}".format(str(exc))
            return return_str, 400

    return app

    
