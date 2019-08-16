import json
import requests
import datetime
from  numpy import percentile

"""
TODO: test with really big set (abou 10000) - can we insert data in one transaction - tested for 4000 for now
TODO: bad patch - test that nothing have been done
TODO: test more extensively situation with relative connection to themself
TODO: get import_id after insert from responese not from the head!!!!!!


TODO: make test with duplicate relatives
TODO:make test with citizen without relative and presents to buy

"""
def full_addr(path):
    addr = "http://127.0.0.1:5000"
    return addr + path

#tell server to initialise database
def post_init():
    path  = "/test"
    addr = full_addr(path)
    #print(addr)
    r = requests.post(addr, json = {'action':'init'})
    #print(r.status_code, r.reason)
    #print(r.text)
    
def init():
    post_init()
    
def get_test_file_as_structure(data_file):
    """
    Read structure from test file, which is used mostly to check returned values against
    Args:
        file (str): input file to read
    
    Returns:
        patch_structure (dict or list): json structure as dict or list
    """
    with open(data_file,'r') as json_file:
        patch_structure = json.load(json_file)
    return patch_structure

  
def post_data_set(data_set_file):
    """
    Request to insert data to db
    
    Args:
        data_set_file (str): file name that contains citizen set data as json
    
    Returns:
        (requests.Response): server’s response to a post request
    """
    with open(data_set_file,'r') as json_file:
        citizens_structure = json_file.read()
    
    path = "/imports"
    addr = full_addr(path)
    return requests.post(addr, data=citizens_structure, headers={'content-type': 'application/json'})

def patch(import_id, citizen_id, data_file):
    """
    Request to patch data in db
    
    Args:
        import_id (int): id of set of citiziens 
        citizen_id (int): id of citizen in set
        data_set_file (str): file name that contains citizen's data as json
    
    Returns:
        (requests.Response): server’s response to a patch request
        
    """
    with open(data_file,'r') as json_file:
        patch_structure = json_file.read()
    
    path =  "/imports/{}/citizens/{}".format(import_id, citizen_id)
    addr = full_addr(path)
    return requests.patch(addr, data=patch_structure, headers={'content-type': 'application/json'})

#get citizens tests
def get_citizens_set(import_id):
    """
    Request to get data set of citizens with id import_id
    
    Args:
        import_id (int): id of set of citiziens
    
    Returns:
        (requests.Response): server’s response to a get request
    """
    path =  "/imports/{}/citizens".format(import_id)
    addr = full_addr(path)
    return requests.get(addr)

def get_citizens_birthdays(import_id):
    """
    Request to get information about citizens' relatives' birthdays grouped by month in data set with id import_id
    
    Args:
        import_id (int): id of set of citiziens
        
    Returns:
        (requests.Response): server’s response to a get request
    """
    path =  "/imports/{}/citizens/birthdays".format(import_id)
    addr = full_addr(path)
    return requests.get(addr)

def get_percentile(citizen_structure):
    """
    Count percentiles for  50%, 75% and 99%  for age for citizens grouped by towns
    Args:
        citizen_structure (dict): citizens data_set
    
    Returns:
        (dict): percentiles for  50%, 75% and 99%  for age for citizens grouped by towns 
    """
    citizens_list = citizen_structure["citizens"]
    age_dict = dict()
    today = datetime.date.today()
    for citizen in citizens_list:
        date = citizen['birth_date']
        born = datetime.datetime.strptime(date, "%d.%m.%Y").date()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if citizen['town'] not in age_dict:
            age_dict[citizen['town']] = [age]
        else:
            age_dict[citizen['town']].append(age)
    data = list()
    for town in age_dict:
        ages = age_dict[town]
        perc_list = percentile(ages, [50, 75, 99], interpolation='linear')
        data.append({"town": town, "p50": perc_list[0], "p75": perc_list[1], "p99": perc_list[2]})
    return {"data": data}

def get_statistic(import_id):
    """
    Request to get percentiles for  50%, 75% and 99%  for age for citizens in set with import_id grouped by towns
    
    Args:
        import_id (int): id of set of citiziens
        
    Returns:
        (requests.Response): server’s response to a get request
    """
    path  = "/imports/{}/towns/stat/percentile/age".format(import_id)
    addr = full_addr(path)
    return requests.get(addr)
#=================================================================================================
#insertion tests
def test_good_input():
    init()
    r = post_data_set('test_files/simple_good_data_set.test')
    assert r.status_code == 201
    import_id = json.loads(r.text)['data']['import_id']
    assert import_id is not None
    r = get_citizens_set(import_id)
    data_for_insertion = get_test_file_as_structure('test_files/simple_good_data_set.test')["citizens"]
    got_data = json.loads(r.text)["data"]
    assert len(data_for_insertion) == len(got_data)
    for i in range(len(data_for_insertion)):
        assert data_for_insertion[i] == got_data[i]

