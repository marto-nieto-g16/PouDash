from flask import Flask, render_template, request, flash
import yfinance as yf
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import plotly.graph_objs as go
import plotly.offline as pyo

app = Flask(__name__)
app.secret_key = '14151617080706'  # Necesario para mostrar mensajes de error

# Función para obtener el precio actual de una criptomoneda
def get_crypto_price(crypto_symbol):
    try:
        crypto = yf.Ticker(crypto_symbol)
        price_data = crypto.history(period='1d')
        if price_data.empty:
            return None
        price = price_data['Close'].iloc[-1]
        return f"${price:,.8f}"  # Formato con 8 decimales y símbolo de dólar para SHIB-USD
    except Exception as e:
        print(f"Error al obtener el precio: {e}")
        return None

# Función para obtener precios históricos de una criptomoneda
def get_historical_prices(crypto_symbol, days=30):
    try:
        crypto = yf.Ticker(crypto_symbol)
        historical_data = crypto.history(period=f'{days}d')
        if historical_data.empty:
            return None
        return historical_data['Close']
    except Exception as e:
        print(f"Error al obtener datos históricos: {e}")
        return None

# Función para predecir el precio con escalado
def predict_price(prices):
    # Escalado de los precios
    scaled_prices = prices / prices.max()

    model = ARIMA(scaled_prices, order=(5, 1, 0))  # Ajusta el orden según sea necesario
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=7)  # Predecir para los próximos 7 días
    
    # Revertir el escalado
    forecast_reverted = forecast * prices.max()
    return forecast_reverted

@app.route('/', methods=['GET', 'POST'])
def index():
    price = None
    crypto_symbol = None
    predictions_table = None
    graph = None

    if request.method == 'POST':
        crypto_symbol = request.form.get('crypto_id')
        if crypto_symbol:
            price = get_crypto_price(crypto_symbol)
            if price is None:
                flash('Error: No se pudo obtener el precio actual. Asegúrate de que el símbolo sea correcto.', 'danger')
            else:
                historical_prices = get_historical_prices(crypto_symbol)
                if historical_prices is None:
                    flash('Error: No se pudo obtener datos históricos. Asegúrate de que el símbolo sea correcto.', 'danger')
                else:
                    weekly_predictions = predict_price(historical_prices)

                    # Obtener fechas futuras para la predicción semanal
                    future_dates = [pd.Timestamp.now() + pd.Timedelta(days=i) for i in range(1, 8)]
                    future_dates_list = [date.strftime('%Y-%m-%d') for date in future_dates]

                    # Preparar la tabla de predicciones
                    predictions_table = list(zip(future_dates_list, weekly_predictions.tolist()))

                    # Obtener datos históricos para el gráfico (ajusta según tus datos)
                    yearly_prices = get_historical_prices(crypto_symbol, days=365)
                    yearly_predictions = predict_price(yearly_prices)

                    # Crear gráfico
                    trace1 = go.Scatter(
                        x=yearly_prices.index,
                        y=yearly_prices.values,
                        mode='lines+markers',
                        name='Histórico',
                        line=dict(color='royalblue', width=2),
                        marker=dict(size=5, symbol='circle')
                    )

                    trace2 = go.Scatter(
                        x=pd.date_range(start=yearly_prices.index[-1] + pd.Timedelta(days=1), periods=365, freq='D'),
                        y=yearly_predictions,
                        mode='lines+markers',
                        name='Predicción Anual',
                        line=dict(color='orange', width=2, dash='dash'),
                        marker=dict(size=5, symbol='square')
                    )

                    layout = go.Layout(
                        title=f'Precios de {crypto_symbol} (Histórico y Predicción)',
                        xaxis_title='Fecha',
                        yaxis_title='Precio (USD)',
                        legend=dict(x=0, y=1, traceorder='normal', orientation='h'),
                        hovermode='closest',
                        plot_bgcolor='rgba(240, 240, 240, 0.8)',
                        margin=dict(l=40, r=40, t=40, b=40)
                    )

                    fig = go.Figure(data=[trace1, trace2], layout=layout)
                    graph = pyo.plot(fig, output_type='div')

    return render_template('index.html', price=price, crypto_symbol=crypto_symbol, predictions_table=predictions_table, graph=graph)

if __name__ == '__main__':
    app.run(debug=True)
