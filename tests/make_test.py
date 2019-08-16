import random
import datetime
import itertools
import json
"""
For making test-files with json-structures used by tests

Attributes:
    TOWNS_NUM_FOR_SET (int): Number of different cities in autogenerated set
    STREETS_NUM_FOR_SET (int): Number of different streets in autogenerated sets
    MAX_BUILDING (int): Maximum building number in  autogenerated sets
    MAX_CORPUS (int): Maximum corpus number in  autogenerated sets
    MAX_STROENIE (int): Maximum stroenie number in  autogenerated sets
    MAX_APARTMENT (int): Maximum apartment number in  autogenerated sets
    MIN_RELATIVE_TO_MESS (int): Minumum non-mutual relatives to make generated set inconsistant regarding relatives
    MAX_RELATIVE_TO_MESS (int): Maximum non-mutual relatives to make generated set inconsistant regarding relatives
    MIN_YEAR (int): Minimum year for date generation
    MAX_YEAR (int): Maximum year for date generation
    
"""
TOWNS_NUM_FOR_SET = 3 
STREETS_NUM_FOR_SET = 40 
MAX_BUILDING = 60 
MAX_CORPUS = 10 
MAX_STROENIE = 10 
MAX_APARTMENT = 150 
MIN_RELATIVE_TO_MESS = 20 
MAX_RELATIVE_TO_MESS = 20
MIN_YEAR = 1950
MAX_YEAR = 2007


def get_titles_from_file(file_name):
    """
    Read titles (for ex. names, towns) from file
    
    Args:
        file_name(str): file containing titles one for string
        
    Returns:
        content (list): list of titles stripped off white-spaces
    """
    with open(file_name,"r") as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

#===================================================      
#Get titles from files
#Use this list as globale that maybe not the best idea
men = get_titles_from_file("men.txt")
women = get_titles_from_file("women.txt")
towns = get_titles_from_file("towns.txt")
streets = get_titles_from_file("streets.txt")
#====================================================

def generate_date():
    """
        Generate random date between MIN_YEAR and MAX_YEAR years
        
        Returns:
            (str): date in format "ДД.ММ.ГГГГ"
    """
    date =  datetime.datetime.strptime('{} {}'.format(random.randint(1, 365), random.randint(MIN_YEAR, MAX_YEAR)), '%j %Y').date()
    month = date.month if date.month >= 10 else "0" + str(date.month)
    day = date.day if date.day >= 10 else "0" + str(date.day)
    return "{}.{}.{}".format(day, month, date.year)


def generate_building():
    """
        Generate random building number which may or may not include "к_" or "стр_" sabstrings
        (str): number of corpus
    """
    building = str(random.randint(1, MAX_BUILDING))
    if random.random() < 0.3:
        building += "к{}".format(random.randint(1, MAX_CORPUS))
    if random.random() < 0.2:
        building += "стр{}".format(random.randint(1, MAX_STROENIE))
    return building

def make_relative_pairs(citizens_num, num_pairs):
    """
        Generate pairs which represents relationships
        
        Args:
            citizens_num (int): number of citizens - effecrively the number for which combinatios generated
            num_pairs(int): requiered quantity of realative connections
            
        Note: 
            No args verification privided,  num_pairs sould be reasonable regarding citizens_num
            
        Returns:
            (list) : pairs represents mutual relative connections (that is pair (1,2) tells that citizens 1 and 2 are relatives to each other)

    """
    # Generate all possible non-repeating pairs
    pairs = list(itertools.combinations(range(1,citizens_num+1), 2))
    
    # Randomly shuffle these pairs
    random.shuffle(pairs)
    return pairs[:num_pairs]
    
def write_data_set_to_file(data_set, output_file):
    """
        Write data_set to file as json_structure
        
        Args:
            data_set(dict or list): structure to wrte to output_file
            output_file (str): output file 
            
    """
    with open(output_file, 'w') as f:
        json.dump(data_set, f, indent = 4)
        
def write_raw_to_file(raw_data, output_file):
    """
        Write raw_data to file as it is
        Args: 
            raw_data (str): effectively some string to wrte to file 
            output_file (str): output file
    """
    with open(output_file, 'w') as f:
        f.write(raw_data)

def make_good_set(citizens_num, relatives_pairs, seed=None):
    """
    Generate good data set
    
    Args:
        citizens_num (int): Number of citizens in set
        relatives_pairs (int): Number of relatives pairs of citizens
        seed (int) : seed to fix process of randomization to get the same data set every time (default None)
        
    Returns:
        citizens_structure(dict): good set of citizens data as structure of requiered format 
    """
    if seed is not None:
        random.seed(seed)
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
        citizen_dict['birth_date'] =  generate_date()
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
    

