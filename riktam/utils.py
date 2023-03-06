from pymongo import MongoClient
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from channels.generic.websocket import WebsocketConsumer


def get_mongo_db(
    db_name="chat_db", host="localhost", port="27017", username="", password=""
):
    client = MongoClient(
        host=host, port=int(port), username=username, password=password
    )
    cursor = client[db_name]
    print(f"Got db connection to {cursor}")
    return cursor, client


class ModelViewSetConsumer(ModelViewSet, WebsocketConsumer):
    def __init__(self, **kwargs):
        super(ModelViewSet, self).__init__(**kwargs)
        super(WebsocketConsumer, self).__init__(**kwargs)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def refactor_dicts(dict1, dict2, ignored_keys=[], key_mapping={}):
    cleaned_dict1 = {k: dict1[k] for k in dict1.keys() if k not in ignored_keys}
    cleaned_dict2 = {
        key_mapping[k] if k in key_mapping.keys() else k: dict2[k]
        for k in dict2.keys()
        if k not in ignored_keys
    }
    return cleaned_dict1, cleaned_dict2


def compare_dict(dict1, dict2, ignored_keys=[], key_mapping={}):
    res = True
    r_dict1, r_dict2 = refactor_dicts(dict1, dict2, ignored_keys, key_mapping)
    diff_keys = []

    for k, v in r_dict1.items():
        if isinstance(v, dict):
            if compare_dict(v, r_dict2[k])[0]:
                diff_keys.append(k)
                res = False
        else:
            if v != r_dict2[k]:
                diff_keys.append(k)
                res = False
    return res, diff_keys
