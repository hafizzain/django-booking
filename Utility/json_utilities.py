import json


def format_json_string(data):
    if type(data) == str:
        data = data.replace("'", '"')
        data = json.loads(data)
    elif type(data) == list:
        pass

    return data