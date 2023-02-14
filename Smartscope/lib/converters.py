import functools

def list_to_dict(data):
    output = dict()
    for i in data:
        output[i['id']] = i
    return output

def isnull_to_none(value):
    return None if value == 'null' else value

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))