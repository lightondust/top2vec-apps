from page.base_page import BasePage
import streamlit as st


class WordPage(BasePage):
    title = 'Search Word'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        self.function_map = {
            self.function_search_by_words_key: self.search_words_by_word
        }

    def search_words_by_word(self):
        sim_words_selected = st.multiselect('search words by words:', self.word_list)
        if sim_words_selected:
            words, word_scores = self.top2vec_model.similar_words(keywords=sim_words_selected,
                                                                  keywords_neg=[],
                                                                  num_words=self.num_res)
            for word, score in zip(words, word_scores):
                st.write(f"{word} {score}")

    def run(self):
        super().run()
        self.title_comp.title(WordPage.title)
