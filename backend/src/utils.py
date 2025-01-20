def find(element, json):
    """https://stackoverflow.com/a/31033676/9089233"""
    """ Find a value in a nested dictionary by specifying a path to the value """
    keys = element.split(".")
    rv = json
    for key in keys:
        if key not in rv:
            return None
        rv = rv[key]
    return rv


def update(element, json: dict, value):
    """Update a value in a nested dictionary by specifying a path to the value"""
    keys = element.split(".")
    rv = json
    for key in keys:
        if key == keys[-1]:
            rv[key] = value
            break
        elif key not in rv:
            rv[key] = {}
        rv = rv[key]
    return json
