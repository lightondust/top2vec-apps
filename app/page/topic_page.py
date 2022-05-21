from page.base_page import BasePage
import streamlit as st
import pandas as pd


class TopicPage(BasePage):
    title = 'Topic Page'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        st.title(TopicPage.title)

    def run(self):
        model_name_selected = st.selectbox('model:', self.app_data.model_map.keys())
        if model_name_selected in self.app_data.model_map:
            model = self.app_data.model_map[model_name_selected]
            top2vec_model = model.top2vec_model

            topic_no = top2vec_model.get_num_topics()
            st.write('topic no: ', topic_no)

            topic_selected = st.selectbox('topic:', [''] + list(range(topic_no)))

            num_res = st.slider('number of results:', 0, 100, 10, 1)
            num_res = int(num_res)

            if topic_selected != '':
                st.write(top2vec_model.topic_sizes[topic_selected])
                # fig = generate_topic_wordcloud(model, topic_selected)
                # st.pyplot(fig=fig)
                # w_ = dict(zip(model.topic_words[topic_selected],
                #               softmax(model.topic_word_scores[topic_selected])))
                # st.write(w_)
                # words_ = [{'text': w, 'value': float(s)} for w, s in zip(model.topic_words[topic_selected], model.topic_word_scores[topic_selected])]
                # st.write(words_)
                # wordcloud.visualize(words_, enable_tooltip=False, key='aaa')

                topic_words = top2vec_model.topic_words[topic_selected]
                scores = top2vec_model.topic_word_scores[topic_selected]
                topic_df = pd.DataFrame(zip(topic_words, scores), columns=['word', 'score'])
                # print(topic_df)
                st.dataframe(topic_df)

                documents, document_scores, document_ids = top2vec_model.search_documents_by_topic(topic_num=topic_selected,
                                                                                                   num_docs=num_res)
                for doc, score, doc_id in zip(documents, document_scores, document_ids):
                    st.write(f"### Document: {doc_id}, Score: {score}")
                    # print("-----------")
                    st.write(doc[:300].replace('\n', ' /// '))
                    with st.expander('detail'):
                        st.write(doc)
                    # print("-----------")
                    # print()

