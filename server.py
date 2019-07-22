import json
from flask import Flask, request, jsonify, g
import sqlite3

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
    print(import_id, citizen_id)
    if request.method == 'PATCH':
        res = fix_data(import_id, citizen_id)
        res = jsonify(res)
        return res

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
    return res
      
@app.route('/imports/<int:import_id>/citizens')
def get_citizens(import_id):
    print(import_id)
    res = get_citizens_for_import_id(import_id)
    res = jsonify(res)
    return res


def get_citizens_for_import_id(import_id):
    return {
        "data": [{
            "citizen_id": 1,
            "town": "Керчь",
            "street": "Иосифа Бродского",
            "building": "16к7стр5",
            "appartement": 7,
            "name": "Иванов Иван Иванович",
            "birth_date": "01.02.2000",
            "gender": "male",
            "relatives": [2]}, {
            "citizen_id": 2,
            "town": "Москва",
            "street": "Льва Толстого",
            "building": "16к7стр5",
            "appartement": 7,
            "name": "Иванов Иван Петрович",
            "birth_date": "01.02.2000",
            "gender": "male",
            "relatives": [1]}]
    }
@app.route('/imports/<int:import_id>/citizens/birthdays')
def get_citizens_birthdays(import_id):
    res = get_citizens_birthdays_for_import_id(import_id)
    res = jsonify(res)
    return res

def get_citizens_birthdays_for_import_id(import_id):
    return {"data": {
        "1": [{
            "citizen_id": 1,
            "presents": 20
            }],
        "2": [{
            "citizen_id": 2,
            "presents": 7
            }],
        "3": [],
        "12": [{
            "citizen_id": 3,
            "presents": 4
            },
        {
            "citizen_id": 8,
            "presents": 2}]
        }}

@app.route('/imports/<import_id>/towns/stat/percentile/age')
def get_statistic(import_id):
    print(import_id)
    res = get_statistic_for_import_id(import_id)
    res = jsonify(res)
    return res

def get_statistic_for_import_id(import_id):
    return {"data": [{
        "town": "Москва",
        "p50": 20,
        "p75": 45,
        "p99": 100
        },{
        "town": "Санкт-Петербург",
        "p50": 17,
        "p75": 35,
        "p99": 80
        }]}


    
 
#with app.test_request_context('/imports', method='POST'):
#    assert request.path == '/imports'
#    assert request.method == 'POST'
#    print("we are here")
#    print(request.form)
    



