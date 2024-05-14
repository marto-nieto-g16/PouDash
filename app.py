import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import yfinance as yf
import statsmodels.api as sm
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Función para calcular el RSI
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Crear la aplicación Dash
app = dash.Dash(__name__, title="Pou Dash")
server = app.server

# Diseño de la aplicación
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Link(
        rel='stylesheet', href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
        ),
    html.Br(),
    html.H1("Predicción de Precios de Criptomonedas", className='text-center'),
    html.Label('Símbolo de la Criptomoneda', className='text-center'),
    dcc.Input(id="input-symbol", type="text", placeholder="BTC-USD", className='text-center', autoFocus=True),
    html.Button(id='submit-button', n_clicks=0, children='Buscar', style={'display': 'none'}),
    dcc.Graph(id="price-chart"),
    html.Div(id="prediction-text", className='text-center'),
    html.Footer([
        html.Div("Para donaciones: Dirección BTC: 1AGjmwbDJWjmBLqxXNMvkpLvzto2x43w3V", className='text-center'),
        html.A(html.I(className="fa fa-twitter"), href="https://twitter.com/marto_nieto_g", target="_blank", className='ml-2'),
        html.A("Twitter desarollador", href="https://twitter.com/marto_nieto_g", target="_blank", className='ml-1'),
        html.A("Repositorio en GitHub", href="#", target="_blank", className='ml-2')
    ], className='text-center mt-5', style={'margin-bottom': '50px'})
], className='container-fluid')

# Callback para actualizar el gráfico y mostrar predicciones
@app.callback(
    [Output("price-chart", "figure"),
     Output("prediction-text", "children"),
     Output("submit-button", "n_clicks")],
    [Input("input-symbol", "n_submit")],
    [State("input-symbol", "value")]
)
def update_chart(n_submit, symbol):
    if n_submit and symbol:
        try:
            # Obtener fecha actual del sistema
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)  # Datos históricos del último año

            # Obtener datos históricos
            data = yf.download(symbol, start=start_date, end=end_date)

            # Calcular indicadores (EMA, RSI)
            data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
            data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
            data['RSI'] = calculate_rsi(data['Close'])

            # Modelo ARIMA
            model = sm.tsa.ARIMA(data['Close'], order=(5,1,0))
            results = model.fit()

            # Predicciones
            current_close_prediction = data['Close'].iloc[-1]  # Predicción del precio de cierre para la fecha actual
            next_year_prediction = results.forecast(steps=365)[0]  # Predicción para el próximo año

            # Gráfico
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines+markers', name='Precio de Cierre'))
            fig.add_trace(go.Scatter(x=[end_date], y=[current_close_prediction], mode='markers', name='Precio de Cierre Actual', marker=dict(color='red', size=10)))
            fig.add_trace(go.Scatter(x=[end_date + timedelta(days=365)], y=[next_year_prediction], mode='markers', name='Predicción para el próximo año', marker=dict(color='green', size=10)))
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA_20'], mode='lines', name='EMA 20'))
            fig.add_trace(go.Scatter(x=data.index, y=data['EMA_50'], mode='lines', name='EMA 50'))
            fig.update_layout(title=f"Datos Históricos de {symbol} {start_date} - {end_date}",
                              xaxis_title="Fecha",
                              yaxis_title="Precio",
                              showlegend=True)

            # Texto de predicciones
            prediction_text = [
                html.P(f"Predicción del precio de cierre para la fecha actual ({end_date.strftime('%Y-%m-%d')}): ${current_close_prediction:.9f} USD"),
                html.P(f"Predicción para el próximo año ({end_date.year + 1}): ${next_year_prediction:.9f} USD aproximadamente")
            ]

            return fig, prediction_text, 0
        except Exception as e:
            error_message = f"Error al obtener datos para la criptomoneda: '{symbol}'"
            return {}, [html.P(error_message, style={"color": "red"})], 0
    else:
        return {}, "", 0

if __name__ == "__main__":
    app.run_server(debug=True)
