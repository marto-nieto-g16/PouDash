import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.graph_objs as go
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

# Obtener datos históricos de Yahoo Finance
def get_historical_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date, interval='1d')
    return data

# Predecir precio utilizando ARIMA
def predict_price(data, steps):
    if data.empty:
        return None
    model = ARIMA(data['Close'], order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    return forecast[-1]

# Obtener fecha actual del sistema
current_date = datetime.now().date()

# Obtener fecha hace 6 meses
start_date = current_date - timedelta(days=180)

# Inicializar la aplicación Dash
app = dash.Dash(__name__, )
app.Title = "Pou Dash"

server = app.server

# Diseño de la aplicación web
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
        html.Link(
            rel='stylesheet',
            href='https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
        ),
    html.Br(),
    html.H1('Predicción de Precio de Criptomoneda', className='text-center'), html.Br(),
    html.Label('Símbolo de la Criptomoneda', className='text-center'),
    dcc.Input(id='symbol-input', type='text', value='BTC-USD', className='text-center'),
    dcc.Graph(id='historical-graph'),
    html.Div(id='next-day-prediction', className='text-center'),
    html.Div(id='next-year-prediction', className='text-center'),
    html.Footer([
        html.Div("Para donaciones: Dirección BTC: 1AGjmwbDJWjmBLqxXNMvkpLvzto2x43w3V", className='text-center'),
        html.A(html.I(className="fa fa-twitter"), href="https://twitter.com/marto_nieto_g", target="_blank", className='ml-2'),
        html.A("Twitter desarollador", href="https://twitter.com/marto_nieto_g", target="_blank", className='ml-1'),
        html.A("Repositorio en GitHub", href="#", target="_blank", className='ml-2')
    ], className='text-center mt-5', style={'margin-bottom': '50px'})
], className='container-fluid')

# Callback para actualizar el gráfico histórico y las predicciones
@app.callback(
    [Output('historical-graph', 'figure'),
     Output('next-day-prediction', 'children'),
     Output('next-year-prediction', 'children')],
    [Input('symbol-input', 'value')]
)
def update_data_and_predictions(symbol):
    next_year_prediction = ""  # Inicializar la variable con una cadena vacía
    # Obtener datos históricos actualizados
    historical_data = get_historical_data(symbol, start_date, current_date)
    if historical_data.empty:
        return {}, "No se encontraron datos para el símbolo ingresado.", "No se encontraron datos para el símbolo ingresado."
    # Predecir precio para el próximo día
    next_day_price = predict_price(historical_data, steps=1)
    # Predecir precio para el próximo año
    next_year_price = predict_price(historical_data, steps=365)
    # Determinar si el precio predicho para el próximo año es alcista o bajista
    if next_year_price is not None and historical_data['Close'].iloc[-1] is not None:
        if next_year_price > historical_data['Close'].iloc[-1]:
            trend_next_year = 'Alcista'
        elif next_year_price < historical_data['Close'].iloc[-1]:
            trend_next_year = 'Bajista'
        else:
            trend_next_year = 'Estable'
        
    # Crear gráfico histórico y otras actualizaciones
    historical_graph = go.Figure()
    historical_graph.add_trace(go.Scatter(x=historical_data.index, y=historical_data['Close'], mode='lines', name='Precio de Cierre'))
    if next_day_price is not None:
        next_day = current_date + timedelta(days=1)
        historical_graph.add_trace(go.Scatter(x=[next_day], y=[next_day_price], mode='markers', name='Predicción para mañana', marker=dict(color='red')))
    historical_graph.update_layout(title=f'Histórico de Precio de {symbol} ({start_date} - {current_date})', xaxis=dict(title='Fecha'), yaxis=dict(title='Precio (USD)'), title_x=0.5)
    if next_day_price is None:
        next_day_prediction = "No se puede predecir el precio para el próximo día."
    else:
        next_day = current_date.day + 1
        next_day_prediction = f'El precio de {symbol} para mañana ({next_day} - {current_date.month} - {current_date.year}) será: {next_day_price:.10f} USD'
    if next_year_price is None:
        next_year_prediction = "No se puede predecir el precio para el próximo año."
    else:
        next_year = current_date.year + 1
        next_year_prediction += f'\nEl precio de {symbol} para el año {next_year} será: {next_year_price:.10f} USD, Tendencia: {trend_next_year}'
    return historical_graph, next_day_prediction, next_year_prediction

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
