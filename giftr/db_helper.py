from flask import Flask
from flask import current_app
from sqlalchemy import text

from  numpy import percentile

from .models import db, Citizens, Imports, Kinships
from . import help_data

"""
TODO: Citizens.query vs Citizen.session.query
TODO:undestand more about how to use session, when to commit, when start transaction manually
TODO: mayby try to rif of plain sql completly but it's not requiered
"""
def trace():
    from inspect import currentframe, getframeinfo
    cf = currentframe()
    print('>>>>> TRACE: {}:{}'.format(getframeinfo(cf).filename, cf.f_back.f_lineno))

def insert_citizens_set(request_json):
    """ 
    Insert set of citizens data to db
    
    Args:
        crequest_json (dict): data about citizens to insert
    
    Returns:
        import_id (int):  import_id if insert is succesively completed
    
    Raises:
        jsonschema.exceptions.ValidationError: if request_json is not valid json
        json.decoder.JSONDecodeError: if request_json is not of required structure or values of request_json are not of valid types
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format
        db.Error: if something went wrong during insertion in db
        
    """
    
    #validate json before parse it
    help_data.validate_insert_json(request_json)
    
    #parse json and get data to insert to db
    citizens_data, kinships_data = help_data.get_insert_data(request_json)
    
    citizen_len = len(citizens_data)
    kinship_len = len(kinships_data)
    
    import_obj = Imports()
    #get unique import number import_id
    try:
        db.session.add(import_obj)
        db.session.commit()
    except Exception as e:
        session.rollback()
        raise
    current_app.logger.info(import_obj.import_id)
    
    
    #add import_id to inserted data
    citizen_data_with_import_id = list(map(list.__add__, [[import_obj.import_id]]*citizen_len, citizens_data))
    kinship_data_with_import_id = list(map(list.__add__, [[import_obj.import_id]]*kinship_len, kinships_data))
    citizens_dicts = [dict(zip(Citizens.get_keys(), sublist)) for sublist in citizen_data_with_import_id]
    kinsip_dicts = [dict(zip(Kinships.get_keys(), sublist)) for sublist in kinship_data_with_import_id]
    try:
        db.session.execute(Citizens.__table__.insert(), citizens_dicts)
        db.session.execute(Kinships.__table__.insert(), kinsip_dicts)
        db.session.commit()
    except Exception as e:
        session.rollback()
        raise
    return import_obj.import_id


def get_citizens_set(import_id_):
    """
    Get set of citizens with certain import_id
    
    Args:
        import_id (int): import id of set to get
    
    Returns:
        dict: information about citizens of set with import_id
        
    Raises:
        Exception: when there is no set with given import_id in db
    """
    try:
        citizens_responce = Citizens.query.filter_by(import_id=import_id_).all()
        current_app.logger.info(citizens_responce)
        if not citizens_responce:
            raise Exception("import with import_id = {} does not exist".format(import_id_))
        citizens_dict = {citizen.citizen_id: citizen.serialize() for citizen in citizens_responce}
        kinships_responce =  Kinships.query.filter_by(import_id=import_id_).all()
        for kinship in kinships_responce:
            citizen_id = kinship.citizen_id
            relative_id = kinship.relative_id
            citizens_dict[citizen_id]["relatives"].append(relative_id)
            if citizen_id != relative_id:
                citizens_dict[relative_id]["relatives"].append(citizen_id)
    except Exception as e:
        raise
    return {"data":list(citizens_dict.values())}


def fix_data(import_id_, citizen_id_, request_json):
    """
    Updete information about citizen with given import_id and citizen_id
        
    Args:
        import_id (int): import id  of set  where citizen is
        citizen_id (int):citizen id whose information to change
        request_json (dict): data to update
    
    Returns:
        res(dict):    Updated information about citizen
    
    Raises:
        jsonschema.exceptions.ValidationError: if request_json is not valid json
        json.decoder.JSONDecodeError: if request_json is of not required structure or values of request_json are of not valid types
        ValueError: in case of wrong date 
        Exception: if relatives links are inconsistant or if date string isn't of "ДД.ММ.ГГГГ" format or if citizen with  given import_id, citizen_id not in base or if somthing get wrong during work with bd
    """

    #validate request_json
    help_data.validate_patch_json(request_json)
    
    # if we have to change realatives extract all new relative connections from request_json
    if "relatives" in request_json:
        update_relatives = True
        #Get citizen_id-s of citizens that existant in set with import_id
        citizen_ids = Citizens.query.with_entities(Citizens.citizen_id).filter_by(import_id=import_id_).all()
        citizen_ids = set(citizen_id for t in citizen_ids for citizen_id in t)
        kinships_data = help_data.get_new_relatives(import_id_, citizen_id_, request_json, citizen_ids)
    
    #we need not information about relatives anynore - get rid of it 
    request_json.pop("relatives", None)

    try:
        #update relatives in necessary  - delete all relative pairs contains citizen_id_ boss as Kinships.citizen_id and as Kinships.relative_id and add new pairs of relative connections if there are any
        if update_relatives:
            Kinships.query.filter_by(import_id=import_id_, citizen_id=citizen_id_).delete()
            Kinships.query.filter_by(import_id=import_id_, relative_id=citizen_id_).delete()
            if kinships_data:
                kinsip_dicts = [dict(zip(Kinships.get_keys(), sublist)) for sublist in kinships_data]
                db.session.execute(Kinships.__table__.insert(), kinsip_dicts)
        #update all other data if it is necessary
        if len(request_json):
            citizen = Citizens.query.filter_by(import_id=import_id_, citizen_id=citizen_id_).first()
            citizen.patch(**request_json)
        
        db.session.commit()
    except Exception as e:
        session.rollback()
        raise
    
    #get information that we have changed: it can be different from what we expected in case of parrallel work with db (if somebody managed to change the same data too before we get responce), but this information would reflect the newest state of the base and the base will be consistant anyway (patch is atomic)
    citizen = Citizens.query.filter_by(import_id=import_id_, citizen_id=citizen_id_).first().serialize()
    kinships_response = Kinships.query.with_entities(Kinships.relative_id).filter_by(import_id=import_id_, citizen_id=citizen_id_).all()
    kinships_response_mutual = Kinships.query.with_entities(Kinships.citizen_id).filter_by(import_id=import_id_, relative_id=citizen_id_).all()
    kinships_ids = set(id for t in kinships_response for id in t)
    kinships_mutual_ids = set(id for t in kinships_response_mutual for id in t)
    kinships_ids = kinships_ids.union(kinships_mutual_ids)
    for id in kinships_ids:
        citizen['relatives'].append(id)
        
    return {"data":citizen}

