
def isNull(param) -> bool:
    if type(param) == str:
        return param == ''
    elif type(param) == list:
        return len(param) == 0
    elif type(param) == dict:
        return len(param) == 0
    elif type(param) == int:
        return param == 0
    elif type(param) == float:
        return param == 0.0
    elif type(param) == bool:
        return param == False
    else:
        return param is None

def isNotNull(param)  -> bool:
    return not isNull(param)

