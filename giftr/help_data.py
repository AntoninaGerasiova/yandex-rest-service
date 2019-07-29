"""help functions to work with data
parsing json,  validation
"""
import jsonschema

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
citizens_structure = {'citizens': [{'citizen_id': 1, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}

citizens_structure = {'citizens': [{'citizen_id': 1,'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Иванович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [2]}, {'citizen_id': 2, 'town': 'Москва', 'street': 'Льва Толстого', 'building': '16к7стр5', 'appartement': 7, 'name': 'Иванов Иван Петрович', 'birth_date': '01.02.2000', 'gender': 'male', 'relatives': [1]}]}

try:
    jsonschema.validate(citizens_structure, schema_input)
    print("passed")
except jsonschema.exceptions.ValidationError as e:
    print("well-formed but invalid JSON:", e)
except json.decoder.JSONDecodeError as e:
    print("poorly-formed text, not JSON:", e)








    
    
