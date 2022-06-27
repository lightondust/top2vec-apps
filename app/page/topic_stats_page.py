from page.base_page import BasePage
import streamlit as st
import pandas as pd
import plotly.express as px


class TopicStatsPage(BasePage):
    title = 'Topic stats'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        self.num_res = None
        self.function_map = {
            self.function_topic_stats_key: self.topic_stats
        }

    def topic_stats(self):
        df = self.topic_df.copy(deep=True)
        fig = px.bar(df, x='name', y='topic_size')
        st.plotly_chart(fig)
        if df.shape[0] > 20:
            df.loc[df.topic_size < df.topic_size.iloc[19], 'name'] = 'other'
        fig = px.pie(df, values='topic_size', names='name')
        st.plotly_chart(fig)
        st.dataframe(self.topic_df)

    def run(self):
        st.title(TopicStatsPage.title)
        self.run_model_process()
        if self.model:
            self.topic_stats()

    def topic_link(self, topic_idx):
        pm = {self.function_url_key: self.function_topic_detail_key, 'topic': topic_idx, 'page': TopicPage.title}
        return '[topic detail]({})'.format(self.app_url.internal_link(**pm))
