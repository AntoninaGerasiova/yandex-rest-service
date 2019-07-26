import json
import requests

"""{
            "data": [{
                "citizen_id": 1,
                "town": "Керчь",
                "street": "Иосифа Бродского",
                "building": "16к7стр5",
                "appartement": 7,
                "name": "Иванов Иван Иванович",
                "birth_date": "01.02.2000",
                "gender": "male",
                "relatives": [2, 28]}, {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "appartement": 7,
                "name": "Иванов Иван Петрович",
                "birth_date": "01.02.2000",
                "gender": "male",
                "relatives": [1]}]
}""" 
def full_addr(path):
    addr = "http://127.0.0.1:5000"
    return addr + path

"initialize data base"
def init():
    path  = "/test"
    addr = full_addr(path)
    print(addr)
    r = requests.post(addr, json = {'action':'init'})
    print(r.status_code, r.reason)
    print(r.text)
    

def post_data_set():
    citizens_structure = {'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2, 28]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}

    #citizens_json = json.dumps(citizens_structure, indent = 4)
    #print(citizens_json)

    path = "/imports"
    addr = full_addr(path)
    
    r = requests.post(addr, json=citizens_structure)

    print(r.status_code, r.reason)
    print(r.text)
    

def patch(import_id, citizen_id):
    patch_structure = {"town": "Керчь",
                       "street": "Иосифа Бродского",
                       "relatives": [2, 27]}

    path =  "/imports/{}/citizens/{}".format(import_id, citizen_id)
    addr = full_addr(path)
    
    r = requests.patch(addr, json=patch_structure)
    print(r.status_code, r.reason)
    print(r.text)
    
def get_citizens_set(import_id):
    path =  "/imports/{}/citizens".format(import_id)
    addr = full_addr(path)
    print(addr)

    r = requests.get(addr)
    print(r.status_code, r.reason)
    print(r.text)

def get_citizens_birthdays(import_id):
     path =  "/imports/{}/citizens/birthdays".format(import_id)
     addr = full_addr(path)
     print(addr)
     r = requests.get(addr)
     print(r.status_code, r.reason)
     print(r.text)
    

def get_statistic(import_id):
        path  = "/imports/{}/towns/stat/percentile/age".format(import_id)
        addr = full_addr(path)
        print(addr)
        r = requests.get(addr)
        print(r.status_code, r.reason)
        print(r.text)




if __name__ == "__main__":
    init()
    post_data_set()
    post_data_set()
    patch(1, 1)
    get_citizens_set(1)
    get_citizens_set(2)
    get_citizens_birthdays(1)
    #get_statistic(1)
    
        
