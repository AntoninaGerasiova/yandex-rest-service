import random
import datetime
import itertools
import json
TOWNS_NUM_FOR_SET = 3
STREETS_NUM_FOR_SET = 40
MAX_BUILDING = 60
MAX_CORPUS = 10
MAX_STROENIE = 10
MAX_APARTMENT = 150

MIX_RELATIVE_TO_MESS = 20
MAX_RELATIVE_TO_MESS = 20

def get_titles_from_file(file_name):
    with open(file_name,"r") as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

def generate_data():
    date =  datetime.datetime.strptime('{} {}'.format(random.randint(1, 365), random.randint(1950, 2007)), '%j %Y').date()
    month = date.month if date.month >= 10 else "0" + str(date.month)
    day = date.day if date.day >= 10 else "0" + str(date.day)
    return "{}.{}.{}".format(day, month, date.year)


def generate_building():
    building = str(random.randint(1, MAX_BUILDING))
    if random.random() < 0.3:
        building += "к{}".format(random.randint(1, MAX_CORPUS))
    if random.random() < 0.2:
        building += "стр{}".format(random.randint(1, MAX_STROENIE))
    return building

def make_relative_pairs(citizens_num, num_pairs):
    # Generate all possible non-repeating pairs
    pairs = list(itertools.combinations(range(1,citizens_num+1), 2))
    
    # Randomly shuffle these pairs
    random.shuffle(pairs)
    return pairs[:num_pairs]
    
def write_data_set_to_file(data_set, output_file): 
    with open(output_file, 'w') as f:
        json.dump(data_set, f, indent = 4)

def make_good_set(citizens_num, relatives_pairs):
    """
    Make good data set
    Args:
        citizens_num (int): Number of citizens in set
        relatives_pairs (int): Number of relatives pair of citizens
    """
    men_num = int(citizens_num*0.5)
    women_num = citizens_num - men_num
    men_idx = random.sample(range(len(men)), men_num)
    women_idx = random.sample(range(len(women)), women_num)
    men_list = list(zip(map(men.__getitem__, men_idx), ["male"]*men_num))
    women_list = list(zip(map(women.__getitem__, women_idx), ["female"]*women_num))
    citizens_names = men_list + women_list
    random.shuffle(citizens_names)
    
    towns_idx = random.sample(range(len(towns)), TOWNS_NUM_FOR_SET)
    towns_list = list(map(towns.__getitem__, towns_idx))
    
    streets_idx = random.sample(range(len(streets)), STREETS_NUM_FOR_SET)
    streets_list = list(map(streets.__getitem__, streets_idx))
    
    citizens_data = list()
    for i in range(citizens_num):
        citizen_dict = {'citizen_id': i + 1}
        citizen_dict['town'] = random.choice(towns_list) 
        citizen_dict['street'] = random.choice(streets_list)
        citizen_dict[ 'building'] = generate_building()
        citizen_dict[ 'apartment'] = random.randint(1, MAX_APARTMENT)
        citizen_dict['name'] =citizens_names[i][0]
        citizen_dict['birth_date'] =  generate_data()
        citizen_dict['gender'] = citizens_names[i][1]
        citizen_dict['relatives'] = list() 
        citizens_data.append(citizen_dict)
    
    pairs = make_relative_pairs(citizens_num, relatives_pairs)
    for pair in pairs:
        i = pair[0] - 1
        j = pair[1] - 1
        citizens_data[i]['relatives'].append(pair[1])
        citizens_data[j]['relatives'].append(pair[0])
    citizens_structure = {'citizens':citizens_data}
    return citizens_structure
    

