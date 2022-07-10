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

    @staticmethod
    def item_df_from_document_ids(doc_ids, v_df):
        center_item_df = v_df[v_df['name'].isin(doc_ids)]
        return center_item_df

    def plot_at_center_plotly_fig(self, center, v_df, x_l, y_l, highlight_item_df=pd.DataFrame(), if_display_text=False):
        x_l *= 1.1
        y_l *= 1.1
        x_range = [center[0] - x_l / 2, center[0] + x_l / 2]
        y_range = [center[1] - y_l / 2, center[1] + y_l / 2]

        df_view = v_df[(v_df.x < x_range[1]) & (v_df.x > x_range[0])]
        df_view = df_view[(df_view.y < y_range[1]) & (df_view.y > y_range[0])]

        df_view = df_view.sort_values('size').iloc[::-1].iloc[:self.num_res]

        additional_args = {}
        if if_display_text:
            df_view = self.model.pickup_points(df_view, 30, 30, x_range_l=x_l, y_range_l=y_l)
            additional_args['text'] = 'display_text'

        if highlight_item_df.shape[0]:
            highlight_item_df = highlight_item_df.copy()
            highlight_item_df['display_text'] = highlight_item_df['name']
            df_view = pd.concat([df_view, highlight_item_df])
        fig = px.scatter(df_view,
                         x='x',
                         y='y',
                         **additional_args,
                         color='color',
                         range_x=x_range,
                         range_y=y_range,
                         size='size',
                         size_max=10,
                         symbol='node_type',
                         hover_data=['name', 'topic_id', 'topic_name'],
                         color_discrete_map={'red': 'red', 'blue': 'blue'},
                         symbol_map={
                             'topic': 'circle-open',
                             'document': 'x-open'
                         })
        # size = {'width': 1400, 'height': 900}
        # fig.update_layout(**size)
        return fig, df_view

    def plot_at_center(self, center, fig_el, v_df, x_l, y_l,
                       document_ids_selected,
                       center_item_doc_id='',
                       if_display_text=False):
        center_item_doc_id = self.app_url.sync_variable('center_item', center_item_doc_id, '')
        document_ids_highlight = document_ids_selected + [center_item_doc_id]

        v_df['color'] = v_df.name.apply(lambda x: 'red' if x in document_ids_highlight else 'blue')
        v_df['size'] = v_df['score'].apply(lambda x: max(x, 0.1))
        highlight_item_df = self.item_df_from_document_ids(document_ids_highlight, v_df)

        fig, df_view = self.plot_at_center_plotly_fig(center, v_df, x_l, y_l, highlight_item_df=highlight_item_df,
                                                      if_display_text=if_display_text)
        with fig_el.container():
            ev = plotly_events(fig)
        return ev, df_view

    @staticmethod
    def display_range_and_center(df, zoom):
        scale = 1/(2**zoom)
        x_range = df.x.min(), df.x.max()
        x_l = x_range[1] - x_range[0]
        x_l *= scale
        y_range = df.y.min(), df.y.max()
        y_l = y_range[1] - y_range[0]
        y_l *= scale
        center_default = ((x_range[1] - x_range[0]) / 2, (y_range[1] - y_range[0]) / 2)
        return x_l, y_l, x_range, y_range, center_default

    def run(self):
        self.title_comp = st.title(TravelingPage.title)
        self.run_model_process()

        if self.model:
            v_df = self.model.viz_df.copy(deep=True)

            doc_el = st.empty()
            document_ids_selected = doc_el.multiselect('highlight document:', [''] + list(self.top2vec_model.document_ids))
            document_ids_selected = [str(d) for d in document_ids_selected]

            self.num_res = st.slider('number of results:', 0, self.num_res_max, 50, 1)
            self.num_res = int(self.num_res)

            zoom = st.slider('zoom:', -1., 10., 1., 0.5, '2**%f')
            fig_el = st.empty()
            if_display_text = st.checkbox('show text')

            x_l, y_l, x_total_range, y_total_range, center_default = self.display_range_and_center(v_df, zoom)
            center = self.app_url.sync_variable_list('center', [], center_default)
            center = [float(c) for c in center]

            ev, df_view = self.plot_at_center(center, fig_el, v_df, x_l, y_l,
                                              document_ids_selected=document_ids_selected,
                                              center_item_doc_id='',
                                              if_display_text=if_display_text)

            if ev:
                point = (ev[0]['x'], ev[0]['y'])
                df_view['x_diff'] = df_view.x - point[0]
                df_view['y_diff'] = df_view.y - point[1]
                df_view['dis_diff'] = abs(df_view['x_diff']) + abs(df_view['y_diff'])
                df_view = df_view.sort_values('dis_diff')
                df_sel = df_view.iloc[0:1].copy()
                df_sel['text'] = ''
                if df_sel.iloc[0]['node_type'] == 'document':
                    doc_id_sel = df_sel['name'].iloc[0]
                    doc_id_sel = self.model.transform_document_id(doc_id_sel)
                    doc_idx = self.model.top2vec_model.doc_id2index[doc_id_sel]
                    doc = self.top2vec_model.documents[doc_idx]
                    df_sel['text'] = [doc]
                st.write(df_sel[['name', 'text', 'x', 'y', 'score', 'topic_name']])
                if_move_center = st.button('move to above point')

                if if_move_center:
                    center_item_doc_id = df_sel['name'].iloc[0]
                    self.app_url.sync_variable_list('center', point, ())
                    ev, df_view = self.plot_at_center(point, fig_el, v_df, x_l, y_l,
                                                      document_ids_selected=document_ids_selected,
                                                      center_item_doc_id=center_item_doc_id,
                                                      if_display_text=if_display_text)

            st.write('no of displayed items:', df_view.shape[0])
            # st.write(document_ids_highlight)
            st.write(df_view)

