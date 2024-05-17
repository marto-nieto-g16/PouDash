import dash
import plotly.graph_objs as go
import requests
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from dash import dcc, html, dash_table, Input, Output, State


# Obtener datos de la criptomoneda
def obtener_datos_criptomoneda(crypto_id, days):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}&interval=daily'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['volume'] = [v[1] for v in data['total_volumes']]
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame(columns=['timestamp', 'price', 'volume'])

# Calcular medias móviles
def calcular_sma(df, window):
    df[f'SMA_{window}'] = df['price'].rolling(window=window).mean()
    return df

# Predicción de precios utilizando ARIMA
def predecir_precio(df):
    try:
        model = ARIMA(df['price'], order=(5, 1, 0))
        model_fit = model.fit()
        
        # Predecir los próximos 7 días
        forecast = model_fit.forecast(steps=7)
        
        future_dates = pd.date_range(df['timestamp'].max() + pd.Timedelta(days=1), periods=7)
        
        prediction_df = pd.DataFrame({
            'Fecha': future_dates,
            'Precio Predicho': forecast
        })
        
        return prediction_df
    except Exception as e:
        print(f"Error al predecir precios: {e}")
        return pd.DataFrame(columns=['Fecha', 'Precio Predicho'])


# Crear la aplicación Dash
app = dash.Dash(__name__, title= 'Pou dash')
server = app.server

# Contenido del layout
app.layout = html.Div(children=[
    html.Link(
        rel='stylesheet', href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
    ),
    html.Br(),
    html.H1(children='Análisis de Criptomonedas en Tiempo Real', className='text-center mb-4'),

    html.Div(className='container', children=[
        html.Div(className='row justify-content-center mb-3', children=[
            dcc.Input(
                id='input-crypto',
                type='text',
                placeholder='Ingrese el nombre o símbolo de la criptomoneda',
                value='bitcoin',
                className='form-control mr-2'
            ),


            dcc.RadioItems(
                id='radio-period',
                options=[
                    {'label': '1 Mes', 'value': '30'},
                    {'label': '3 Meses', 'value': '90'},
                    {'label': '6 Meses', 'value': '180'},
                    {'label': '1 Año', 'value': '365'}
                ],
                value='30',
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            ), 

            html.Button(id='submit-button', n_clicks=0, children='Submit', className='btn btn-primary')
        ]),

        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # Actualizar cada minuto
            n_intervals=0
        ),

        html.Div(className='row justify-content-center mb-3', children=[
            dcc.Graph(id='price-graph', className='col-md-6 mb-3'),
            dcc.Graph(id='volume-graph', className='col-md-6 mb-3'),
            dcc.Graph(id='sma-graph', className='col-md-6 mb-3'),
            dcc.Graph(id='prediction-graph', className='col-md-6 mb-3')
        ]),

        html.Div(className='container', children=[
            html.H3(children='Precios Predichos para los Próximos 7 Días', className='mb-3'),
            dash_table.DataTable(
                id='prediction-table',
                columns=[{'name': 'Fecha', 'id': 'Fecha'}, {'name': 'Precio Predicho', 'id': 'Precio Predicho'}],
                style_table={'margin': 'auto', 'width': '50%'},
                style_cell={'textAlign': 'center'}  
            )
        ])
    ]),

    html.Footer([
        html.Div([
            html.P("Para donaciones: Dirección BTC: 1AGjmwbDJWjmBLqxXNMvkpLvzto2x43w3V", className='mb-0'),
            html.P([
                html.A(html.I(className="fa fa-twitter"), href="https://twitter.com/marto_nieto", target="_blank"),
                html.A("Twitter del desarrollador", href="https://twitter.com/marto_nieto", target="_blank", className='ml-2'),
            ], className='mb-0'),
            html.P(html.A("Repositorio en GitHub", href="#", target="_blank", className='ml-2'), className='mb-0')
        ], className='text-center')
    ], className='container mt-5')
])


@app.callback(
    [Output('price-graph', 'figure'),
     Output('volume-graph', 'figure'),
     Output('sma-graph', 'figure'),
     Output('prediction-graph', 'figure'),
     Output('prediction-table', 'data')],
    [Input('submit-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('input-crypto', 'value'),
     State('radio-period', 'value')]
)
def actualizar_graficos(n_clicks, n_intervals, crypto_id, period):
    df = obtener_datos_criptomoneda(crypto_id, period)
    if df.empty:
        return {}, {}, {}, {}, []

    df = calcular_sma(df, 30)
    df = calcular_sma(df, 90)
    prediction_df = predecir_precio(df)

    # Gráfico de precios
    price_figure = {
        'data': [
            go.Scatter(
                x=df['timestamp'],
                y=df['price'],
                mode='lines',
                name='Precio'
            )
        ],
        'layout': go.Layout(
            title=f'Precio de {crypto_id.capitalize()} en los últimos {period} días',
            xaxis={'title': 'Fecha'},
            yaxis={'title': 'Precio en USD'}
        )
    }

    # Gráfico de volumen
    volume_figure = {
        'data': [
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volumen'
            )
        ],
        'layout': go.Layout(
            title=f'Volumen de Transacciones de {crypto_id.capitalize()} en los últimos {period} días',
            xaxis={'title': 'Fecha'},
            yaxis={'title': 'Volumen'}
        )
    }

    # Gráfico de medias móviles
    sma_figure = {
        'data': [
            go.Scatter(
                x=df['timestamp'],
                y=df['price'],
                mode='lines',
                name='Precio'
            ),
            go.Scatter(
                x=df['timestamp'],
                y=df['SMA_30'],
                mode='lines',
                name='SMA 30 días'
            ),
            go.Scatter(
                x=df['timestamp'],
                y=df['SMA_90'],
                mode='lines',
                name='SMA 90 días'
            )
        ],
        'layout': go.Layout(
            title=f'Medias Móviles de {crypto_id.capitalize()} en los últimos {period} días',
            xaxis={'title': 'Fecha'},
            yaxis={'title': 'Precio en USD'}
        )
    }

    # Gráfico de predicción de precios
    prediction_figure = {
        'data': [
            go.Scatter(
                x=df['timestamp'],
                y=df['price'],
                mode='lines',
                name='Precio Actual'
            ),
            go.Scatter(
                x=prediction_df['Fecha'],
                y=prediction_df['Precio Predicho'],
                mode='lines',
                name='Predicción de Precio'
            )
        ],
        'layout': go.Layout(
            title=f'Predicción del Precio de {crypto_id.capitalize()} para los Próximos 7 Días',
            xaxis={'title': 'Fecha'},
            yaxis={'title': 'Precio en USD'}
        )
    }

    # Datos para la tabla de predicción
    prediction_table_data = prediction_df.to_dict('records')

    return price_figure, volume_figure, sma_figure, prediction_figure, prediction_table_data

if __name__ == '__main__':
    app.run_server(debug=True)
