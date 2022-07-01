from page.base_page import BasePage
import plotly.express as px
import streamlit as st
import pandas as pd
from streamlit_plotly_events import plotly_events


class TravelingPage(BasePage):
    title = 'Traveling in data'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        self.num_res_max = 1000

    def center_from_document_id(self, doc_id, v_df):
        center_item = v_df[v_df['name'] == doc_id]
        center = ()
        if center_item.shape[0]:
            center = (center_item.iloc[0].x, center_item.iloc[0].y)
        return center, center_item

    def plot_at_center_plotly_fig(self, center, v_df, x_l, y_l, center_item=pd.DataFrame(), if_display_text=False):
        x_l *= 1.1
        y_l *= 1.1
        x_range = [center[0] - x_l / 2, center[0] + x_l / 2]
        y_range = [center[1] - y_l / 2, center[1] + y_l / 2]

        df_view = v_df[(v_df.x < x_range[1]) & (v_df.x > x_range[0])]
        df_view = df_view[(df_view.y < y_range[1]) & (df_view.y > y_range[0])]

        df_view = df_view.sort_values('size').iloc[::-1].iloc[:self.num_res]
        if center_item.shape[0]:
            df_view = pd.concat([df_view, center_item])

        additional_args = {}
        if if_display_text:
            additional_args['text'] = 'name'
        fig = px.scatter(df_view,
                         x='x',
                         y='y',
                         **additional_args,
                         color='color',
                         range_x=x_range,
                         range_y=y_range,
                         size='size',
                         symbol='node_type',
                         hover_data=['name', 'topic_id', 'topic_name'],
                         color_discrete_map={'red': 'red', 'blue': 'blue'},
                         symbol_map={
                             'topic': 'circle-open',
                             'document': 'x-open'
                         })
        size = {'width': 1200, 'height': 900}
        fig.update_layout(**size)
        return fig, df_view

    def plot_at_center(self, center, fig_el, v_df, x_l, y_l, center_item=pd.DataFrame(), if_display_text=False):
        # fig_el.empty()
        fig, df_view = self.plot_at_center_plotly_fig(center, v_df, x_l, y_l, center_item=center_item,
                                                      if_display_text=if_display_text)
        with fig_el.container():
            ev = plotly_events(fig)
        return ev, df_view

    def run(self):
        self.title_comp = st.title(TravelingPage.title)
        self.run_model_process()

        if self.model:
            v_df = self.model.viz_df.copy(deep=True)

            doc_el = st.empty()
            document_id_selected = doc_el.selectbox('highlight document:', [''] + list(self.top2vec_model.document_ids))
            document_id_selected = str(document_id_selected)

            self.num_res = st.slider('number of results:', 0, self.num_res_max, 50, 1)
            self.num_res = int(self.num_res)

            v_df['color'] = v_df.name.apply(lambda x: 'red' if x == document_id_selected else 'blue')
            v_df['size'] = v_df['score'].apply(lambda x: max(x, 0.1))

            scale = st.slider('zoom:', 0.01, 1., 0.5, 0.01)
            fig_el = st.empty()
            if_display_text = st.checkbox('show text')

            x_total_range = v_df.x.min(), v_df.x.max()
            x_l = x_total_range[1] - x_total_range[0]
            x_l *= scale
            y_total_range = v_df.y.min(), v_df.y.max()
            y_l = y_total_range[1] - y_total_range[0]
            y_l *= scale
            center_default = ((x_total_range[1] - x_total_range[0])/2, (y_total_range[1] - y_total_range[0])/2)

            center_doc, center_item = self.center_from_document_id(document_id_selected, v_df)
            center = self.app_url.sync_variable_list('center', [], center_default)
            center = [float(c) for c in center]
            # st.write(center)

            ev, df_view = self.plot_at_center(center, fig_el, v_df, x_l, y_l, center_item=center_item, if_display_text=if_display_text)

            if ev:
                # st.write(ev)
                point = (ev[0]['x'], ev[0]['y'])
                # st.write(point)
                df_view['x_diff'] = df_view.x - point[0]
                df_view['y_diff'] = df_view.y - point[1]
                df_view['dis_diff'] = abs(df_view['x_diff']) + abs(df_view['y_diff'])
                df_view = df_view.sort_values('dis_diff')
                df_sel = df_view.iloc[0:1].copy()
                if df_sel.iloc[0]['node_type'] == 'document':
                    doc_id_sel = df_sel['name'].iloc[0]
                    doc_idx = self.model.top2vec_model.doc_id2index[doc_id_sel]
                    doc = self.top2vec_model.documents[doc_idx]
                df_sel['text'] = [doc]
                st.write(df_sel)
                # st.write(pd.DataFrame([doc]))

                # st.write(df_view.iloc[ev[0]['pointIndex']: ev[0]['pointIndex']+1])
                if_move_center = st.button('move to above point')

                # st.write(if_move_center)
                if if_move_center:
                    self.app_url.sync_variable_list('center', point, ())
                    ev, df_view = self.plot_at_center(point, fig_el, v_df, x_l, y_l, center_item=center_item,
                                                      if_display_text=if_display_text)


            st.write('no of displayed items:', df_view.shape[0])
            st.write(document_id_selected)
            st.write(df_view)

