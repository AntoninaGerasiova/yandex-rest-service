"""
Help functions that perform data processing such as
    -   converting formats
    -   parsing jsons 
    -   validation jsons
    -   create handy structures to work with bd 

"""
import jsonschema
from dateutil.parser import parse
import datetime
#Json schemas
#json-schema to check input data json
schema_input = {
    "type": "object",
    "properties":{
        "citizens": {"type": "array",
                    "items": {"type":"object",
                              "required": ["citizen_id", "town", "street", "building", "apartment", "name", "birth_date", "gender", "relatives"],
                              "properties":{
                                  "citizen_id":{"type": "integer"},
                                  "town":{"type": "string"},
                                  "street":{"type": "string"},
                                  "building":{"type": "string"},
                                  "apartment":{"type": "integer"},
                                  "name":{"type": "string"},
                                  "birth_date":{"type": "string"},
                                  "gender":{"type": "string", "enum": ["male", "female"]},
                                  "relatives":{"type": "array", "items":{"type": "integer"}}
                                  
                                },
                              "additionalProperties": False
                              }
                    
                    }
        },
    "required": ["citizens"],
    "additionalProperties": False
}
#json-schema to check patch data json                              
schema_patch = {"type": "object",
                "anyOf":[
                    {"required": ["town"]},
                    {"required": ["street"]},
                    {"required": ["building"]},
                    {"required": ["apartment"]},
                    {"required": ["name"]},
                    {"required": ["birth_date"]},
                    {"required": ["gender"]},
                    {"required": ["relatives"]}],
                "properties":{
                    "town":{"type": "string"},
                    "street":{"type": "string"},
                    "building":{"type": "string"},
                    "apartment":{"type": "integer"},
                    "name":{"type": "string"},
                    "birth_date":{"type": "string"},
                    "gender":{"type": "string", "enum": ["male", "female"]},
                    "relatives":{"type": "array", "items":{"type": "integer"}}
                    },
                "additionalProperties": False}
                              

#help functions
def date_to_bd_format(date):
    """ 
    Convert date format to suitable for bd one
    
    Args: 
        date(str): date in original format that sould be "ДД.ММ.ГГГГ"
    
    Returns: 
        date(str): date suitable for db "YYYY-MM-DD"
        
    Raises:
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format
    """
    #Validate date format
    d,m,y = date.strip().split(".")
    if len(d) != 2 or len(m) != 2 or len(y) != 4:
        raise RuntimeError("Bad date format")
    bd_date = "-".join((y, m, d))
    parse(bd_date)
    return  datetime.datetime(int(y), int(m), int(d))
    
    
def date_to_output_format(date):
    """
    Convert data in format suitable for output
    
    Args: 
        date(str): date in format sutable for db "YYYY-MM-DD"
    
    Returns: 
        date(str): date in format "ДД.ММ.ГГГГ"
    """
    month = date.month if date.month >= 10 else "0" + str(date.month)
    day = date.day if date.day >= 10 else "0" + str(date.day)
    return "{}.{}.{}".format(day, month, date.year)


def get_age(date):
    """
    Convert date to age regarding current day
    
    Args: 
        date(str): date in format sutable for db "YYYY-MM-DD"
        
    Returns:
        (int): age
    """
    today = datetime.date.today()
    return today.year - date.year - ((today.month, today.day) < (date.month, date.day))
    
def validate_insert_json(request_json):
    """
    Validate insert data format
    
    Args:
        request_json (dict): citizens set in dict format
    
    Raises:
        jsonschema.exceptions.ValidationError: if request_json is not valid json
        json.decoder.JSONDecodeError: if request_json is of not required structure or values of request_json are of not valid types    
    
    """
    jsonschema.validate(request_json, schema_input)
    
def get_insert_data(request_json):
    """
    Unpack data from request_json structure
    
    Args:
        request_json (dict): citizens set in dict format
    
    Returns:
        citizens_data (list) : data about citizens formed for inserting in db (without information about kinship)
        kinships_data (list) : data about kinshps formed for inserting in db
        
    Raises:
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format
    """
   
    citizens = request_json["citizens"]
    citizens_data = list()
    kinships_data = set()
    kinship_set = set()
    for citizen in citizens:
        citizen_id = citizen['citizen_id']
        town = citizen['town']
        street = citizen['street']
        building = citizen['building']
        apartment = citizen['apartment']
        name = citizen['name']
        birth_date = date_to_bd_format(citizen['birth_date'])
        gender = citizen['gender']
        relatives = citizen['relatives']
        citizens_data.append([citizen_id, town, street, building, apartment, name, birth_date, gender])
        #Generate pairs of relatives for this citizen
        #For now just eliminate duplicates, but maybe we'd better should reject the whole request
        for relative in set(relatives):
            kinships_data.add((citizen_id, relative))
            #keep track of pairs of relatives - every one should has pair
            pair_in_order = (citizen_id, relative) if citizen_id < relative else (relative, citizen_id)
            if citizen_id != relative:
                if pair_in_order not in kinship_set:
                    kinship_set.add(pair_in_order)
                else: 
                    kinship_set.remove(pair_in_order)
    if  len(kinship_set) != 0:
        print ("Informationt about relatives inconsistant")
        raise RuntimeError("Inconsistant relatives data")
    return citizens_data, list(map(list, kinships_data))



def validate_patch_json(request_json):
    """
    Validate patch data
    
    Args:
        request_json (dict): data to change
    
    Raises:
        jsonschema.exceptions.ValidationError: if request_json is not valid json
        json.decoder.JSONDecodeError: if request_json is of not required structure or values of request_json are of not valid types
    """
    jsonschema.validate(request_json, schema_patch)
    
    
    
def get_new_relatives(import_id, citizen_id, request_json, citizen_ids):
    """
    Make pairs of relatives to add to kinships table
    
    Args:
        import_id (int): import id were to find citizen
        citizen_id (int):citizen id whose information to change
        request_json (dict): data to change
    
    Returns: 
        kinships_data (list): pairs of citizens' kinships to insert into table
    """

    kinships_data = set()
    
    for relative in request_json['relatives']:
        if relative not in citizen_ids:
            raise RuntimeError("Can't be relative to non-existant citizen")
        kinships_data.add((import_id, citizen_id, relative))
        if citizen_id != relative:
            kinships_data.add((import_id, relative, citizen_id))
                
    return list(kinships_data)














    
    
