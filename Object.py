
def inspect(objType, obj = None):
    if obj == None:
        return "#" + objType
    elif isinstance(obj, object):
        return "#" + objType + "<" + str(obj.__dict__) + ">"
    else:
        return "#" + objType + "<" + str(obj) + ">"

def find(list, condition):
    return next((x for x in list if condition(x)), None)
