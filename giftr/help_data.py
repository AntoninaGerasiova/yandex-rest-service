"""help functions to work with data
parsing json,  validation
"""
import jsonschema
from dateutil.parser import parse
schema_input = {
    "type": "object",
    "properties":{
        "citizens": {"type": "array",
                    "items": {"type":"object",
                              "required": ["citizen_id", "town", "street", "building", "appartement", "name", "birth_date", "gender", "relatives"],
                              "properties":{
                                  "citizen_id":{"type": "integer"},
                                  "town":{"type": "string"},
                                  "street":{"type": "string"},
                                  "building":{"type": "string"},
                                  "appartement":{"type": "integer"},
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
                              
#help functions
def date_to_bd_format(date):
    """ get data in format suitable for bd format"""
    #Validate date format
    d,m,y = date.split(".")
    if len(d) != 2 or len(m) != 2 or len(y) != 4:
        raise Exception("Bad data format")
    bd_date = "-".join((y, m, d))
    parse(bd_date)
    return  bd_date
    
    
def date_to_output_format(date):
    """get data in format suitable for output"""
    month = date.month if date.month >= 10 else "0" + str(date.month)
    day = date.day if date.day >= 10 else "0" + str(date.day)
    return "{}.{}.{}".format(day, month, date.year)
    
def get_insert_data(request_json):
    """Unpack data from request_json structure
    Args:
        crequest_json (dict): citizens set in dict format
    Returns:
        citizens_data (list) : data about citizens formed for inserting in db (without information about kinship)
        kinships_data (list) : data about kinshps formed for inserting in db
        
    Raises:
    Exception: if relatives links are inconsistant
    """
    #validate schema before parse it
    jsonschema.validate(request_json, schema_input)
    
    citizens = request_json["citizens"]
    citizens_data = list()
    kinships_data = list()
    kinship_set = set()
    for citizen in citizens:
        citizen_id = citizen['citizen_id']
        town = citizen['town']
        street = citizen['street']
        building = citizen['building']
        appartement = citizen['appartement']
        name = citizen['name']
        birth_date = date_to_bd_format(citizen['birth_date'])
        gender = citizen['gender']
        relatives = citizen['relatives']
        citizens_data.append([citizen_id, town, street, building, appartement, name, birth_date, gender])
        #Generate pairs of relatives for this citizen
        #For now just eliminate duplicates, but maybe we'd better should reject the whole request
        for relative in set(relatives):
            kinships_data.append([citizen_id, relative])
            #keep track of pairs of relatives - every one should has pair
            if citizen_id != relative:
                pair_in_order = (citizen_id, relative) if citizen_id < relative else (relative, citizen_id)
                if pair_in_order not in kinship_set:
                    kinship_set.add(pair_in_order)
                else: 
                    kinship_set.remove(pair_in_order)
    if  len(kinship_set) != 0:
        print ("Informationt about relatives inconsistant")
        raise Exception("Inconsistant relatives data")
    return citizens_data, kinships_data











    
    
