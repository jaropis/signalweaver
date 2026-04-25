from flask import Flask, config, session
from flask_cors import CORS
import os

from auth import auth
from auth.config import AuthConfig
from datetime import datetime, timezone
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from auth.config import AuthConfig
from auth.auth import AuthService
from auth.blueprint import create_auth_blueprint
from api.ecg_routes import ecg_bp

def create_app():
    """
    Application factory - creates and configures the Flask app.

    Flask's application factory pattern is the recommended way to
    structure Flask apps. It makes testing easier (you can create
    apps with different configs) and avoids circular imports.
    """
    app = Flask(__name__)
    # --- Configuration ---
    # In development, I  pass values directly
    # in Production, I use environmet variables (AuthConfig.from_env())
    config = AuthConfig(
        jwt_secret_key='alsdkjf-sldfj-ekjd-alkdfjoe',
        database_path ='users.db',
        frontend_url='http://localhost:5173', # Vue dev server
        cors_allowed_origins=[
            'http://localhost:5173', # Vite dev server,
            'http://localhost:3000', # Alternative dev port
        ]
    )

    # Flask needs the JWT secret key in its own config
    app.config['JWT_SECRET_KEY'] = config.jwt_secret_key

    # Configuring access token expiry for Flask-JWT-Extended
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.access_token_expires
    app.secret_key = 'sdfasdsadsadaseqrfddfdfgrtbgbhgbnrt' # Needed for session management

    # Configure CORS for frontend communication
    if config.cors_allowed_origins:
        CORS(app, origins=config.cors_allowed_origins, supports_credentials=True)
    else:
        CORS(
            app,
            supports_credentials=True
        )
    # --- JWT Manager ---
    jwt = JWTManager(app)

    # --- Auth Service ---
    auth_service = AuthService(config)

    # --- JWT Callbacks ---
    # Flask-JWT-Extended calls this function automatically on every
    # request to a @jwt_required() endpoint. If it returns True,
    # the request is rejected with 401
    @jwt.token_in_blocklist_loader
    def check_if_toke_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        email = jwt_payload['sub']
        toke_issued_at = datetime.fromtimestamp(
            jwt_payload['iat'], tz=timezone.utc
        )

        # Check 1: Is this specific token blacklisted? (logout)
        if auth_service.is_token_blacklisted(jti):
            return True
        # Check 2: Was it issued before the user revoked all tokens?
        return auth_service.is_token_revoked(email, token_issued_at)

    # --- Rate Limiter ---
    # In production, use Redis: storage_uri = "redis://localhost: 6379"
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # --- regster blueprint ---
    auth_bp = create_auth_blueprint(
        auth_service, name='auth', limiter=limiter
    )
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # Register API blueprint
    app.register_blueprint(ecg_bp, url_prefix='/api')
    # --- health check ---
    @app.route('/')
    def index():
        return {'status': 'ok', 'message': 'Auth API is running'}
    return app

if __name__ == '__main__':
    app = create_app()
    print("Auth API running at http://localhost:5001")
    print("Endpoints: /api /auth/register, /auth/login, /auth/verify-email")
    app.run(debug=True, host='0.0.0.0', port=5001)
