from datetime import datetime as dt


def extract_date_from_json(dict:dict) -> dt.date:
    if dict is None:
        return None
    
    year = int(dict.get('year', {}).get('value', ''))
    
    month = dict.get('month', {})
    if month is None:
        month = 1
    else:
        month = int(month.get('value', ''))
    
    day = dict.get('day', {})
    if day is None:
        day = 1
    else:
        day = int(day.get('value', ''))
    
    return dt(year=year, month=month, day=day).date()