def get_citizens_birthdays_for_import_id(import_id_):
    """
    Get information about relatives' birthdays grouped by mothes
    
    Args:
        import_id (int): import_id for which get such information
    
    Returns:
        (dict):    information about relatives' birthdays grouped by monthes
        
    Raises:
        Exception:  if set with import_id doesn't exist in db
    """
    
    #may be not to keep mutuall connection in bas was not such a good idea
    #get information for birthdays two times
    #first get information for citizens with citizen_id in kinships table
    #second get informtion for citizens with relative_id in kinships table
    sql_get_kins_birtmonth = '''SELECT citizens.citizen_id as citizen_id,
    strftime("%m", (SELECT  birth_date FROM citizens WHERE citizen_id = relative_id and citizens.import_id = :import_id_val)) as birth_month,
    count(citizens.citizen_id) as presents
    FROM citizens, kinships  
    WHERE citizens.citizen_id = kinships.citizen_id and citizens.import_id = kinships.import_id and citizens.import_id = :import_id_val
    GROUP BY citizens.citizen_id, birth_month
    '''
    sql = text(sql_get_kins_birtmonth)
    
    birthdays_1 = db.session.execute(sql, {'import_id_val': import_id_}).fetchall()
    
    sql_get_kins_birtmonth = '''SELECT citizens.citizen_id as citizen_id,
    strftime("%m", (SELECT  birth_date FROM citizens WHERE citizen_id = kinships.citizen_id and citizens.import_id = :import_id_val)) as birth_month,
    count(citizens.citizen_id) as presents
    FROM citizens, kinships  
    WHERE citizens.citizen_id = kinships.relative_id and kinships.relative_id <> kinships.citizen_id and citizens.import_id = kinships.import_id and citizens.import_id = :import_id_val
    GROUP BY citizens.citizen_id, birth_month
    '''
    sql = text(sql_get_kins_birtmonth)
    birthdays_2 = db.session.execute(sql, {'import_id_val': import_id_}).fetchall()

    if (not birthdays_1) and not(birthdays_2): 
        raise Exception("import with import_id = {} does not exist".format(import_id_))
    
    #use both responces to gather information about birthdays together
    print(birthdays_1)
    print(birthdays_2)
    birthdays_1.extend(birthdays_2)
    result_dict  = {"1": [], "2": [], "3": [], "4": [],  "5": [], "6": [], "7":[],  "8": [], "9": [], "10": [], "11": [], "12": []}
    
    for birthday_row in birthdays_1:
        key = str(int(birthday_row["birth_month"]))
        result_dict[key].append({
            "citizen_id": birthday_row["citizen_id"],
            "presents": birthday_row["presents"]
            })
        
    return {"data":result_dict}
    
    
        
        

def get_statistic_for_import_id(import_id_):
    """
        Count percentiles for  50%, 75% and 99%  for age for citizens grouped by towns for given import_id (particular import)
        
        Args:
            import_id (int): import_id for which get such information
        
        Returns:
            (dict):   percentiles for  50%, 75% and 99%  for age for citizens grouped by towns formed as requaired structure 
            
        Raises:
            Exception:  if set with import_id doesn't exist in db
    """
    citizens = Citizens.query.with_entities(Citizens.town, Citizens.birth_date).filter_by(import_id=import_id_).all()
    if not citizens: 
        raise Exception("import with import_id = {} does not exist".format(import_id))
    
    age_dict = dict()
    for citizen in citizens:
        key = citizen.town
        
        if key not in age_dict:
            age_dict[key] = [help_data.get_age(citizen.birth_date)]
        else:
            age_dict[key].append(help_data.get_age(citizen.birth_date))
        
        
    data = list()
    for town in age_dict:
        ages = age_dict[town]
        perc_list = percentile(ages, [50, 75, 99], interpolation='linear')
        data.append({"town": town, "p50": perc_list[0], "p75": perc_list[1], "p99": perc_list[2]})
    
    return {"data": data}
    
    
    
    
    
    

    
    
