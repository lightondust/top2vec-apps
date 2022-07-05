from plotly import express as px
from typing import List
import japanize_matplotlib
from matplotlib import pyplot as plt
from scipy.special import softmax
from top2vec import Top2Vec
from top2vec.Top2Vec import default_tokenizer
from wordcloud import WordCloud
import jieba
from sudachipy import dictionary, tokenizer
import streamlit as st
from typing import Optional
import umap
import pandas as pd
import os


class BaseModel(object):

    def __init__(self):
        self.info = ''
        self.top2vec_model: Optional[Top2Vec] = None
        self.path = ''
        self.tokenizer = None
        self.font_path = ''
        self.jp_font_path = japanize_matplotlib.get_font_path() + '/ipaexg.ttf'
        self.ch_font_path = '../data/fonts/chinese.simhei.ttf'
        self.topic_name_list = None
        self.viz_df:Optional[pd.DataFrame] = None

    def query_to_vec(self, query):
        self.top2vec_model._validate_query(query)
        # self._validate_num_docs(num_docs)

        if self.top2vec_model.embedding_model != "doc2vec":
            query_vec = self.top2vec_model._embed_query(query)

        else:
            tokenizer = self.tokenizer
            # if tokenizer is not passed use default
            if self.tokenizer is None:
                tokenizer = default_tokenizer

            tokenized_query = tokenizer(query)

            query_vec = self.top2vec_model.model.infer_vector(doc_words=tokenized_query,
                                                              alpha=0.025,
                                                              min_alpha=0.01,
                                                              epochs=100)
        return query_vec

    @property
    def viz_path(self):
        return self.path + '.viz.csv'

    def create_viz_data(self):
        if not os.path.exists(self.viz_path):
            u_model = umap.UMAP(metric='cosine')
            doc_vec_u = u_model.fit_transform(self.top2vec_model.document_vectors)

            doc_df = pd.DataFrame(doc_vec_u, columns=['x', 'y'])
            doc_df['name'] = self.top2vec_model.document_ids
            doc_df['topic_id'] = self.top2vec_model.doc_top
            doc_df['topic_id'] = doc_df.topic_id.astype('category')
            doc_df['node_type'] = 'document'
            doc_df['score'] = self.top2vec_model.doc_dist

            topic_u_embedding = u_model.transform(self.top2vec_model.topic_vectors)
            topic_u_embedding_df = pd.DataFrame(topic_u_embedding, columns=['x', 'y'])
            topic_u_embedding_df['node_type'] = 'topic'
            topic_u_embedding_df['name'] = self.topic_name_list
            topic_u_embedding_df['topic_id'] = list(range(topic_u_embedding_df.shape[0]))
            topic_u_embedding_df['topic_id'] = topic_u_embedding_df.topic_id.astype('category')
            topic_u_embedding_df['score'] = 1.

            viz_df = pd.concat([doc_df, topic_u_embedding_df])
            viz_df.to_csv(self.viz_path)
        self.viz_df = pd.read_csv(self.viz_path, index_col=0)
        self.viz_df['topic_name'] = self.viz_df.topic_id.apply(lambda x: self.topic_name_list[x])
        self.viz_df.topic_id = self.viz_df.topic_id.astype('category')
        self.viz_df.node_type = self.viz_df.node_type.astype('category')

    def top_display(self, top_id):
        return '{}_{}'.format(top_id, '_'.join(self.top2vec_model.topic_words[top_id][:3]))

    def view_document(self, doc_id, **kwargs):
        self._view_document(doc_id, **kwargs)

    def _view_document(self, doc_id, full_doc=True):
        doc_idx = self.top2vec_model.doc_id2index[doc_id]
        top_idx = self.top2vec_model.doc_top[doc_idx]
        top = self.top_display(top_idx)
        top_score = self.top2vec_model.doc_dist[doc_idx]
        st.markdown('topic: {}, score: {}'.format(top, top_score))
        doc = self.top2vec_model.documents[doc_idx]
        st.write(doc[:300].replace('\n', ' /// '))
        if full_doc:
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
        self.topic_name_list = ['{}_{}'.format(i, '_'.join(t[:3])) for i, t in enumerate(self.top2vec_model.topic_words)]
        self.create_viz_data()

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


class W2VCitation(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/w2v_citation.model'
        self.info = '''
        learned on papers which cite the word2vec paper [link](https://arxiv.org/abs/1301.3781)
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

    def view_document(self, doc_id):
        self._view_document(doc_id, full_doc=False)


class JpModel(BaseModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/yutura.model'
        # self.path = '../data/models/twitter.model'
        # self.path = '../data/models/blockchain_biz.model'
        self.tokenizer = jp_tokenizer
        self.font_path = self.jp_font_path


class JpNounStopModel(JpModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/youhou_norm_noun_stopword.model'
        self.tokenizer = jp_tokenizer_noun


class YouturaModel(JpModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/yutura.model'


class TwitterModel(JpModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/twitter.model'


class YouhouModel(JpModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/youhou_norm_form.model'


class YouhouNounStopModel(JpNounStopModel):

    def __init__(self):
        super().__init__()
        self.path = '../data/models/youhou_norm_noun_stopword.model'


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
    # 'jpmodel': JpModel,
    'twitter': TwitterModel,
    'yutura': YouturaModel,
    # 'ch': ChOtModel,
    # 'ch fix 500': ChOtFix500Model,
    # 'livedoor news dataset': LivedoorModel,
    # '20 news group model': NewsGroup20Model,
    'arxiv papers': W2VCitation,
}
