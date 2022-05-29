import streamlit as st

from app_url import AppURL
from page.main_page import MainPage
from page.topic_page import TopicPage
from page.document_page import DocumentPage
from page.word_page import WordPage
from app_data import get_app_data
import logging
from app_model import model_class_map

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%m/%d/%Y %X")

st.set_page_config(layout='wide', page_title='top2vec apps', page_icon='./favico_s_t.png')


@st.cache(allow_output_mutation=True)
def _get_app_data(page_class, model_class_map):
    return get_app_data(page_class, model_class_map)


page_class = {
    'Main page': MainPage,
    'Topic page': TopicPage,
    'Document page': DocumentPage,
    'Word page': WordPage,
}
page_selected = st.sidebar.radio('page:', list(page_class.keys())+[''], index=len(page_class))

app_data = _get_app_data(page_class, model_class_map)
app_url = AppURL()
page = app_url.sync_variable('page', page_selected, 'Main page')

page_obj = page_class[page](app_data=app_data, app_url=app_url)
page_obj.run()
