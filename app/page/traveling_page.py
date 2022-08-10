from page.base_page import BasePage
from page.document_page import DocumentPage
import plotly.express as px
import streamlit as st
import pandas as pd
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go


def sampling_df(df, max_no):
    if df.shape[0] > max_no:
        stp = df.shape[0] // max_no
        return df.iloc[::stp]
    return df


class TravelingPage(BasePage):
    title = 'Traveling in data'

    def __init__(self, app_data, **kwargs):
        super().__init__(app_data, **kwargs)
        self.num_res_max = 1000
        self.column_for_text_display = ''

    def pickup_points(self, *args, **kwargs):
        return self.model.pickup_points(*args, **kwargs)

    def set_text(self, *args, **kwargs):
        return self.model.set_text(*args, **kwargs)

    def display_item(self, df_sel):
        df_sel['text'] = ''
        if df_sel.iloc[0]['node_type'] == 'document':
            doc_page = DocumentPage(app_data=self.app_data, app_url=self.app_url, model_name=self.model_name)
            doc_id_sel = df_sel['name'].iloc[0]
            doc_id_sel = self.model.transform_document_id(doc_id_sel)
            st.markdown('{} {}'.format(doc_id_sel, doc_page.document_link(doc_id_sel)))
            doc = self.model.document_from_id(doc_id_sel)
            st.write(doc[:300].replace('\n', ''))
            with st.expander('full text'):
                st.write(doc)
        else:
            st.write(df_sel[['name', 'text', 'x', 'y', 'score', 'topic_name', 'node_type']])
        return df_sel

    @staticmethod
    def item_df_from_document_ids(doc_ids, v_df):
        center_item_df = v_df[v_df['name'].isin(doc_ids)]
        return center_item_df

    def set_point_size(self, df):
        df['size'] = df['score'].apply(lambda x: max(x, 0.1))
        return df

    def plot_at_center_plotly_fig(self, center,
                                  v_df, x_l, y_l,
                                  highlight_item_df=pd.DataFrame(),
                                  if_display_text=False):
        hover_data = ['name', 'topic_id', 'topic_name']
        if 'keywords' in v_df.columns:
            hover_data += ['keywords']

        x_l *= 1.1
        y_l *= 1.1
        x_range = [center[0] - x_l / 2, center[0] + x_l / 2]
        y_range = [center[1] - y_l / 2, center[1] + y_l / 2]

        df_filter = v_df[(v_df.x < x_range[1]) & (v_df.x > x_range[0])]
        df_filter = df_filter[(df_filter.y < y_range[1]) & (df_filter.y > y_range[0])]

        df_filter['color'] = 'blue'
        df_filter = self.set_point_size(df_filter)
        df_view, _ = self.pickup_points(df=df_filter, split_no_x=self.num_res, split_no_y=self.num_res, x_range_l=x_l, y_range_l=y_l)

        additional_args = {}
        if if_display_text:
            df_view = self.set_text(df=df_view, split_no_x=30, split_no_y=30, x_range_l=x_l, y_range_l=y_l, use_text_label=self.column_for_text_display)
            additional_args['text'] = 'display_text'

        if highlight_item_df.shape[0]:
            highlight_item_df = highlight_item_df.copy()
            highlight_item_df = self.set_point_size(highlight_item_df)
            highlight_item_df['color'] = 'red'
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
                         hover_data=hover_data,
                         color_discrete_map={'red': 'red', 'blue': 'blue'},
                         symbol_map={
                             'topic': 'circle-open',
                             'document': 'x-open'
                         })
        return fig, df_view, df_filter

    def plot_at_center(self, center, fig_el, v_df, x_l, y_l,
                       items_selected,
                       center_item_doc_id='',
                       if_display_text=False):
        center_item_doc_id = self.app_url.sync_variable('center_item', center_item_doc_id, '')
        if center_item_doc_id in v_df.name.to_list():
            items_hightlight = items_selected + [center_item_doc_id]
        else:
            items_hightlight = items_selected

        highlight_item_df = self.item_df_from_document_ids(items_hightlight, v_df)

        fig, df_view, df_filter = self.plot_at_center_plotly_fig(center, v_df, x_l, y_l,
                                                                 highlight_item_df=highlight_item_df,
                                                                 if_display_text=if_display_text)
        with fig_el.container():
            ev = plotly_events(fig)

        return ev, df_view, df_filter

    def plot_distribution(self, df, el, df2=pd.DataFrame()):
        hover_data = ['name']
        if 'keywords' in df.columns:
            hover_data.append('keywords')
        title = ''
        df = sampling_df(df, 1000).copy()
        df_show = df
        if df2.shape[0]:
            df['color'] = 'not show'
            df2['color'] = 'showing'
            df_show = pd.concat([df, df2])
            title = '{} items in {} : {:.2}'.format(df2.shape[0], df.shape[0], df2.shape[0] / df.shape[0])
        fig = px.scatter(df_show, title=title, x='x', y='y', color='color', hover_data=hover_data,
                         color_discrete_map={'not show': 'green', 'showing': 'red'}, opacity=0.7)
        el.plotly_chart(fig)

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

    def travel_components(self, v_df):
        with st.expander('settings'):
            self.num_res = st.slider('number of results:', 0, self.num_res_max, 50, 1)
            self.num_res = int(self.num_res)
            if_show_dist = st.checkbox('show_distribution', True)
            self.column_for_text_display = 'name'
            if 'keywords' in v_df.columns:
                self.column_for_text_display = st.selectbox('column for text display', ['keywords', 'name'])

        doc_el = st.empty()
        items_selected = doc_el.multiselect('hightlight items:', [''] + list(v_df.name.to_list()))
        items_selected = [str(i) for i in items_selected]

        zoom = st.slider('zoom:', -1., 10., 1., 0.5, '2**%f')
        fig_el = st.empty()
        if_display_text = True

        x_l, y_l, x_total_range, y_total_range, center_default = self.display_range_and_center(v_df, zoom)
        center = self.app_url.sync_variable_list('center', [], center_default)
        center = [float(c) for c in center]
        if not (center[0] > x_total_range[0] and center[0] < x_total_range[1] and center[1] > y_total_range[0] and center[1] < y_total_range[1]):
            center = self.app_url.sync_variable_list('center', center_default, center_default)

        ev, df_view, df_fileter = self.plot_at_center(center, fig_el, v_df, x_l, y_l,
                                                      items_selected=items_selected,
                                                      center_item_doc_id='',
                                                      if_display_text=if_display_text)

        if ev:
            point = (ev[0]['x'], ev[0]['y'])
            df_view['x_diff'] = df_view.x - point[0]
            df_view['y_diff'] = df_view.y - point[1]
            df_view['dis_diff'] = abs(df_view['x_diff']) + abs(df_view['y_diff'])
            df_view = df_view.sort_values('dis_diff')
            df_sel = df_view.iloc[0:1].copy()

            df_sel = self.display_item(df_sel)

            if_move_center = st.button('move to above point')
            if if_move_center:
                center_item_doc_id = df_sel['name'].iloc[0]
                self.app_url.sync_variable_list('center', point, ())
                ev, df_view, df_fileter = self.plot_at_center(point, fig_el, v_df, x_l, y_l,
                                                              items_selected=items_selected,
                                                              center_item_doc_id=center_item_doc_id,
                                                              if_display_text=if_display_text)
        if if_show_dist:
            dist_el, contour_el = st.columns(2)
            self.plot_distribution(df_fileter, dist_el, df_view)
            self.plot_contour(v_df, contour_el, df_fileter, df_view)

        st.write('no of displayed items:', df_view.shape[0])
        st.write(df_view)

    def plot_contour(self, v_df, el, df2=pd.DataFrame(), df3=pd.DataFrame()):
        if 'keywords' in v_df.columns:
            hover_column = 'keywords'
        else:
            hover_column = 'name'

        n_bins = st.slider('contour bins', 10, 100, 20, 1)
        fig = go.Figure()
        fig.add_trace(go.Histogram2dContour(
            x=v_df.x,
            y=v_df.y,
            nbinsx=n_bins,
            nbinsy=n_bins,
            colorscale='Blues',
            reversescale=True,
            xaxis='x',
            yaxis='y'
        ))
        v_df = sampling_df(v_df, 300)
        fig.add_trace(go.Scatter(
            x=v_df.x,
            y=v_df.y,
            xaxis='x',
            yaxis='y',
            text=v_df[hover_column],
            hovertemplate='%{text}',
            mode='markers',
            marker=dict(
                color='white',
                size=3
            ),
            opacity=0.7
        ))

        df2 = sampling_df(df2, 300)
        if df2.shape[0]:
            fig.add_trace(go.Scatter(
                x=df2.x,
                y=df2.y,
                text=df2[hover_column],
                hovertemplate='%{text}',
                xaxis='x',
                yaxis='y',
                mode='markers',
                marker=dict(
                    color='yellow',
                    size=3
                ),
                opacity=0.7
            ))
        if df3.shape[0]:
            fig.add_trace(go.Scatter(
                x=df3.x,
                y=df3.y,
                text=df3[hover_column],
                hovertemplate='%{text}',
                xaxis='x',
                yaxis='y',
                mode='markers',
                marker=dict(
                    color='red',
                    size=3
                )
            ))

        fig.update_layout(
            autosize=False,
            xaxis=dict(
                zeroline=False,
                domain=[0, 0.85],
                showgrid=False
            ),
            yaxis=dict(
                zeroline=False,
                domain=[0, 0.85],
                showgrid=False
            ),
            # height=600,
            # width=600,
            bargap=0,
            hovermode='closest',
            showlegend=False
        )

        # fig = px.density_contour(v_df, x="x", y="y")
        # fig.update_traces(contours_coloring="fill", contours_showlabels=True)
        el.plotly_chart(fig)

    def run(self):
        self.title_comp = st.title(TravelingPage.title)
        self.run_model_process()

        if self.model:
            v_df = self.model.viz_df.copy(deep=True)
            self.travel_components(v_df)



