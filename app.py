import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Inicializar la aplicación Dash con Bootstrap para facilitar la creación de layouts responsive
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Función que devuelve los gráficos y los datos
def create_dashboard(df, prediction_df, crypto_id, period):
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
            yaxis={'title': 'Precio en USD'},
            autosize=True,
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
            yaxis={'title': 'Precio en USD'},
            autosize=True,
        )
    }

    # Datos para la tabla de predicción
    prediction_table_data = prediction_df.to_dict('records')

    return sma_figure, prediction_figure, prediction_table_data

# Layout de la app con un diseño responsive
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard Criptomonedas"), width=12)
    ], justify='center'),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='sma-graph'), width=12, lg=6),  # Gráfico de medias móviles
        dbc.Col(dcc.Graph(id='prediction-graph'), width=12, lg=6)  # Gráfico de predicciones
    ], justify='center'),

    dbc.Row([
        dbc.Col(dbc.Table(id='prediction-table', striped=True, bordered=True, hover=True), width=12)
    ], justify='center')
], fluid=True)

# Callbacks para actualizar los gráficos y la tabla
@app.callback(
    [Output('sma-graph', 'figure'),
     Output('prediction-graph', 'figure'),
     Output('prediction-table', 'children')],
    [Input('crypto-dropdown', 'value'),
     Input('period-dropdown', 'value')]
)
def update_dashboard(crypto_id, period):
    # Cargar los datos aquí
    df = load_data(crypto_id, period)  # Función ficticia para cargar datos
    prediction_df = load_prediction_data(crypto_id)  # Función ficticia para cargar predicciones

    sma_figure, prediction_figure, prediction_table_data = create_dashboard(df, prediction_df, crypto_id, period)

    # Convertir los datos de la tabla en filas HTML
    table_header = [html.Thead(html.Tr([html.Th(col) for col in prediction_df.columns]))]
    table_body = [html.Tbody([html.Tr([html.Td(row[col]) for col in row]) for row in prediction_table_data])]

    return sma_figure, prediction_figure, table_header + table_body

if __name__ == '__main__':
    app.run_server(debug=True)