def make_set_with_inconsistant_relatives(citizens_num, relatives_pairs, seed=None):
    """
        Generate test data with not mutual relative connections - server should reject it
        
        Args: 
            citizens_num (int): Number of citizens in set
            relatives_pairs (int): Approximate number of relatives pairs of citizens
            seed (int) : seed to fix process of randomization to get the same data set every time (default None)
        Returns:
            citizens_structure(dict): set of citizens data conteining non-mutual relative connections
            
    """
    citizens_structure = make_good_set(citizens_num, relatives_pairs, seed)
    citizens_data = citizens_structure['citizens']
    relatives_to_mess = random.randint(MIN_RELATIVE_TO_MESS, MAX_RELATIVE_TO_MESS) 
    #just add some random relatives to random citizens - they are not likely to be mutual
    for _ in range(relatives_to_mess):
        i = random.randint(1, citizens_num)
        j = random.randint(1, citizens_num)
        #it can be situation when i == j, and that's valid to be relative to self, but it's not very likely
        #and we have several attempts to mess data set anyway
        citizens_data[i - 1]['relatives'].append(j)
    return citizens_structure
            
            

def make_set_with_absent_realtives(citizens_num, relatives_pairs, seed=None):
    """ Generate data set  where relatives includes non existant citizens - server should reject it
        Args: 
            citizens_num (int): Approximate number of citizens in set (actually can be less)
            relatives_pairs (int): Approximate number of relatives pairs of citizens
            seed (int) : seed to fix process of randomization to get the same data set every time (default None)
        Returns:
            citizens_structure(dict): set of citizens data conteining relative connections with non-existant citizens
        
    """
    citizens_structure = make_good_set(citizens_num, relatives_pairs, seed)
    citizens_data = citizens_structure['citizens']
    citizen_whose_relative_to_delete = random.randint(0, citizens_num)
    #delete relative of some citizens
    for relative in   citizens_data[citizen_whose_relative_to_delete]['relatives']:
        citizens_data.pop(relative - 1)
    return citizens_structure
        
    
#=========================================================================================================
#insertion tests
#Rather costly generation, do not run every time
"""good_data_set = make_good_set(99, 200)
write_data_set_to_file(good_data_set, 'test_files/good_data_set1.test')
data_set_with_inconsistant_relatives = make_set_with_inconsistant_relatives(99, 200)
write_data_set_to_file(data_set_with_inconsistant_relatives, 'test_files/data_set_with_inconsistant_relatives1.test')
data_set_with_absent_realtives = make_set_with_absent_realtives(99, 200)
write_data_set_to_file(data_set_with_absent_realtives, 'test_files/data_set_with_absent_realtives1.test')"""
"""good_and_big_data_set = make_good_set(4000, 8000)
write_data_set_to_file(good_and_big_data_set, 'test_files/good_and_big_set.test')"""

write_raw_to_file("It's not even json structure", "test_files/simple_set_without_json_structure.test")

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_good_data_set.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1, 2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_good_data_set_with_relative_connection_to_self.test')

birthdays_answer_connection_to_self  = {
    "data": {
        "1": [],
        "2": [
                {
                    "citizen_id":1,
                    "presents": 2,
                },
                {
                    "citizen_id":2,
                    "presents": 1,
                }
            ],
        "3": [],
        "4": [],
        "5": [],
        "6": [],
        "7": [],
        "8": [],
        "9": [],
        "10": [],
        "11": [],
        "12": []
        }
    }
                
write_data_set_to_file(birthdays_answer_connection_to_self , "test_files/birthdays_answer_to_self.test")


write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': []}]},'test_files/simple_inconsistant_relatives_set.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2, 28]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_absent_realtives_set.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': 'rubish', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_set_with_rubbish_in_place_of_date.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '2000.01.03', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_set_with_wrong_date_format.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000 ', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_set_date_with_whitespaces.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '61.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_set_with_tricky_wrong_date_format1.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.32.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_set_with_tricky_wrong_date_format2.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '31.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_set_with_trickier_wrong_date_format.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '29.02.2016', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_set_with_the_trickiest_wrong_date_format.test')

#very exclusive test
write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'not known', 'relatives': [1]}]}, 'test_files/simple_set_with_wrong_geneder_format.test')

