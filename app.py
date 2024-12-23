import dash
from dash import html, dcc, Input, Output, State, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import logging
from config import Config
import open_meteo
import plotly.graph_objs as go
import plotly_graphs


app = dash.Dash(__name__)

parameters_map = Config.parameters_map

div_stile = {
    'margin-top': '20px',
    'border': '2px solid black',  # Толщина и цвет рамки
    'padding': '10px',            # Внутренний отступ
    'border-radius': '5px',       # Закругленные углы
    'width': '300px',             # Ширина рамки
}


app.layout = html.Div([
    # Выбор отображаемых графиков
    html.Div(
        [
            html.H3("Выбор графиков"),
            dcc.Checklist(
                id='graph-checklist',
                options=[
                    {'label': v[0], 'value': k} for k, v in parameters_map.items()
                ],
                value=["temperature"],
                inline=True
            )
        ],
        style=div_stile
    ),

    # Выбор количества дней для прогноза
    html.Div(
        [
            html.H3("Количество дней для прогноза"),
            dcc.Input(
                id='forecast_days',
                type='number',
                value=4,
                min=1,
                max=16,
                step=1,
                style={'margin-top': '20px'}
            )
        ],
        style=div_stile
    ),

    # Добавление и удаление точек маршрута
    html.Div(
        [
            html.H3("Широта и долгота точки маршрута(от -90 до 90): "),
            html.H4('', id='error'),
            dbc.Row([
                dbc.Col(dbc.Input(id='latitude', placeholder='Широта', type='number', min=-90, max=90)),
                dbc.Col(dbc.Input(id='longitude', placeholder='Долгота', type='number', min=-90, max=90)),
                dbc.Col(dbc.Button("Добавить точку", id='add-button', n_clicks=0))
            ]),
        ],
        id='add_points',
        style=div_stile
    ),


    dcc.Store(
        id='points_list',
        data=[]
    ),
    html.Div(
        [
            html.H3("Добавленные точки маршрута:"),
            html.Div(
                id='points_cards'
            ),
        ],
        style=div_stile
    ),

    # Карта
    html.Div(
        [
            dbc.Checklist(
                id='show_map',
                options=[{'label': 'Показать/Скрыть карту', 'value': 'show'}],
                value=['show']
            ),
        ],
        style=div_stile
    ),

    html.Div(id='route_map'),

    # Вывод графиков
    html.Div(id='output-graphs')
])


# Добавление точек
@app.callback(
    Output('points_cards', 'children'),
    Input('points_list', 'data')
)
def show_cards(points_list):
    cards = [
        dbc.Card([
            dbc.CardHeader(f"Точка {i + 1}"),
            dbc.CardBody([
                html.P(f"Широта: {lat}; Долгота: {lon}"),
                dbc.Button("Удалить", id={'type': 'delete-button', 'index': i}, n_clicks=0)
            ])
        ],
        style={
            'margin-top': '20px',
            'border': '1px solid gray',
            'padding': '5px',
            'border-radius': '5px',
            'width': '200px',
        }
        )
        for i, (lat, lon) in enumerate(points_list)
    ]
    return cards


@app.callback(  # Новая точка
    Output('points_list', 'data', allow_duplicate=True),
    Output('error', 'children'),
    Input('add-button', 'n_clicks'),
    State('points_list', 'data'),
    State('latitude', 'value'),
    State('longitude', 'value'),
    prevent_initial_call=True
)
def update_points(n_clicks, points_list, lat, lon):
    error = ''
    if lat is not None and lon is not None:
        if [lat, lon] not in points_list:
            try:
                points_list.append([lat, lon])
            except RuntimeError as e:
                logging.error(e)
                error = str(e)
    return points_list, error


@app.callback(
    Output('points_list', 'data'),
    Input({'type': 'delete-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('points_list', 'data'),
)
def delete_point(n_clicks, points_list):
    if not all(n is None for n in n_clicks):
        index_to_delete = [i for i, n in enumerate(n_clicks) if n]
        if index_to_delete:
            # Удаляем последнюю нажатую кнопку
            last_index = max(index_to_delete)
            points_list.pop(last_index)

    return points_list


# Отображение карты
@app.callback(
    Output('route_map', 'style'),
    Input('show_map', 'value')
)
def show_map(value):
    if 'show' in value:
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(
    Output('route_map', 'children'),
    Input('points_list', 'data')
)
def create_map(points_list):
    if not points_list:
        return None
    latitudes, longitudes = zip(*points_list)
    fig = go.Figure(go.Scattermapbox(
        lon=longitudes,
        lat=latitudes,
        mode='markers',
        marker=dict(size=10),
        customdata=list(range(1, len(latitudes)+1)),
        hovertemplate="<b>Точка %{customdata}</b><br>" +
                      "Longitude: %{lon}<br>" +
                      "Latitude: %{lat}<br><extra></extra>"

    ))
    fig.update_layout(
        mapbox=dict(
            style='carto-positron',  # Стиль карты
            center=dict(lat=latitudes[0], lon=longitudes[0]),  # Центр карты
            zoom=5  # Уровень приближения
        ),
        margin=dict(t=10, b=10, l=10, r=10)  # Отступы от границ фигуры
    )
    return dcc.Graph(figure=fig)


# Отображение графиков
@app.callback(
    Output('output-graphs', 'children'),
    Input('graph-checklist', 'value'),
    Input('forecast_days', 'value'),
    Input('points_list', 'data')
)
def update_graphs(selected_graphs, forecast_days, points_list):
    graphs = []
    if not points_list:
        return None
    latitudes, longitudes = zip(*points_list)

    try:
        weather_data = open_meteo.get_weather(latitudes, longitudes, forecast_days)
    except RuntimeError as e:
        return html.H2(f"Ошибка при получении погоды:\n {e}")


    graphs = plotly_graphs.make_weather_graph(weather_data, selected_graphs)
    graphs = [dcc.Graph(figure=fig) for fig in graphs]
    return graphs


if __name__ == '__main__':
    app.run_server(debug=True, host=Config.url, port=Config.port)

