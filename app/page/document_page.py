from page.base_page import BasePage
import pandas as pd
import streamlit as st



class DocumentPage(BasePage):
    title = 'Document Page'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        self.function_map = {
            self.function_document_detail_key: self.document_view,
            self.function_search_by_words_key: self.search_documents_by_words,
            self.function_search_by_text_key: self.search_documents_by_text,
            self.function_search_by_documents_key: self.search_documents_by_documents
        }

    def search_documents_by_documents(self):
        doc_ids_selected = st.multiselect('document to words:', [''] + list(self.top2vec_model.document_ids))
        if doc_ids_selected:
            self._search_documents_by_documents(doc_ids_selected)

    def _search_documents_by_documents(self, document_ids):
        document_ids, document_scores, document_ids = self.top2vec_model.search_documents_by_documents(document_ids,
                                                                                                       num_docs=self.num_res)
        self.view_document_list(document_ids, document_scores, document_ids)

    def document_view(self):
        doc_selected = st.selectbox('document to words:', [''] + list(self.top2vec_model.document_ids))
        doc_selected = self.app_url.sync_variable('document', doc_selected, '')
        doc_selected = self.model.transform_document_id(doc_selected)

        st.markdown('#### document: {}'.format(doc_selected))
        if doc_selected in self.top2vec_model.doc_id2index:
            doc_idx_selected = self.top2vec_model.doc_id2index[doc_selected]
            doc_vec = self.top2vec_model.document_vectors[doc_idx_selected]
            word_ids, scores = self.top2vec_model._search_vectors_by_vector(self.top2vec_model.word_vectors,
                                                                            doc_vec,
                                                                            num_res=self.num_res_max)
            words = [self.top2vec_model.vocab[i] for i in word_ids]
            word_score_dict = {w:s for w,s in zip(words, scores)}
            fig = self.model.wordcloud(word_score_dict)
            st.pyplot(fig)

            st.table(pd.DataFrame(zip(words, scores), columns=['word', 'score']).iloc[:self.num_res])

            self.model.view_document(doc_selected)
            st.markdown('## documents similar')
            self._search_documents_by_documents([doc_selected])

    def view_document_list(self, documents, document_scores, document_ids):
        for doc, score, doc_id in zip(documents, document_scores, document_ids):
            st.write(f"### Document: {doc_id}, Score: {score}")
            self.model.view_document(doc_id)
            if doc_id:
                st.markdown(self.document_link(doc_id))

    def search_documents_by_text(self):
        text_documents = st.text_input('search documents by similar text:')
        if text_documents:
            documents, document_scores, document_ids = self.top2vec_model.query_documents(
                text_documents, num_docs=self.num_res, tokenizer=self.model.tokenizer)
            if self.model.tokenizer:
                st.write(', '.join(self.model.tokenizer(text_documents)))
            self.view_document_list(documents, document_scores, document_ids)

    def search_documents_by_words(self):
        document_words_selected = st.multiselect('search documents by words:', self.word_list)
        if document_words_selected:
            documents, document_scores, document_ids = self.top2vec_model.search_documents_by_keywords(
                keywords=document_words_selected,
                num_docs=self.num_res)
            self.view_document_list(documents, document_scores, document_ids)

    def run(self):
        super().run()
        self.title_comp.title(DocumentPage.title)

    def document_link(self, document_id):
        pm = {self.function_url_key: self.function_document_detail_key, 'document': document_id, 'page': DocumentPage.title}
        return '[document detail]({})'.format(self.app_url.internal_link(**pm))
