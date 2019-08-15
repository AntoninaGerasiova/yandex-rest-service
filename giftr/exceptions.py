class SetNotFoundError(Exception): 
  
    def __init__(self, value): 
        self.value = value 
  
    def __str__(self): 
        return(repr(self.value))
    
    
class BadFormatError(Exception):
    """ Supercalss for user-defined exceptions related to prblems with cilent data"""
    
    def __init__(self, value): 
        self.value = value 
  
    def __str__(self): 
        return(repr(self.value))
    
class BadDateFormatError(BadFormatError): 
    """Bad date format"""
    
class NonUniqueRelativeError(BadFormatError): 
    """More then one relative with the same id"""
    
class InconsistentRelativesError(BadFormatError):
    """Not all relative connections are mutual"""
    
class RelativesToNonexistantCitizenError(BadFormatError):
    """Can't be relative to non-existant citizen"""    

