from typing import List
import japanize_matplotlib
from matplotlib import pyplot as plt
from scipy.special import softmax
from top2vec import Top2Vec
from wordcloud import WordCloud
import jieba
from sudachipy import dictionary, tokenizer
import streamlit as st
from typing import Optional


class BaseModel(object):

    def __init__(self):
        self.info = ''
        self.top2vec_model: Optional[Top2Vec] = None
        self.path = ''
        self.tokenizer = None
        self.font_path = ''
        self.jp_font_path = japanize_matplotlib.get_font_path() + '/ipaexg.ttf'
        self.ch_font_path = '../data/fonts/chinese.simhei.ttf'

    def top_display(self, top_id):
        return '{}_{}'.format(top_id, '_'.join(self.top2vec_model.topic_words[top_id][:3]))

    def view_document(self, doc_id):
        doc_idx = self.top2vec_model.doc_id2index[doc_id]
        top_idx = self.top2vec_model.doc_top[doc_idx]
        top = self.top_display(top_idx)
        top_score = self.top2vec_model.doc_dist[doc_idx]
        st.markdown('topic: {}, score: {}'.format(top, top_score))
        doc = self.top2vec_model.documents[doc_idx]
        st.write(doc[:300].replace('\n', ' /// '))
        with st.expander('full text'):
            st.write(doc.replace('\n', '\n\n'))

    @staticmethod
    def transform_document_id(doc_id):
        try:
            return int(doc_id)
        except ValueError:
            return doc_id

    def load_model(self):
        self.top2vec_model = Top2Vec.load(self.path)

    def wordcloud(self, word_score_dict, background_color="black"):
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

    def generate_topic_wordcloud(self, topic_num, reduced=False, **kwargs):
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

        return self.wordcloud(word_score_dict, **kwargs)


class NewsGroup20Model(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/20_news_group.model'
        self.info = '''
        learned on dataset: 20 Newsgroups
        [link](http://qwone.com/~jason/20Newsgroups/)
        '''


class LivedoorModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/livedoor.model'
        self.tokenizer = jp_tokenizer
        self.font_path = self.jp_font_path
        self.info = '''
        learned on livedoor ニュースコーパス([link](https://www.rondhuit.com/download.html#news%20corpus))
        '''

    def view_document(self, doc):
        st.write(doc[:300].replace('\n', ' /// '))
        # with st.expander('full text'):
        #     st.write(doc.replace('\n', '\n\n'))


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


def split_text(txt, txt_chunk_length_th=10000) -> List[str]:
    sts = txt.split()
    txt_chunks = []
    txt_chunk = ''
    for s in sts:
        if len(txt_chunk) > txt_chunk_length_th - len(s):
            txt_chunks.append(txt_chunk)
            txt_chunk = s
        else:
            txt_chunk += '\n' + s
    txt_chunks.append(txt_chunk)
    return txt_chunks


class SudachiTokenizer(object):

    def __init__(self):
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.C

    @staticmethod
    def filter_word(tk):
        part_of_speech = tk.part_of_speech()

        if '数詞' in part_of_speech:
            return False
        elif '名詞' in part_of_speech:
        # elif '名詞' in part_of_speech or '動詞' in part_of_speech or '形容詞' in part_of_speech:
            return True

    def tokenize(self, txt, auto_split):
        try:
            tks = self.tokenizer_obj.tokenize(txt)
            return tks
        except Exception as e:
            if auto_split:
                tks = []
                txt_chunks = split_text(txt)
                for t in txt_chunks:
                    tks += self.tokenizer_obj.tokenize(t)
                return tks
            else:
                raise e

    def wakati(self, txt, auto_split=True):
        tk_list = self.tokenize(txt, auto_split=auto_split)

        words = []
        for tk in tk_list:
            if self.filter_word(tk):
                words.append(tk.normalized_form())

        return words

    def wakati_no_filter(self, txt, auto_split=True):
        tk_list = self.tokenize(txt, auto_split=auto_split)
        words = [t.normalized_form() for t in tk_list]
        return words


model_class_map = {
    # 'youho': YouhouModel,
    # 'youho_noun_stop': YouhouNounStopModel,
    # 'ch': ChOtModel,
    # 'ch fix 500': ChOtFix500Model,
    'livedoor news dataset': LivedoorModel,
    '20 news group model': NewsGroup20Model
}
