from page.base_page import BasePage
from page.topic_page import TopicPage
from page.document_page import DocumentPage
import streamlit as st


class AdvancedSearchPage(BasePage):
    title = 'advanced Search Page'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        self.vec_src = []
        self.vecs_tar = []

    def run(self):
        self.title_comp = st.empty()
        self.num_res = st.slider('number of results:', 0, self.num_res_max, 10, 1)
        self.num_res = int(self.num_res)
        self.run_model_process()

        if self.model:
            topic_page = TopicPage(self.app_data, app_url=self.app_url, model_name=self.model_name)
            document_page = DocumentPage(self.app_data, app_url=self.app_url, model_name=self.model_name)

            topic_name_selected = st.multiselect('topics:', self.model.topic_name_list)
            topic_weight = st.slider('topic weight', 0., 10.0, 1.0, 0.1)
            # topic_idx_selected = self.topic_name_list.index(topic_name_selected)
            if topic_name_selected:
                topic_idx_selected = [self.topic_name_list.index(t) for t in topic_name_selected]
                # topic_idx_selected = self.app_url.sync_variable_list('topic', topic_idx_selected, '')
                topic_vecs_src = [self.top2vec_model.topic_vectors[i]*topic_weight for i in topic_idx_selected]
                with st.expander('topic source detail'):
                    for t_name, t_idx in zip(topic_name_selected, topic_idx_selected):
                        st.markdown('{}: {}'.format(t_name, topic_page.topic_link(t_idx)))
            else:
                topic_vecs_src = []

            words_selected = st.multiselect('words:', self.word_list)
            word_weight = st.slider('word weight', 0., 10.0, 1.0, 0.1)
            word_idx_selected = [self.top2vec_model.word_indexes[t] for t in words_selected]
            word_vecs_src = [word_weight * self.top2vec_model.word_vectors[i] for i in word_idx_selected]

            document_ids_selected = st.multiselect('documents::', self.top2vec_model.document_ids)
            document_idx_selected = [self.top2vec_model.doc_id2index[t] for t in document_ids_selected]
            document_weight = st.slider('document weight', 0., 10.0, 1.0, 0.1)
            docs_vecs_src = [document_weight * self.top2vec_model.document_vectors[i] for i in document_idx_selected]
            with st.expander('document source detail'):
                for d_id in document_ids_selected:
                    st.markdown('{}: {}'.format(d_id, document_page.document_link(d_id)))

            text_documents = st.text_input('text:')
            text_weight = st.slider('text weight', 0., 10.0, 1.0, 0.1)
            if text_documents:
                text_vecs_src = [text_weight * self.model.query_to_vec(text_documents)]
            else:
                text_vecs_src = []

            vecs_src = topic_vecs_src + word_vecs_src + docs_vecs_src + text_vecs_src
            if vecs_src:
                self.vec_src = self.top2vec_model._get_combined_vec(vecs_src, [])

            search_for = st.radio('search for:', ['', 'topics', 'words', 'documents'], horizontal=True)
            if search_for == 'topics':
                self.vecs_tar = self.top2vec_model.topic_vectors
                if vecs_src:
                    idx_list, score_list = self.top2vec_model._search_vectors_by_vector(self.vecs_tar, self.vec_src, num_res=self.num_res)
                    topic_idx = idx_list
                    topic_scores = score_list
                    topic_words = [self.top2vec_model.topic_words[i] for i in topic_idx]
                    topic_page.view_topic_list(topic_idx, topic_words, topic_scores)
            elif search_for == 'words':
                self.vecs_tar = self.top2vec_model.word_vectors
                if vecs_src:
                    idx_list, score_list = self.top2vec_model._search_vectors_by_vector(self.vecs_tar, self.vec_src, num_res=self.num_res)
                    word_list = [self.top2vec_model.vocab[i] for i in idx_list]
                    for word, score in zip(word_list, score_list):
                        st.write(f"{word} {score}")
            elif search_for == 'documents':
                self.vecs_tar = self.top2vec_model.document_vectors
                if vecs_src:
                    idx_list, score_list = self.top2vec_model._search_vectors_by_vector(self.vecs_tar, self.vec_src, num_res=self.num_res)
                    doc_id_list = [self.top2vec_model.document_ids[i] for i in idx_list]
                    documents = [self.top2vec_model.documents[i] for i in idx_list]
                    document_page.view_document_list(documents, score_list, doc_id_list)


