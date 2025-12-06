from flask import Flask, session
from flask_cors import CORS
import os

app = Flask(__name__)
app.secret_key = 'sdfasdsadsadaseqrfddfdfgrtbgbhgbnrt' # Needed for session management

# Configure CORS for frontend communication
CORS(app, supports_credentials=True)

# Register API blueprint
from api.ecg_routes import ecg_bp
app.register_blueprint(ecg_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
