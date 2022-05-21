from abc import ABC, abstractmethod
from app_data import AppData
from app_url import AppURL
import streamlit as st


class BasePage(ABC):
    def __init__(self, app_data: AppData, app_url: AppURL):
        self.app_data = app_data
        self.app_url = app_url
        self.topic_no = None
        self.top2vec_model = None
        self.model = None

        self.function_url_key = 'function'
        self.function_topic_detail_key = 'topic details'
        self.function_document_detail_key = 'document details'
        self.function_search_by_words_key = 'search by words'
        self.function_search_by_text_key = 'search by text'

    def run(self):
        self.num_res = st.slider('number of results:', 0, 100, 10, 1)
        self.num_res = int(self.num_res)

        if self.select_model():
            func = st.radio('function:', [''] + list(self.function_map.keys()))
            func = self.app_url.sync_variable(self.function_url_key, func, '')
            st.markdown('### function {}'.format(func))
            if func in self.function_map:
                self.function_map[func]()

    def select_model(self):
        model_name_selected = st.selectbox('model:', [''] + list(self.app_data.model_map.keys()))
        model_name = self.app_url.sync_variable('model', model_name_selected, '')
        st.markdown('#### model: {}'.format(model_name))
        if model_name in self.app_data.model_map:
            self.model = self.app_data.model_map[model_name]
            self.top2vec_model = self.model.top2vec_model
            self.word_list = list(self.top2vec_model.word_indexes.keys())
            self.topic_no = self.top2vec_model.get_num_topics()
            st.markdown('#### total topic no: {}'.format(self.topic_no))
        return model_name

    def topic_link(self, topic):
        pm = {self.function_url_key: self.function_topic_detail_key, 'topic': topic}
        return '[detail link]({})'.format(self.app_url.internal_link(**pm))