write_data_set_to_file({'citizens': [{'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]},'test_files/simple_set_with_absent_key.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'wage': '2000USD', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_set_with_extra_key.test')

write_data_set_to_file([{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}], 'test_files/simple_set_wrong_structure.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}, {'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_set_with_non_unique_citizen_id.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2, 2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_set_with_non_unique_relatives.test')

write_data_set_to_file({'citizens': [{'citizen_id': None, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_set_with_null_citizen_id.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': None, 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files/simple_set_with_null_town.test')

write_data_set_to_file({'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': None }, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'apartment': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}, 'test_files//simple_set_with_null_relatives.test')


#======================================================
#patch tests

test_insert_for_patch = {"citizens": [
    {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2] },
    {"citizen_id": 2,"town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "name": "Иванов Сергей Иванович", "birth_date": "17.04.1997","gender": "male","relatives": [1] },
    {"citizen_id": 3, "town": "Керчь", "street": "Иосифа Бродского", "building": "2", "apartment": 11, "name": "Романова Мария Леонидовна", "birth_date": "23.11.1986", "gender": "female", "relatives": []}]
}

write_data_set_to_file(test_insert_for_patch, 'test_files/data_set_to_patch_it.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1]}, 'test_files/good_patch.test')

write_data_set_to_file({}, 'test_files/patch_no_keys.test')

write_data_set_to_file({"citizen_id": 3, "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1]}, 'test_files/patch_extra_key.test')

write_data_set_to_file({"citizens":[{ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1]}]}, 'test_files/patch_wrong_structure.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [3]}, 'test_files/patch_relative_to_self.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [6]}, 'test_files/patch_wrong_relative.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1, 1]}, 'test_files/patch_with_non_unique_relatives.test')

write_data_set_to_file({ "name": None, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": [1]}, 'test_files/patch_with_null_name.test')

write_data_set_to_file({ "name": "Иванова Мария Леонидовна", "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "relatives": None }, 'test_files/patch_with_null_relatives.test')

write_data_set_to_file({ "birth_date": "31.02.2000"}, 'test_files/patch_bad_date.test')

write_data_set_to_file({"relatives": [1]}, 'test_files/patch_add_relative.test')
write_data_set_to_file({"relatives": []}, 'test_files/patch_remove_relative.test')

#======================================================
#tests for birtdays request
birthdays_answer  = {
    "data": {
        "1": [],
        "2": [],
        "3": [],
        "4": 
            [
                {
                    "citizen_id":1,
                    "presents": 1,
                }
            ],
        "5": [],
        "6": [],
        "7": [],
        "8": [],
        "9": [],
        "10": [],
        "11": 
            [
                {
                    "citizen_id": 1,
                    "presents": 1
                }
            ],
        "12": 
            [
                {
                    "citizen_id": 2,
                    "presents": 1
                },
                {
                    "citizen_id": 3,
                    "presents": 1
                }
            ]
    }
}
                
write_data_set_to_file(birthdays_answer, "test_files/birthdays_answer.test")

#test for several relatives with birthsday in one month
#we have there twins with birthdays in one month who are both brothers to "Иванов Иван Иванович" who compeled to buy two presents in April
#in case you wondering why twins have different day of birth well...it was long labor in the night
test_insert_multiple_birthdays = {"citizens": [
    {"citizen_id": 1, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "name": "Иванов Иван Иванович", "birth_date": "26.12.1986", "gender": "male", "relatives": [2,3,4]},
    {"citizen_id": 2,"town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "name": "Иванов Сергей Иванович", "birth_date": "17.04.1997","gender": "male","relatives": [1,4] },
    {"citizen_id": 3, "town": "Керчь", "street": "Иосифа Бродского", "building": "2", "apartment": 11, "name": "Романова Мария Леонидовна", "birth_date": "23.11.1986", "gender": "female", "relatives": [1]},
    {"citizen_id": 4, "town": "Москва", "street": "Льва Толстого", "building": "16к7стр5", "apartment": 7, "name": "Иванов Артём Иванович", "birth_date": "18.04.1997", "gender": "male", "relatives": [1,2] },
    ]
}

write_data_set_to_file(test_insert_multiple_birthdays, "test_files/data_set_for_multiple_birtdays_in_one_month.test")

#answer for multiple birthdays
birthdays_answer_multiple  = {
    "data": {
        "1": [],
        "2": [],
        "3": [],
        "4": 
            [
                {
                    "citizen_id":1,
                    "presents": 2,
                },
                {
                    "citizen_id":2,
                    "presents": 1,
                },
                {
                    "citizen_id":4,
                    "presents": 1,
                }
                
                
            ],
        "5": [],
        "6": [],
        "7": [],
        "8": [],
        "9": [],
        "10": [],
        "11": 
            [
                {
                    "citizen_id": 1,
                    "presents": 1
                }
            ],
        "12": 
            [
                {
                    "citizen_id": 2,
                    "presents": 1
                },
                {
                    "citizen_id": 3,
                    "presents": 1
                },
                {
                    "citizen_id": 4,
                    "presents": 1
                }
            ]
    }
}
                
write_data_set_to_file(birthdays_answer_multiple, "test_files/birthdays_answer_multiple.test")

#============================================================
#percentile tests
write_data_set_to_file(test_insert_multiple_birthdays, 'test_files/data_set_for_percentile1.test')

#!!! Not sure about such direct testing with existing answer as this information inevitably will be staled 
#it won't happen during the  August though, so only this small test will do, others answers are created in process of testing
percentile_answer = { 
    "data": [
        {
            "town": "Москва",
            "p50": 22.,
            "p75": 27.,
            "p99": 31.8
        },
        {
            "town": "Керчь",
            "p50": 32.,
            "p75": 32.,
            "p99": 32.
        }
    ]
}

write_data_set_to_file(percentile_answer, 'test_files/answer_for_percentile1.test')

citizen_structure = make_good_set(99, 200, seed=3)
write_data_set_to_file(citizen_structure, 'test_files/data_set_for_percentile2.test')















    
