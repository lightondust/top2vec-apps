from abc import ABC, abstractmethod
import pandas as pd
from typing import List
from app_data import AppData
from app_url import AppURL
import streamlit as st
from top2vec import Top2Vec
from typing import Optional
from app_model import BaseModel


class BasePage(ABC):
    def __init__(self, app_data: AppData, app_url: AppURL):
        self.topic_name_list = []
        self.num_res = None
        self.word_list: List[str] = []
        self.app_data = app_data
        self.app_url = app_url
        self.topic_no = None
        self.top2vec_model: Optional[Top2Vec] = None
        self.model: Optional[BaseModel] = None
        self.num_res_max = 100
        self.function_map = {}
        self.title_comp = None

        self.function_url_key = 'function'
        self.function_topic_detail_key = 'topic details'
        self.function_topic_stats_key = 'topic stats'
        self.function_document_detail_key = 'document details'
        self.function_search_by_words_key = 'search by words'
        self.function_search_by_text_key = 'search by text'
        self.function_search_by_documents_key = 'search by documents'

    def run(self):
        self.title_comp = st.empty()
        self.num_res = st.slider('number of results:', 0, self.num_res_max, 10, 1)
        self.num_res = int(self.num_res)

        if self.select_model():
            func = st.radio('function:', [''] + list(self.function_map.keys()))
            func = self.app_url.sync_variable(self.function_url_key, func, '')
            st.markdown('### function {}'.format(func))
            if func in self.function_map:
                self.function_map[func]()

        if self.model:
            st.sidebar.markdown(self.model.info)

        st.sidebar.markdown('[source code](https://github.com/lightondust/top2vec-apps)')

    def select_model(self):
        model_name_selected = st.selectbox('model:', [''] + list(self.app_data.model_map.keys()))
        model_name = self.app_url.sync_variable('model', model_name_selected, '')
        st.markdown('#### model: {}'.format(model_name))
        if model_name in self.app_data.model_map:
            self.model = self.app_data.model_map[model_name]
            self.top2vec_model = self.model.top2vec_model
            self.word_list = list(self.top2vec_model.word_indexes.keys())
            self.topic_no = self.top2vec_model.get_num_topics()
            self.topic_name_list = ['{}_{}'.format(i, '_'.join(t[:3])) for i, t in enumerate(self.top2vec_model.topic_words)]
            self.topic_df = pd.DataFrame(zip(self.topic_name_list, self.top2vec_model.topic_sizes),
                                         columns=['name', 'topic_size'])
            st.markdown('#### total topic no: {}'.format(self.topic_no))
        return model_name

    def topic_link(self, topic):
        pm = {self.function_url_key: self.function_topic_detail_key, 'topic': topic}
        return '[topic detail]({})'.format(self.app_url.internal_link(**pm))

    def document_link(self, document):
        pm = {self.function_url_key: self.function_document_detail_key, 'document': document}
        return '[document detail]({})'.format(self.app_url.internal_link(**pm))
