import json
from flask import Flask, request, jsonify

app = Flask(__name__)

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

@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>',methods=['PATCH'])
def change(import_id, citizen_id):
    if request.method == 'PATCH':
        return fix_data(import_id, citizen_id)

def fix_data(import_id, citizen_id):
    request_json = request.get_json()
    print(request_json)
    
    res   =   {
        "data": {"citizen_id": 1,
                 "town": "Керчь",
                 "street": "Иосифа Бродского",
                 "building": "16к7стр5",
                 "appartement": 7,
                 "name": "Иванов Иван Иванович",
                 "birth_date": "01.02.2000",
                 "gender": "male",
                 "relatives": [2, 28]}}
    res = jsonify(res)

    return res
      
@app.route('//imports/$import_id/citizens')



#with app.test_request_context('/imports', method='POST'):
#    assert request.path == '/imports'
#    assert request.method == 'POST'
#    print("we are here")
#    print(request.form)
    



