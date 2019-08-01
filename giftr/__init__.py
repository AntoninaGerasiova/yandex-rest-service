import os
from flask import Flask, request, jsonify

def trace():
    from inspect import currentframe, getframeinfo
    cf = currentframe()
    print('>>>>> TRACE: {}:{}'.format(getframeinfo(cf).filename, cf.f_back.f_lineno))

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'gifts.sqlite'),
    )
    
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # register the database commands
    from giftr import db
    db.init_app(app)
    
    # a simple page that says hello
    @app.route('/test',  methods=['POST'])
    def test():
        data = request.get_json()
        action = data.get("action","")
        if action == 'init':
            db.init_db()
            return("Initialized the database.")
        return 'Nothing has been done'
    
        
    @app.route('/imports', methods=['POST'])
    def imports():
        if request.method == 'POST':
            #print(request.get_data())
            request_json = request.get_json()
            #print(request_json)
            try:
                import_id = db.insert_citizens_set(request_json)
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
            res = db.get_citizens_set(import_id)
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
                res = db.fix_data(import_id, citizen_id, request_json)
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
            res = db.get_citizens_birthdays_for_import_id(import_id)
            res = jsonify(res)
            return res
        except Exception as exc:
            trace()
            import traceback
            traceback.print_exc()
            return_str = "Get failed: {}".format(str(exc))
            return return_str, 400

    return app

    
