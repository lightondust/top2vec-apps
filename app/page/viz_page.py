from page.base_page import BasePage
import streamlit as st
import plotly.express as px


class VizPage(BasePage):
    title = 'Visualization Page'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)

    def run(self):
        super().run()
        self.title_comp.title(VizPage.title)

        if self.model:
            topic_name_selected = st.selectbox('topic:', [''] + self.model.topic_name_list)
            if topic_name_selected != '':
                topic_idx_selected = self.topic_name_list.index(topic_name_selected)
            else:
                topic_idx_selected = -1

            document_selected = st.multiselect('document:', [''] + list(self.top2vec_model.document_ids))
            v_df = self.model.viz_df.copy(deep=True)
            v_df['size'] = v_df['score']
            v_df['color1'] = v_df.topic_id.apply(lambda x: True if x == topic_idx_selected else False)
            v_df['color2'] = v_df.name.apply(lambda x: True if x in [str(d) for d in document_selected] else False)
            v_df['selected'] = (v_df.color1 + v_df.color2).apply(lambda x: True if x > 0 else False)
            v_df['opacity'] = v_df.selected.apply(lambda x: 1.0 if x else 0.3)
            # v_df['size'] = v_df['size'] + v_df['selected']
            v_df['color'] = v_df.selected.apply(lambda x: 'selected' if x else 'other')

            fig = px.scatter(v_df, x='x', y='y', color='color',
                             size='size',
                             opacity=v_df.opacity,
                             symbol='node_type', hover_data=['name', 'topic_id', 'topic_name', 'opacity'],
                             color_discrete_map={'selected': 'red', 'other': 'blue'})
            st.plotly_chart(fig)

