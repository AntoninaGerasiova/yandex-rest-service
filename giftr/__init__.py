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
            request_json = request.get_json()
            #print(request_json)
            import_id = db.insert_citizens_set(request_json)
            if import_id is None:
                return "Insertion failed", 400
            
            response = jsonify({"data": {"import_id": import_id}})
            return response , 201


    
    return app
