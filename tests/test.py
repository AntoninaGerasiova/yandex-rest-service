import json
import requests

def full_addr(path):
    addr = "http://127.0.0.1:5000"
    return addr + path

"initialize data base"
def init():
    path  = "/test"
    addr = full_addr(path)
    #print(addr)
    r = requests.post(addr, json = {'action':'init'})
    print(r.status_code, r.reason)
    print(r.text)
    
def post_data_set(data_set_file):
    with open(data_set_file,'r') as json_file:
        citizens_structure = json_file.read()
    
    #print(repr(citizens_structure))
    path = "/imports"
    addr = full_addr(path)
    return requests.post(addr, data=citizens_structure, headers={'content-type': 'application/json'})


def test_good_input():
    init()
    r = post_data_set('simple_good_data_set')
    assert r.status_code == 201

def test_good_input_with_connection_to_self():
    init()
    r = post_data_set('simple_good_data_set_with_relative_connection_to_self')
    assert r.status_code == 201    

def test_input_with_inconsistant_relatives():
    init()
    r = post_data_set('simple_inconsistant_relatives_set')
    assert r.status_code == 400
    
def test_input_with_absent_relatives():
    init()
    r = post_data_set('simple_absent_realtives_set')
    assert r.status_code == 400
    
def test_input_with_rubbish_in_place_of_date():
    init()
    r = post_data_set('simple_set_with_rubbish_in_place_of_date')
    assert r.status_code == 400
    
def test_input_with_wrong_date_format():
    init()
    r = post_data_set('simple_set_with_wrong_date_format')
    assert r.status_code == 400
    
def test_input_with_tricky_wrong_date_format1():
    init()
    r = post_data_set('simple_set_with_tricky_wrong_date_format1')
    assert r.status_code == 400
    
def test_input_with_tricky_wrong_date_format2():
    init()
    r = post_data_set('simple_set_with_tricky_wrong_date_format2')
    assert r.status_code == 400
    
def test_input_with_trickier_wrong_date_format():
    init()
    r = post_data_set('simple_set_with_trickier_wrong_date_format')
    assert r.status_code == 400

def test_input_with_the_trickiest_wrong_date_format():
    init()
    r = post_data_set('simple_set_with_the_trickiest_wrong_date_format')
    assert r.status_code == 201

def test_input_with_wrong_geneder_format():
    init()
    r = post_data_set('simple_set_with_wrong_geneder_format')
    #print(r.status_code, r.reason)
    #print(r.text)
    assert r.status_code == 400
    
def test_input_with_absent_key():
    init()
    r = post_data_set('simple_set_with_absent_key')
    assert r.status_code == 400

def test_input_with_extra_key():
    init()
    r = post_data_set('simple_set_with_extra_key')
    assert r.status_code == 400
    
def test_input_wrong_structure():
    init()
    r = post_data_set( 'simple_set_wrong_structure')
    assert r.status_code == 400
    
def test_input_without_json_structure():
    init()
    r = post_data_set( 'simle_set_without_json_structure')
    assert r.status_code == 400
    
def test_input_with_non_unique_citizen_id():
    init()
    r = post_data_set('simple_set_with_non_unique_citizen_id')
    assert r.status_code == 400
    


#TODO тест с вставкой нескольких сетов
