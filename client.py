import json
import requests


ADDRESS = "http://127.0.0.1:5000"
def post_data_set():
    citizens_structure = {'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}

    #citizens_json = json.dumps(citizens_structure, indent = 4)
    #print(citizens_json)

    path = "/imports"
    addr = ADDRESS + path
    
    r = requests.post(addr, json=citizens_structure)

    print(r.status_code, r.reason)
    print(r.text)
    

def patch(import_id, citizen_id):
    patch_structure = {"town": "Керчь",
                       "street": "Иосифа Бродского"}

    path =  "/imports/{}/citizens/{}".format(import_id, citizen_id)
    addr = ADDRESS + path
    
    r = requests.patch(addr, json=patch_structure)
    print(r.status_code, r.reason)
    print(r.text)
    
def get_data_set(import_id):
    path =  "/imports/{}/citizens".format(import_id)
    addr = ADDRESS + path
    print(addr)

    r = requests.get(addr)
    print(r.status_code, r.reason)
    print(r.text)
    
    
if __name__ == "__main__":
    #post_data_set()
    #patch(6, 1)
    get_data_set(6)
        
