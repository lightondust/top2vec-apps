from top2vec import Top2Vec
from wordcloud import WordCloud
from scipy.special import softmax
import jieba
import os
from sudachi_tokenizer import SudachiTokenizer
import json
import matplotlib.pyplot as plt
import japanize_matplotlib


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
            'ch': ChOtModel,
            'ch fix 500': ChOtFix500Model,
            'livedoor news dataset': LivedoorModel,
            '20 news group model': NewsGroup20Model
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
        self.tokenizer = None
        self.font_path = ''
        self.jp_font_path = japanize_matplotlib.get_font_path() + '/ipaexg.ttf'
        self.ch_font_path = '../data/fonts/chinese.simhei.ttf'

    def load_model(self):
        self.top2vec_model = Top2Vec.load(self.path)

    def generate_topic_wordcloud(self, topic_num, background_color="black", reduced=False):
        model = self.top2vec_model

        if reduced:
            model._validate_hierarchical_reduction()
            model._validate_topic_num(topic_num, reduced)
            word_score_dict = dict(zip(model.topic_words_reduced[topic_num],
                                       softmax(model.topic_word_scores_reduced[topic_num])))
        else:
            model._validate_topic_num(topic_num, reduced)
            word_score_dict = dict(zip(model.topic_words[topic_num],
                                       softmax(model.topic_word_scores[topic_num])))

        fig = plt.figure(figsize=(16, 4),
                         dpi=200)
        plt.axis("off")
        additional_input = {}
        if self.font_path:
            additional_input['font_path'] = self.font_path
        plt.imshow(
            WordCloud(width=1600,
                      height=400,
                      background_color=background_color, **additional_input).generate_from_frequencies(word_score_dict))
        return fig


class NewsGroup20Model(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/20_news_group.model'


class LivedoorModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/livedoor.model'
        self.tokenizer = jp_tokenizer
        self.font_path = self.jp_font_path


class YouhouModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/youhou_norm_form.model'
        self.tokenizer = jp_tokenizer
        self.font_path = self.jp_font_path


class YouhouNounStopModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/youhou_norm_noun_stopword.model'
        self.tokenizer = jp_tokenizer_noun
        self.font_path = self.jp_font_path


class ChOtFix500Model(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/ch_ot_fix500.model'
        self.tokenizer = jieba_tokenizer
        self.font_path = self.ch_font_path


class ChOtModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/ch_ot.model'
        self.tokenizer = jieba_tokenizer
        self.font_path = self.ch_font_path


def jieba_tokenizer(doc):
    return list(jieba.cut(doc))


def jp_tokenizer(txt):
    sudachi_tokenizer = SudachiTokenizer()
    return sudachi_tokenizer.wakati_no_filter(txt)


def jp_tokenizer_noun(txt):
    sudachi_tokenizer = SudachiTokenizer()
    return sudachi_tokenizer.wakati(txt)


def get_app_data(page_class):
    return AppData(page_class)
