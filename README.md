# PouDash

¡Bienvenido a nuestro proyecto de predicción de precios de criptomonedas! Este proyecto tiene como objetivo proporcionar a los usuarios una herramienta para analizar y predecir los precios de criptomonedas utilizando datos históricos y técnicas de análisis avanzadas.

## Características Principales

- **Predicción de Precios:** Utilizamos modelos ARIMA para predecir el precio de cierre de una criptomoneda para la fecha actual y el próximo año.
- **Indicadores Técnicos:** Calculamos y visualizamos medias móviles exponenciales (EMA) de 20 y 50 períodos, así como el índice de fuerza relativa (RSI) de 14 períodos.
- **Actualización en Tiempo Real:** La aplicación se actualiza automáticamente cuando se presiona la tecla "Enter" después de ingresar el símbolo de la criptomoneda.
- **Manejo de Errores Mejorado:** Implementamos un manejo mejorado de errores para guiar a los usuarios en caso de ingresar incorrectamente un símbolo de criptomoneda.

## Uso

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias utilizando `pip install -r requirements.txt`.
3. Ejecuta la aplicación utilizando `python app.py`.
4. Abre tu navegador y navega a `http://localhost:8050`.

## Tecnologías Utilizadas

- [Dash](https://dash.plotly.com/) - Framework de Python para la creación de aplicaciones web interactivas.
- [Yahoo Finance](https://pypi.org/project/yfinance/) - Para obtener datos históricos de precios de criptomonedas.
- [Statsmodels](https://www.statsmodels.org/stable/index.html) - Para el modelado de series temporales y análisis de datos estadísticos.
- [Plotly](https://plotly.com/python/) - Para la visualización de datos interactiva.

## Contribuir

¡Estamos abiertos a contribuciones! Si tienes alguna idea para mejorar este proyecto, siéntete libre de abrir un PR o una issue.

## Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](LICENSE).

¡Gracias por tu interés en nuestro proyecto! Si tienes alguna pregunta o sugerencia, no dudes en contactarnos.

---

¡Puedes personalizar este README según las necesidades específicas de tu proyecto! Siéntete libre de agregar más detalles, instrucciones de instalación, ejemplos de uso, capturas de pantalla, etc.
