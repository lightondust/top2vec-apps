import os
import json


def save_json(path, obj):
    with open(path+'tmp', 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.rename(path+'tmp', path)


def load_json(path):
    with open(path, 'r') as f:
        obj = json.load(f)
    return obj


class AppData(object):

    def __init__(self, page_class, model_class_map, auto_process=True):
        self.page_class = page_class
        self._model_class_map = model_class_map
        self.model_map = {}

        if auto_process:
            for k, v in self._model_class_map.items():
                _m = v()
                _m.load_model()
                self.model_map[k] = _m


def get_app_data(page_class, model_class_map):
    return AppData(page_class, model_class_map)
