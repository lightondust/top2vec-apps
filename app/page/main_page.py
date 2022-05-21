from page.base_page import BasePage
import streamlit as st


class MainPage(BasePage):
    title = 'Main Page'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        st.title(self.title)

    def run(self):
        for page, page_cls in self.app_data.page_class.items():
            if page_cls.title != MainPage.title:
                st.markdown("[{}]({})".format(page_cls.title, self.app_url.internal_link(page=page)), unsafe_allow_html=True)
