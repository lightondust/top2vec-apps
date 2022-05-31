from page.base_page import BasePage
import streamlit as st


class TemplatePage(BasePage):
    title = 'Template Page'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)

    def run(self):
        super().run()
        self.title_comp.title(TemplatePage.title)
