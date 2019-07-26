import random
import datetime
import itertools
import json
TOWNS_NUM_FOR_SET = 3
STREETS_NUM_FOR_SET = 40
MAX_BUILDING = 60
MAX_CORPUS = 10
MAX_STROENIE = 10
MAX_APPARTMENT = 150
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
    
    

def make_good_set(citizens_num, relatives_pairs, output_file):
    """
    Make good data set
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
        citizen_dict[ 'appartement'] = random.randint(1, MAX_APPARTMENT)
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
    with open(output_file, 'w') as f:
        json_structure = json.dump(citizens_structure, f, indent = 4)
    
men = get_titles_from_file("men.txt")
women = get_titles_from_file("women.txt")
towns = get_titles_from_file("towns.txt")
streets = get_titles_from_file("streets.txt")


make_good_set(99, 200, 'good_data_set1')



citizens_structure = {'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2, 28]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}


    
