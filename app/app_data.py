from top2vec import Top2Vec
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

    def __init__(self, page_class, auto_process=True):
        self.page_class = page_class
        self._model_class_map = {
            'youho': YouhouModel,
            'youho_noun_stop': YouhouNounStopModel,
            'livedoor news dataset': LivedoorModel
        }
        self.model_map = {}

        if auto_process:
            for k, v in self._model_class_map.items():
                _m = v()
                _m.load_model()
                self.model_map[k] = _m


class BaseModel(object):

    def __init__(self):
        self.top2vec_model = None
        self.path = ''

    def load_model(self):
        self.top2vec_model = Top2Vec.load(self.path)


class LivedoorModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/livedoor.model'


class YouhouModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/youhou_norm_form.model'


class YouhouNounStopModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/youhou_norm_noun_stopword.model'


def get_app_data(page_class):
    return AppData(page_class)
