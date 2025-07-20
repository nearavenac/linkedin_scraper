import json

def obj_to_dict(obj):
    # Si el objeto tiene .to_dict(), úsalo
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    # Si el objeto tiene __dict__ (es normal en clases simples)
    elif hasattr(obj, "__dict__"):
        return vars(obj)
    # Si es una lista, procesa cada elemento
    elif isinstance(obj, list):
        return [obj_to_dict(item) for item in obj]
    # Si es un tipo nativo, devuélvelo directo
    else:
        return obj
        
def instance_to_dict(instance):
    instance_dict = {}
    for key, value in instance.__dict__.items():
        instance_dict[key] = obj_to_dict(value)
    return instance_dict
