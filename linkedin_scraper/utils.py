import json
import calendar

def obj_to_dict(obj):
    exclude_words = ["driver", "lock"]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    elif isinstance(obj, list):
        return [obj_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            # Excluye keys que contienen palabras excluidas
            if any(word in k for word in exclude_words) or k.startswith("_"):
                print(f"Excluyendo atributo/clave: {k}")
                continue
            out[k] = obj_to_dict(v)
        return out
    elif hasattr(obj, "__dict__"):
        out = {}
        for k, v in vars(obj).items():
            if any(word in k for word in exclude_words) or k.startswith("_"):
                print(f"Excluyendo atributo/clave: {k}")
                continue
            out[k] = obj_to_dict(v)
        return out
    else:
        return obj
        
def instance_to_dict(instance):
    instance_dict = {}
    for key, value in instance.__dict__.items():
        instance_dict[key] = obj_to_dict(value)
    return instance_dict

def parse_date(date_str):
    """Convert 'Apr 2017' or 'January 2021' to {'month': 4, 'year': 2017}, else None."""
    if not date_str or date_str.strip() in ['Present', '', 'present']:
        return date_str
    date_str = date_str.strip()
    # Ignore things like '3 yrs', '1 yr 5 mos', etc.
    if any(word in date_str.lower() for word in ['yr', 'mos', 'years', 'months']):
        return None
    months = {month: index for index, month in enumerate(calendar.month_abbr) if month}
    months.update({month: index for index, month in enumerate(calendar.month_name) if month})
    parts = date_str.split()
    if len(parts) == 2:
        month_str, year_str = parts
        try:
            month_num = months.get(month_str[:3], 0)
            year_num = int(year_str)
            return {'month': month_num, 'year': year_num}
        except Exception:
            return None
    elif len(parts) == 1:
        try:
            return {'month': None, 'year': int(parts[0])}
        except Exception:
            return None
    else:
        return None