def make_set_with_inconsistant_relatives(citizens_num, relatives_pairs):
    """
        Generate test data with not mutual kinship - server should reject it
    """
    citizens_structure = make_good_set(citizens_num, relatives_pairs)
    citizens_data = citizens_structure['citizens']
    relatives_to_mess = random.randint(MIX_RELATIVE_TO_MESS, MAX_RELATIVE_TO_MESS) 
    #just add some random relative to rendom citizens - they are not likely to be mutual
    for _ in range(relatives_to_mess):
        i = random.randint(1, citizens_num)
        j = random.randint(1, citizens_num)
        #it can be situation when i == j, and that's valid to be relative to self, but it's not very likely
        #and we have several tryals to mess data set anyway
        citizens_data[i - 1]['relatives'].append(j)
    return citizens_structure
            
            

def make_set_with_absent_realtives(citizens_num, relatives_pairs):
    """ Generate data set  where relatives includes non existant citizens - server should reject it"""
    citizens_structure = make_good_set(citizens_num, relatives_pairs)
    citizens_data = citizens_structure['citizens']
    citizen_whose_relative_to_delete = random.randint(0, citizens_num)
    #delete relative of some citizens
    for relative in   citizens_data[citizen_whose_relative_to_delete]['relatives']:
        citizens_data.pop(relative - 1)
    return citizens_structure
        
    
      
men = get_titles_from_file("men.txt")
women = get_titles_from_file("women.txt")
towns = get_titles_from_file("towns.txt")
streets = get_titles_from_file("streets.txt")

#====================================================
#insertion tests
#good_data_set = make_good_set(99, 200)
#write_data_set_to_file(good_data_set, 'good_data_set1')
#data_set_with_inconsistant_relatives = make_set_with_inconsistant_relatives(99, 200)
#write_data_set_to_file(data_set_with_inconsistant_relatives, 'data_set_with_inconsistant_relatives1')
#data_set_with_absent_realtives = make_set_with_absent_realtives(99, 200)
#write_data_set_to_file(data_set_with_absent_realtives, 'data_set_with_absent_realtives1')


write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'simple_good_data_set')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1, 2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_good_data_set_with_relative_connection_to_self')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': []}]},'simple_inconsistant_relatives_set')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2, 28]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_absent_realtives_set')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': 'rubish', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'simple_set_with_rubbish_in_place_of_date')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '2000.01.03', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_set_with_wrong_date_format')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '61.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_set_with_tricky_wrong_date_format1')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.32.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_set_with_tricky_wrong_date_format2')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '31.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_set_with_trickier_wrong_date_format')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '29.02.2016', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_set_with_the_trickiest_wrong_date_format')

#very exclusive test
write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'not known', 'relatives': [1]}]}, 'simple_set_with_wrong_geneder_format')


write_data_set_to_file({'citizens': [{'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'simple_set_with_absent_key')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'wage': '2000USD', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'simple_set_with_extra_key')


write_data_set_to_file([{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}], 'simple_set_wrong_structure')


citizens_structure = {'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}, {'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'simple_set_with_non_unique_citizen_id')

#====================
#patch tests

test_insert_for_patch = {"citizens": [
    {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2] },
    {"citizen_id": 2,"town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "name": "Иванов Сергей Иванович", "birth_date": "17.04.1997","gender": "male","relatives": [1] },
    {"citizen_id": 3, "town": "Керчь", "street": "Иосифа Бродского", "building": "2", "apartment": 11, "name": "Романова Мария Леонидовна", "birth_date": "23.11.1986", "gender": "female", "relatives": []}]
}

write_data_set_to_file(test_insert_for_patch, 'data_set_to_patch_it.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1]}, 'good_patch.test')

write_data_set_to_file({}, 'patch_no_keys.test')

write_data_set_to_file({"citizen_id": 3, "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1]}, 'patch_extra_key.test')

write_data_set_to_file({"citizens":[{ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1]}]}, 'patch_wrong_structure.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [3]}, 'patch_relative_to_self.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [6]}, 'patch_wrong_relative.test')

write_data_set_to_file({"relatives": [1]}, 'patch_add_relative.test')
write_data_set_to_file({"relatives": []}, 'patch_remove_relative.test')
#============================















    
