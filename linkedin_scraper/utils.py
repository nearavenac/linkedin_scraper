import json

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
