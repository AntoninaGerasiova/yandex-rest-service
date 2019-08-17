"""
interaction with db through FLask-SQLAlchemy
"""
from flask import current_app
from sqlalchemy import extract
from sqlalchemy import exc

from numpy import percentile

from .models import db, Citizens, Imports, Kinships
from .exceptions import SetNotFoundError, DBError
from . import help_data

import time


def trace():
    from inspect import currentframe, getframeinfo
    cf = currentframe()
    print('>>>>> TRACE: {}:{}'.format(getframeinfo(cf).filename, cf.f_back.f_lineno))


def insert_citizens_set(request_json):
    """ 
    Insert set of citizens data to db
    
    Args:
        request_json (dict): data about citizens to insert
    
    Returns:
        import_id (int):  import_id if insert is successfully completed
    
    Raises:
        InvalidJSONError: if request_json is not valid json or values of request_json are not of valid types
        exc.SQLAlchemyError: if something get wrong during work with db
        InconsistentRelativesError: if relatives are inconsistent
        NonUniqueRelativeError: if relatives for one citizens are not unique
        BadDateFormatError: if date string isn't of "ДД.ММ.ГГГГ" format or have whitespace characters in the beginning
        or the end of the string or if date is not valid
    """
    start = time.time()
    # validate json before parse it
    help_data.validate_insert_json(request_json)
    print("TIME VALIDATION: ", time.time() - start)

    # parse json and get data to insert to db
    start = time.time()
    citizens_data, kinships_data = help_data.get_insert_data(request_json)
    print("TIME CREATE DATA: ", time.time() - start)
    citizen_len = len(citizens_data)
    kinship_len = len(kinships_data)

    import_obj = Imports()
    try:
        # get unique import number import_id
        db.session.add(import_obj)
        db.session.flush()
        import_id = import_obj.import_id
        # add import_id to citizens data and insert citizens' data to db
        start = time.time()
        citizen_data_with_import_id = list(map(list.__add__, [[import_id]] * citizen_len, citizens_data))
        citizens_dicts = [dict(zip(Citizens.get_keys(), sublist)) for sublist in citizen_data_with_import_id]
        print("TIME PREPARE DATA CITIZEN: ", time.time() - start)
        start = time.time()
        db.session.execute(Citizens.__table__.insert(), citizens_dicts)
        print("INSERT DATA CITIZEN: ", time.time() - start)
        # do the same with kinships' data if there is at least one relativw connection for set
        if kinship_len > 0:
            start = time.time()
            kinship_data_with_import_id = list(map(list.__add__, [[import_id]] * kinship_len, kinships_data))
            kinship_dicts = [dict(zip(Kinships.get_keys(), sublist)) for sublist in kinship_data_with_import_id]
            print("TIME PREPARE DATA RELATIVES: ", time.time() - start)
            start = time.time()
            db.session.execute(Kinships.__table__.insert(), kinship_dicts)
            print("INSERT DATA RELATIVES: ", time.time() - start)
        start = time.time()
        db.session.commit()
        print("COMMIT: ", time.time() - start)
    except exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.info("Error during insertion")
        raise (DBError("Error during insertion"))

    return import_id


def get_citizens_set(import_id_):
    """
    Get set of citizens with certain import_id
    
    Args:
        import_id_ (int): import id of set to get
    
    Returns:
        dict: information about citizens of set with import_id
        
    Raises:       
        SetNotFoundError:  if set with import_id doesn't exist in db
    """
    # get citizens' set with id import_id_ info
    citizens_responce = Citizens.query.filter_by(import_id=import_id_).all()
    # responce souldn't be empty - raise exception
    if not citizens_responce:
        current_app.logger.info("import with import_id = {} does not exist".format(import_id_))
        raise (SetNotFoundError("import with import_id = {} does not exist".format(import_id_)))
    # create responce for client without relative connections
    citizens_dict = {citizen.citizen_id: citizen.serialize() for citizen in citizens_responce}
    # get information  about relatives
    kinship_response = Kinships.query.filter_by(import_id=import_id_).all()
    # add relative connections to response
    for kinship in kinship_response:
        citizen_id = kinship.citizen_id
        relative_id = kinship.relative_id
        citizens_dict[citizen_id]["relatives"].append(relative_id)
    return {"data": list(citizens_dict.values())}


