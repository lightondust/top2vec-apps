from page.base_page import BasePage
import streamlit as st
import pandas as pd


class TopicPage(BasePage):
    title = 'Topic Page'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        self.num_res = None
        st.title(TopicPage.title)
        self.topic_no = None
        self.top2vec_model = None
        self.model = None

    def topic_info(self, topic_selected):
        fig = self.model.generate_topic_wordcloud(topic_selected)
        st.pyplot(fig=fig)

        topic_words = self.top2vec_model.topic_words[topic_selected]
        scores = self.top2vec_model.topic_word_scores[topic_selected]
        topic_df = pd.DataFrame(zip(topic_words, scores), columns=['word', 'score'])
        st.dataframe(topic_df)

    def view_topic(self):

        st.markdown('### view topic')
        topic_selected = st.selectbox('topic:', [''] + list(range(self.topic_no)))

        if topic_selected != '':
            st.write(self.top2vec_model.topic_sizes[topic_selected])
            self.topic_info(topic_selected)

            documents, document_scores, document_ids = self.top2vec_model.search_documents_by_topic(topic_num=topic_selected,
                                                                                                    num_docs=self.num_res)
            for doc, score, doc_id in zip(documents, document_scores, document_ids):
                st.write(f"### Document: {doc_id}, Score: {score}")
                st.write(doc[:300].replace('\n', ' /// '))
                with st.expander('detail'):
                    st.write(doc)

    def search_topic_by_words(self):
        topic_words_selected = st.multiselect('search topics by words:', self.word_list)
        if topic_words_selected:
            topic_words, word_scores, topic_scores, topic_nums = self.top2vec_model.search_topics(
                keywords=topic_words_selected, num_topics=min(self.num_res, self.topic_no))
            self.view_topic_list(topic_nums, topic_words, topic_scores)

    def view_topic_list(self, topic_nums, topic_words, topic_scores):
        for topic, words, score in zip(topic_nums, topic_words, topic_scores):
            st.markdown('#### Topic {}, {:.2f}: {}'.format(topic, score, ','.join(words[:5])))
            # st.write(','.join(words[:5]))
            if_detail = st.checkbox('detail', key='topic-{}'.format(topic))
            if if_detail:
                st.write('detail')
                self.topic_info(topic)

    def search_topic_by_text(self):
        text_topics = st.text_input('search topics by text:')
        if text_topics:
            topic_words, word_scores, topic_scores, topic_nums = self.top2vec_model.query_topics(
                text_topics,
                num_topics=min(self.num_res, self.topic_no),
                tokenizer=self.model.tokenizer
            )
            if self.model.tokenizer:
                st.write(', '.join(self.model.tokenizer(text_topics)))
            self.view_topic_list(topic_nums, topic_words, topic_scores)

    def run(self):
        self.num_res = st.slider('number of results:', 0, 100, 10, 1)
        self.num_res = int(self.num_res)

        model_name_selected = st.selectbox('model:', self.app_data.model_map.keys())
        if model_name_selected in self.app_data.model_map:
            self.model = self.app_data.model_map[model_name_selected]
            self.top2vec_model = self.model.top2vec_model
            self.word_list = list(self.top2vec_model.word_indexes.keys())

            self.topic_no = self.top2vec_model.get_num_topics()
            st.markdown('## total topic no: {}'.format(self.topic_no))

            func = st.radio('function:', ['topic details', 'search topic by words', 'search topic by text'])

            if func == 'topic details':
                self.view_topic()
            elif func == 'search topic by words':
                self.search_topic_by_words()
            elif func == 'search topic by text':
                self.search_topic_by_text()
