from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app) # Abilita il CORS per le chiamate da JavaScript

IBAN_LENGTHS = { 'IT': 27, 'DE': 22, 'FR': 27, 'ES': 24, 'GB': 22 }

def validate_iban(iban: str) -> bool:
    if not isinstance(iban, str): return False
    iban_cleaned = re.sub(r'\s+', '', iban).upper()
    country_code = iban_cleaned[:2]
    if not country_code.isalpha() or len(iban_cleaned) != IBAN_LENGTHS.get(country_code, -1):
        return False
    rearranged_iban = iban_cleaned[4:] + iban_cleaned[:4]
    numeric_iban = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged_iban)
    try:
        return int(numeric_iban) % 97 == 1
    except (ValueError, TypeError):
        return False

@app.route('/validate', methods=['POST', 'OPTIONS'])
def handle_validation():
    if request.method == 'OPTIONS':
        return '', 204 # Gestisce la richiesta preflight CORS

    data = request.get_json()
    if not data or 'iban' not in data:
        return jsonify({'error': 'IBAN non fornito'}), 400

    iban_to_check = data['iban']
    is_valid = validate_iban(iban_to_check)
    status = 'Valido' if is_valid else 'Non Valido'

    return jsonify({ 'status': status, 'iban': iban_to_check })

if __name__ == '__main__':
    # Questo blocco non è usato da Render, ma è utile per test locali
    app.run(host='0.0.0.0', port=5000)
