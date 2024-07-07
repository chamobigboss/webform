from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask_cors import CORS
import os
import json
import logging

app = Flask(__name__)
CORS(app)

# Configurar el nivel de registro
logging.basicConfig(level=logging.DEBUG)

# Leer credenciales desde una variable de entorno
try:
    credentials_info = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
    app.logger.debug('Credenciales cargadas correctamente')
except Exception as e:
    app.logger.error('Error al cargar credenciales: %s', e)

SPREADSHEET_ID = '1E-UUU_e234fj6H1xuqKFuzamiF0OQkJkuDbln53utUg'  # Reemplaza con tu propio ID de la hoja de cálculo

# Autenticación y construcción de servicio
try:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    app.logger.debug('Servicio de Google Sheets construido correctamente')
except Exception as e:
    app.logger.error('Error al construir el servicio de Google Sheets: %s', e)

# Ruta para obtener datos de una hoja específica
@app.route('/data/<sheet_name>', methods=['GET'])
def get_data(sheet_name):
    try:
        sheet = service.spreadsheets()
        range_name = f'{sheet_name}!A1:Z'  # Ajusta el rango según tus necesidades
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        return jsonify({'status': 'success', 'data': values}), 200
    except Exception as e:
        app.logger.error(f'Error al obtener datos de {sheet_name}: %s', e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Ruta para actualizar datos en una hoja específica
@app.route('/update/<sheet_name>', methods=['POST'])
def update_data(sheet_name):
    try:
        data = request.json
        index = data.get('index')
        updated_data = data.get('updatedData')

        sheet = service.spreadsheets()
        range_name = f'{sheet_name}!A{index+1}:Z{index+1}'  # Ajusta el rango según tus necesidades

        values = [updated_data]
        body = {'values': values}

        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        return jsonify({'status': 'success', 'data': result}), 200
    except Exception as e:
        app.logger.error(f'Error al actualizar datos en {sheet_name}: %s', e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Ruta para enviar nuevos datos a una hoja específica
@app.route('/submit/<sheet_name>', methods=['POST'])
def submit(sheet_name):
    try:
        data = request.json
        app.logger.debug(f'Datos recibidos para {sheet_name}: %s', data)
        
        sheet = service.spreadsheets()
        range_name = f'{sheet_name}!A1:Z1'  # Ajusta el rango según tus necesidades
        values = [data]  # Suponiendo que los datos están en un formato adecuado
        body = {'values': values}

        app.logger.debug(f'Enviando datos a Google Sheets: {values}')
        
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        app.logger.debug(f'Resultado de Google Sheets: {result}')

        return jsonify({'status': 'success', 'data': result}), 200
    except Exception as e:
        app.logger.error(f'Error al enviar datos a {sheet_name}: %s', e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