def fix_data(import_id_, citizen_id_, request_json):
    """
    Updete information about citizen with given import_id and citizen_id
        
    Args:
        import_id_ (int): import id  of set  where citizen is
        citizen_id_ (int):citizen id whose information to change
        request_json (dict): data to update
    
    Returns:
        res(dict):    Updated information about citizen
    
    Raises:
        InvalidJSONError: if request_json is not valid json
        
        BadDateFormatError: if date string isn't of "ДД.ММ.ГГГГ" format or have whitespace characters in the
        beginning or the end of the string or if date is not valid
        
        NonUniqueRelativeError: if relatives ids not unique for one citizen
        
        RelativesToNonexistentCitizenError: if there are no citizen with given id to be relativ
        
        SetNotFoundError: in case if there are no set with id import_id_ or there are no citizen with id citizen_id_
        in it
        
        DBError: if something get wrong during work with db 
    """
    # check if there are set import_id_ in db in there are citizen citizen_id_ in this set
    citizen = Citizens.query.filter_by(import_id=import_id_, citizen_id=citizen_id_).first()
    if not citizen:
        current_app.logger.info(
            "citizen with import_id = {} and citizen_id = {} does not exist".format(import_id_, citizen_id_))
        raise (SetNotFoundError(
            "citizen with import_id = {} and citizen_id = {} does not exist".format(import_id_, citizen_id_)))

    # validate request_json
    help_data.validate_patch_json(request_json)

    # if we have to change relatives extract all new relative connections from request_json
    update_relatives = False
    if "relatives" in request_json:
        update_relatives = True
        # Get citizen_id-s of citizens that existent in set with import_id - to test if any relatives in patch data
        # are non-existent
        citizen_ids = Citizens.query.with_entities(Citizens.citizen_id).filter_by(import_id=import_id_).all()
        citizen_ids = set(citizen_id for t in citizen_ids for citizen_id in t)
        # for new relative pairs
        kinship_data = help_data.get_new_relatives(import_id_, citizen_id_, request_json, citizen_ids)

    # we don't need  information about relatives anymore - get rid of it 
    request_json.pop("relatives", None)

    # check data format and change it to db format
    if "birth_date" in request_json:
        request_json["birth_date"] = help_data.date_to_db_format(request_json["birth_date"])

    # update citizen info
    try:
        # update relatives if necessary  - delete all relative pairs contains citizen_id_ both as Kinships.citizen_id
        # and as Kinships.relative_id and add new pairs of relative connections if there are any
        if update_relatives:
            Kinships.query.filter_by(import_id=import_id_, citizen_id=citizen_id_).delete()
            Kinships.query.filter_by(import_id=import_id_, relative_id=citizen_id_).delete()
            if kinship_data:
                kinship_dicts = [dict(zip(Kinships.get_keys(), sublist)) for sublist in kinship_data]
                db.session.execute(Kinships.__table__.insert(), kinship_dicts)
        # update other data if it is necessary
        if len(request_json):
            citizen = Citizens.query.filter_by(import_id=import_id_, citizen_id=citizen_id_).first()
            citizen.patch(**request_json)
        # get information that we have changed
        citizen = Citizens.query.filter_by(import_id=import_id_, citizen_id=citizen_id_).first().serialize()
        kinship_response = Kinships.query.with_entities(Kinships.relative_id).filter_by(import_id=import_id_,
                                                                                        citizen_id=citizen_id_).all()
        kinship_ids = [relative_id for t in kinship_response for relative_id in t]
        for relative_id in kinship_ids:
            citizen['relatives'].append(relative_id)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
        current_app.logger.info(
            "Error during patch citizen with import_id = {} and citizen_id = {}".format(import_id_, citizen_id_))
        raise (DBError(
            "Error during patch citizen with import_id = {} and citizen_id = {}".format(import_id_, citizen_id_)))
    return {"data": citizen}


def get_citizens_birthdays_for_import_id(import_id_):
    """
    Get information about relatives' birthdays grouped by mothes
    
    Args:
        import_id_ (int): import_id for which get such information
    
    Returns:
        (dict):    information about relatives' birthdays grouped by monthes
        
    Raises:
        SetNotFoundError: if set with import_id doesn't exist in db
    """
    # test that citizens' set with id import_id_ exists
    citizens_response = Citizens.query.filter_by(import_id=import_id_).all()
    # response shouldn't be empty - raise exception
    if not citizens_response:
        current_app.logger.info("import with import_id = {} does not exist".format(import_id_))
        raise (SetNotFoundError("import with import_id = {} does not exist".format(import_id_)))

    # get response composed of pairs (citizen, month) and number of presents he have to bay in this month
    birthdays = (db.session.query(Citizens)
                 .join(Kinships, (Kinships.relative_id == Citizens.citizen_id))
                 .filter(Citizens.import_id == import_id_, Kinships.import_id == import_id_)
                 .with_entities(Kinships.citizen_id.label('giver'),
                                extract('month', Citizens.birth_date).label('birth_month'),
                                db.func.count(Citizens.citizen_id).label('presents'))
                 .group_by('giver', 'birth_month').all())

    # form a structure to return
    result_dict = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": [], "11": [],
                   "12": []}

    for birthday in birthdays:
        key = str(int(birthday.birth_month))
        result_dict[key].append({
            "citizen_id": birthday.giver,
            "presents": birthday.presents
        })

    return {"data": result_dict}


def get_statistic_for_import_id(import_id_):
    """
    Count percentiles for  50%, 75% and 99%  for age for citizens grouped by towns for given import_id (particular
    import)
        
    Args:
        import_id_ (int): import_id for which get such information
        
    Returns:
        (dict):   percentiles for  50%, 75% and 99%  for age for citizens grouped by towns formed as required structure
            
    Raises:
        SetNotFoundError:  if set with import_id doesn't exist in db
    """
    # get town and birth_date about every citizen in set
    citizens = Citizens.query.with_entities(Citizens.town, Citizens.birth_date).filter_by(import_id=import_id_).all()
    # shouldn't be empty
    if not citizens:
        current_app.logger.info("import with import_id = {} does not exist".format(import_id_))
        raise (SetNotFoundError("import with import_id = {} does not exist".format(import_id_)))

    # form response
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
        percentile_list = percentile(ages, [50, 75, 99], interpolation='linear')
        data.append({"town": town, "p50": percentile_list[0], "p75": percentile_list[1], "p99": percentile_list[2]})

    return {"data": data}
