from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# Leer credenciales desde una variable de entorno
credentials_info = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
SPREADSHEET_ID = '1E-UUU_e234fj6H1xuqKFuzamiF0OQkJkuDbln53utUg'  # Reemplaza con tu propio ID de la hoja de cálculo

# Autenticación y construcción de servicio
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=SCOPES
)
service = build('sheets', 'v4', credentials=credentials)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    name = data.get('name')
    email = data.get('email')

    try:
        sheet = service.spreadsheets()
        range_name = 'Sheet1!A1:B1'  # Reemplaza 'Sheet1' con el nombre de tu hoja si es diferente
        values = [[name, email]]
        body = {'values': values}

        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        return jsonify({'status': 'success', 'data': result}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