def test_good_input_with_connection_to_self():
    init()
    r = post_data_set('test_files/simple_good_data_set_with_relative_connection_to_self.test')
    assert r.status_code == 201
    
def test_input_with_inconsistant_relatives():
    init()
    r = post_data_set('test_files/simple_inconsistant_relatives_set.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_absent_relatives():
    init()
    r = post_data_set('test_files/simple_absent_realtives_set.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_rubbish_in_place_of_date():
    init()
    r = post_data_set('test_files/simple_set_with_rubbish_in_place_of_date.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_wrong_date_format():
    init()
    r = post_data_set('test_files/simple_set_with_wrong_date_format.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404

def test_input_date_with_whitespaces():
    init()
    r = post_data_set('test_files/simple_set_date_with_whitespaces.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_tricky_wrong_date_format1():
    init()
    r = post_data_set('test_files/simple_set_with_tricky_wrong_date_format1.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_tricky_wrong_date_format2():
    init()
    r = post_data_set('test_files/simple_set_with_tricky_wrong_date_format2.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_trickier_wrong_date_format():
    init()
    r = post_data_set('test_files/simple_set_with_trickier_wrong_date_format.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404

def test_input_with_the_trickiest_wrong_date_format(): #it's not actually wrong, just 29.02 of some leap year
    init()
    r = post_data_set('test_files/simple_set_with_the_trickiest_wrong_date_format.test')
    assert r.status_code == 201

def test_input_with_wrong_geneder_format():
    init()
    r = post_data_set('test_files/simple_set_with_wrong_geneder_format.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_absent_key():
    init()
    r = post_data_set('test_files/simple_set_with_absent_key.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404

def test_input_with_extra_key():
    init()
    r = post_data_set('test_files/simple_set_with_extra_key.test')
    assert r.status_code == 400
        #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_wrong_structure():
    init()
    r = post_data_set( 'test_files/simple_set_wrong_structure.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_without_json_structure():
    init()
    r = post_data_set( 'test_files/simple_set_without_json_structure.test')
    assert r.status_code == 400
    
def test_input_with_non_unique_citizen_id():
    init()
    r = post_data_set('test_files/simple_set_with_non_unique_citizen_id.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404

def test_input_with_non_unique_relatives():
    init()
    r = post_data_set('test_files/simple_set_with_non_unique_relatives.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
    
def test_input_with_null_citizen_id():
    init()
    r = post_data_set('test_files/simple_set_with_null_citizen_id.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_null_town():
    init()
    r = post_data_set('test_files/simple_set_with_null_town.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_input_with_null_relatives():
    init()
    r = post_data_set('test_files//simple_set_with_null_relatives.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
#bigger insert tests
def test_good_bigger_input():
    init()
    r = post_data_set('test_files/good_data_set1.test')
    assert r.status_code == 201
    
def test_good_bigger_input():
    init()
    r = post_data_set('test_files/data_set_with_inconsistant_relatives1.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404
    
def test_good_bigger_input():
    init()
    r = post_data_set('test_files/data_set_with_absent_realtives1.test')
    assert r.status_code == 400
    #Test that nothing was inserted
    r = get_citizens_set(1)
    assert r.status_code == 404

#try to insert the bigest set for this time    
def test_good_and_big_input():
    init()
    r = post_data_set('test_files/good_and_big_set.test')
    assert r.status_code == 201


#=========================================================    
#tests for patch
def test_good_patch():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/good_patch.test')
    assert r.status_code == 200
    patch_data = get_test_file_as_structure('test_files/good_patch.test')
    got_data = json.loads(r.text)["data"]
    #test that data for citizen was updated
    for key in patch_data:
        assert patch_data[key] == got_data[key]
        
def test_good_patch_for_second_import():
    """
    Test that patch for 2-d import doesn't mess up with 1-t import
    """
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(2, 3, 'test_files/good_patch.test')
    assert r.status_code == 200
    patch_data = get_test_file_as_structure('test_files/good_patch.test')
    got_data = json.loads(r.text)["data"]
    #test that data for citizen 3 in 2-d import was updated
    for key in patch_data:
        assert patch_data[key] == got_data[key]
   
    #test that data for citizen 3 in 1-st import was not(!) updated
    insert_data = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    assert got_data == insert_data

def test_patch_bad_import_id():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(2, 3, 'test_files/good_patch.test')
    assert r.status_code == 404
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_bad_citizen_id():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = get_citizens_set(1)
    got_data1 = json.loads(r.text)["data"]
    r = patch(1, 4, 'test_files/good_patch.test')
    assert r.status_code == 404
    r = get_citizens_set(1)
    got_data2 = json.loads(r.text)["data"]
    assert got_data1 == got_data2 #data set should stay the same
    
def test_patch_bad_both_id():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(2, 4, 'test_files/good_patch.test')
    assert r.status_code == 404
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_no_keys():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_no_keys.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_extra_key():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_extra_key.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_wrong_structure():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_wrong_structure.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_with_non_unique_relatives():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_with_non_unique_relatives.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_relative_to_self():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_relative_to_self.test')
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_patch = get_test_file_as_structure('test_files/patch_relative_to_self.test')
    for key in data_for_patch:
        assert  got_data[key] == data_for_patch[key]
        
def test_patch_wrong_relative():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_wrong_relative.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_null_name():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_with_null_name.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
    
def test_patch_null_relatives():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_with_null_relatives.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion
 
def test_patch_bad_date():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = patch(1, 3, 'test_files/patch_bad_date.test')
    assert r.status_code == 400
    #check that nothing has changed
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    data_for_insertion = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    assert got_data == data_for_insertion

#================================
def test_get_citizens_valid_import_id():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = get_citizens_set(1)
    assert r.status_code == 200
    inserted_data = get_test_file_as_structure('test_files/data_set_to_patch_it.test')["citizens"]
    got_data = json.loads(r.text)["data"]
    assert len(inserted_data) == len(got_data)
    for i in range(len(inserted_data)):
        assert inserted_data[i] == got_data[i]

def test_get_citizens_invalid_import_id():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    r = get_citizens_set(2)
    assert r.status_code == 404
    
    
#====================================
#patch and get test
def test_patch_add_remove_relative():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    #add relative 1 for 3-d citizen
    r = patch(1, 3, 'test_files/patch_add_relative.test')
    assert r.status_code == 200
    #get data from bd for 3-d citizen and check thst she has 1-relative
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    assert got_data[2]['relatives'] == [1]
    #also check that first relative has new realtive 3
    assert sorted(got_data[0]['relatives']) == [2, 3]
    #remove relative 1 for 3-d citizen
    r = patch(1, 3, 'test_files/patch_remove_relative.test')
    assert r.status_code == 200
    r = get_citizens_set(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    assert got_data[2]['relatives'] == []
    assert sorted(got_data[0]['relatives']) == [2]
#=======================================
#birthdays (presents) test
def test_get_birthdays_valid_import_id():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    patch(1, 3, 'test_files/good_patch.test')
    r = get_citizens_birthdays(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    assert len(got_data) == 12
    expected_data = get_test_file_as_structure('test_files/birthdays_answer.test')["data"]
    assert got_data == expected_data

def test_get_birthdays_valid_import_id_several_imports():
    init()
    post_data_set('test_files/data_set_to_patch_it.test')
    post_data_set('test_files/data_set_to_patch_it.test')
    patch(2, 3, 'test_files/good_patch.test')
    r = get_citizens_birthdays(2)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    assert len(got_data) == 12
    expected_data = get_test_file_as_structure('test_files/birthdays_answer.test')["data"]
    assert got_data == expected_data
    
def test_multiple_birtdays_in_one_month():
    init()
    post_data_set('test_files/data_set_for_multiple_birtdays_in_one_month.test')
    r = get_citizens_birthdays(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    assert len(got_data) == 12
    expected_data = get_test_file_as_structure('test_files/birthdays_answer_multiple.test')["data"]
    assert got_data == expected_data
    
    
def test_get_birthdays_present_to_self():
    init()
    post_data_set('test_files/simple_good_data_set_with_relative_connection_to_self.test')
    r = get_citizens_birthdays(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    expected_data = get_test_file_as_structure('test_files/birthdays_answer_to_self.test')["data"]
    assert got_data == expected_data
    
    
def test_birtdays_invalid_import_id():
    init()
    post_data_set("test_files/data_set_for_multiple_birtdays_in_one_month.test")
    r = get_citizens_birthdays(2)
    assert r.status_code == 404
    
#================================================
#test percentile requests
def test_statistic_valid_import_id1():
    init()
    post_data_set('test_files/data_set_for_percentile1.test')
    r = get_statistic(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    expected_data = get_test_file_as_structure('test_files/answer_for_percentile1.test')["data"]
    assert len(got_data) == len(expected_data)
    assert got_data == expected_data #this one maybe works only if orders of lists are the same with is not for sure  
    
def test_statistic_valid_import_id2():
    #big test with automaticaly generated answer to compare with
    original_structure_for_percentile = get_test_file_as_structure('test_files/data_set_for_percentile2.test')
    init()
    post_data_set('test_files/data_set_for_percentile2.test')
    r = get_statistic(1)
    assert r.status_code == 200
    got_data = json.loads(r.text)["data"]
    expected_data = get_percentile(original_structure_for_percentile)["data"]
    assert len(got_data) == len(expected_data)
    assert got_data == expected_data #this one maybe works only if orders of lists are the same with is not for sure
    
def test_statistic_invalid_import_id():
    init()
    post_data_set('test_files/data_set_for_percentile1.test')
    r = get_statistic(2)
    assert r.status_code == 404
 
 
if __name__ == '__main__':
    test_good_input()
    







    
    




    
    

