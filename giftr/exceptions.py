"""
User-defined exceptions
"""


class SetNotFoundError(Exception): 
    """
    Exception thrown when there no required set of users or no required user in the required set
    """
    def __init__(self, value): 
        self.value = value 
  
    def __str__(self): 
        return repr(self.value)
    
    
class BadFormatError(Exception):
    """ Superclass for user-defined exceptions related to problems with client data"""
    
    def __init__(self, value): 
        self.value = value 
  
    def __str__(self): 
        return repr(self.value)
    

class BadDateFormatError(BadFormatError):
    """Bad date format"""
    

class NonUniqueRelativeError(BadFormatError):
    """More then one relative with the same id"""
    

class InconsistentRelativesError(BadFormatError):
    """Not all relative connections are mutual"""    
    

class RelativesToNonexistentCitizenError(BadFormatError):
    """Can't be relative to non-existent citizen"""
    

class InvalidJSONError(BadFormatError):
    """
        if request_json is not valid json 
        if request_json is of not required structure or values of request_json are of not valid types
    """
    

class DBError(Exception):
    """ 
        Exception thrown when something wrong has happened during working with db
    """
    def __init__(self, value): 
        self.value = value 
  
    def __str__(self): 
        return repr(self.value)

