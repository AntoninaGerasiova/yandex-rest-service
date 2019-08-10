from flask import Flask
from flask import current_app

from .models import db, Citizens, Imports, Kinships
from . import help_data


def insert_citizens_set(request_json):
    #validate json before parse it
    help_data.validate_insert_json(request_json)
    
    #parse json and get data to insert to db
    citizens_data, kinships_data = help_data.get_insert_data(request_json)
    
    citizen_len = len(citizens_data)
    kinship_len = len(kinships_data)
    
    
    import_obj = Imports()
    
    current_app.logger.info(import_obj.import_id)
    
    db.session.add(import_obj)
    db.session.commit()
    
    current_app.logger.info(import_obj.import_id)
    
    
    
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
        citizens_dict = {citizen.citizen_id: citizen.serialize() for citizen in citizens_responce}
        kinships_responce =  Kinships.query.filter_by(import_id=import_id_).all()
        for kinship in kinships_responce:
            citizen_id = kinship.citizen_id
            relative_id = kinship.relative_id
            citizens_dict[citizen_id]["relatives"].append(relative_id)
        print(citizens_dict)
        
    except Exception as e:
        session.rollback()
        raise
    return {"data":list(citizens_dict.values())}

    
    
