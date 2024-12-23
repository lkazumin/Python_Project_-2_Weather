import plotly.graph_objs as go
from config import Config

parameters_map = Config.parameters_map


def make_weather_graph(all_weather_data, selected_graphs):
    dates = all_weather_data[0]['date']

    all_graphs = []
    for selected_graph in selected_graphs:
        fig = go.Figure()
        # Линии полудня
        for x in dates[12::24]:
            fig.add_vline(x=x, line_color='orange', opacity=0.5, name='Полдень')
        # Линии полуночи
        for x in dates[0::24]:
            fig.add_vline(x=x, line_color='black', opacity=0.5, name='Полночь')

        # Отрисовка графиков
        for index, df in enumerate(all_weather_data, 1):
            fig.add_scatter(x=df["date"], y=df[selected_graph], name=f"Точка {index}", mode='lines+markers')

        fig.update_layout(
            title=', '.join(parameters_map[selected_graph]),
            showlegend=True
        )
        all_graphs.append(fig)
    return all_graphs
