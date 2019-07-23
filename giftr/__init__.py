import os
from flask import Flask, request, jsonify

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
            return get_citizens_info()

    
    def get_citizens_info():
        request_json = request.get_json()
        print(request_json)
    
        import_id = save_data(request_json)
        res = jsonify({"data": {"import_id": import_id}})
        return res , 201


    def save_data(request_json):
        return 1
    
    return app
