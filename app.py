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

SPREADSHEET_ID = '1a2b3c4d5e6f7g8h9i0j'  # Reemplaza con tu propio ID de la hoja de cálculo

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

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        app.logger.debug('Datos recibidos: %s', data)
        name = data.get('name')
        email = data.get('email')

        sheet = service.spreadsheets()
        range_name = 'Sheet1!A1:B1'  # Reemplaza 'Sheet1' con el nombre de tu hoja si es diferente
        values = [[name, email]]
        body = {'values': values}
        
        app.logger.debug('Enviando datos a Google Sheets: %s', values)
        
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        app.logger.debug('Resultado de Google Sheets: %s', result)

        return jsonify({'status': 'success', 'data': result}), 200
    except Exception as e:
        app.logger.error('Error al enviar datos a Google Sheets: %s', e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/data', methods=['GET'])
def get_data():
    try:
        sheet = service.spreadsheets()
        range_name = 'Sheet1!A1:B'  # Reemplaza 'Sheet1' con el nombre de tu hoja si es diferente
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        return jsonify({'status': 'success', 'data': values}), 200
    except Exception as e:
        app.logger.error('Error al obtener datos de Google Sheets: %s', e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/update', methods=['POST'])
def update_data():
    try:
        data = request.json
        index = data.get('index')
        updated_data = data.get('updatedData')

        sheet = service.spreadsheets()
        range_name = f'Sheet1!A{index+1}:B{index+1}'  # Ajusta el rango según tus necesidades

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
        app.logger.error('Error al actualizar datos en Google Sheets: %s', e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
