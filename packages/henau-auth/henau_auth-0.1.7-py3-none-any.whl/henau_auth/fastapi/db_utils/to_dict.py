from playhouse.shortcuts import model_to_dict
from peewee import ModelSelect, Model


def to_dict(obj, **kewargs):
    if isinstance(obj, Model):
        return model_to_dict(obj, **kewargs)
    elif isinstance(obj, dict):
        return {k: to_dict(v, **kewargs) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(item, **kewargs) for item in obj]
    elif isinstance(obj, ModelSelect):
        return [to_dict(item, **kewargs) for item in obj]
    else:
        return obj
