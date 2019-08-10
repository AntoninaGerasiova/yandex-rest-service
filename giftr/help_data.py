"""
Help functions to work with data, convert formats, parsing json, validation

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
        raise Exception("Bad date format")
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
            pair_in_order = (citizen_id, relative) if citizen_id < relative else (relative, citizen_id)
            kinships_data.add(pair_in_order)
            #keep track of pairs of relatives - every one should has pair
            if citizen_id != relative:
                if pair_in_order not in kinship_set:
                    kinship_set.add(pair_in_order)
                else: 
                    kinship_set.remove(pair_in_order)
    if  len(kinship_set) != 0:
        print ("Informationt about relatives inconsistant")
        raise Exception("Inconsistant relatives data")
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
    
    
    
def get_new_relatives(import_id, citizen_id, request_json):
    """
    Make pairs of relatives to add to kinships table
    
    Args:
        import_id (int): import id were to find citizen
        citizen_id (int):citizen id whose information to change
        request_json (dict): data to change
    
    Returns: 
        kinships_data (list): pairs of citizens' kinships to insert into table
    """

    kinships_data = list()
    
    for relative in request_json['relatives']:
            kinships_data.append([import_id, citizen_id, relative])
            if citizen_id != relative:
                kinships_data.append([import_id, relative, citizen_id])
                
    return kinships_data


def form_request(import_id, citizen_id, request_json):
    """
    Make update request to update information about citizen with distinct citizen_id and request_id (except relative field)
    
    Args:
        import_id (int): import id were to find citizen
        citizen_id (int):citizen id whose information to change
        request_json (dict): data to change
    
    Returns: 
        sql_update_citizen (str) :sql-request ready to use to update bd (may be not very safe??? but provided the json structure was checkced it will do)
    
    Raises:
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format
    """
    
    #check if there are keys except relatives and if there are no just return - nothing to patch in citizens table
    key_list = list(request_json.keys())
    key_list.remove('relatives')
    if not key_list:
        return
    #make request to update information (except relative field)
    sql_update_citizen = "UPDATE citizens SET "
    
    #go through keys explicitly
    if "town" in request_json:
        town = request_json['town']
        sql_update_citizen += "town = '{}', ".format(town)
        
    if "street" in request_json:
        street = request_json['street']
        sql_update_citizen += "street = '{}', ".format(street)
    
    if "building" in request_json:
        building = request_json['building']
        sql_update_citizen += "building = '{}', ".format(building)
        
    if "apartment" in request_json:
        apartment = request_json['apartment']
        sql_update_citizen += "apartment = {}, ".format(apartment)
        
    if "name" in request_json:
        name = request_json['name']
        sql_update_citizen += "name = '{}', ".format(name)
    
    if "birth_date" in request_json:
        birth_date = date_to_bd_format(request_json['birth_date'])
        sql_update_citizen += "birth_date = {}, ".format(birth_date)
        
    if "gender" in request_json:
        gender = request_json['gender']
        sql_update_citizen += "gender = '{}', ".format(gender)
        
    sql_update_citizen = sql_update_citizen[:-2] + " WHERE import_id = {} and citizen_id = {}".format(import_id, citizen_id)
    return sql_update_citizen











    
    
