import json
import requests

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
    
def post_data_set(data_set_file):
    with open(data_set_file,'r') as json_file:
        citizens_structure = json.load(json_file)
        #citizens_structure = json_file.read()
    
    #print(citizens_structure)
    path = "/imports"
    addr = full_addr(path)
    #print(addr)
    r = requests.post(addr, json=citizens_structure)

    print(r.status_code, r.reason)
    print(r.text)

def test_input():
    init()
    post_data_set( 'good_data_set1')

if __name__ == "__main__":
    test_input()
    
    
