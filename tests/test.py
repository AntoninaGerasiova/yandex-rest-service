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
    #print(r.status_code, r.reason)
    #print(r.text)

#insertion tests    
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
    
def test_input_several_sets():
    init()
    r = post_data_set('simple_good_data_set')
    import_id1 = json.loads(r.text)["data"]["import_id"]
    
    r = post_data_set('simple_good_data_set')
    import_id2 = json.loads(r.text)["data"]["import_id"]
    
    assert import_id1 + 1 == import_id2
    #try to insert set for with insertion begins but should be rolled back
    r = post_data_set('simple_set_with_non_unique_citizen_id')
    r = post_data_set('simple_good_data_set')
    import_id3 = json.loads(r.text)["data"]["import_id"]
    assert import_id2 + 1 == import_id3
    
#=========================================================    
#tests for patch
def patch(import_id, citizen_id, data_file):
    with open(data_file,'r') as json_file:
        patch_structure = json_file.read()
    print(patch_structure)

    path =  "/imports/{}/citizens/{}".format(import_id, citizen_id)
    addr = full_addr(path)
    
    return requests.patch(addr, data=patch_structure, headers={'content-type': 'application/json'})
    #print(r.status_code, r.reason)
    #print(r.text)
    
def test_good_patch():
    init()
    r = post_data_set('data_set_to_patch_it.test')
    #print(r.status_code, r.reason)
    #print(r.text)
    r = patch(1, 3, 'good_patch.test')
    assert r.status_code == 200
    #print(r.status_code, r.reason)
    #print(r.text)

def test_patch_bad_import_id():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(2, 3, 'good_patch.test')
    assert r.status_code == 400
    
def test_patch_bad_citizen_id():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(1, 4, 'good_patch.test')
    assert r.status_code == 400
    
def test_patch_bad_both_id():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(2, 4, 'good_patch.test')
    assert r.status_code == 400
    
def test_patch_no_keys():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(1, 3, 'patch_no_keys.test')
    assert r.status_code == 400
    
def test_patch_extra_key():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(1, 3, 'patch_extra_key.test')
    assert r.status_code == 400
    
def test_patch_wrong_structure():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(1, 3, 'patch_wrong_structure.test')
    assert r.status_code == 400
    
def test_patch_relative_to_self():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(1, 3, 'patch_relative_to_self.test')
    assert r.status_code == 200
    
def test_patch_wrong_relative():
    init()
    post_data_set('data_set_to_patch_it.test')
    r = patch(1, 3, 'patch_wrong_relative.test')
    assert r.status_code == 200




    
    

