"""Flask blueprint for authentication endpoints."""
from os import link
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from .auth import AuthService
from .exceptions  import  (
    UserNotFoundError, InvalidCredentialsError, EmailNotVerifiedError,
    TokenExpiredError, UserAlreadyExistsError, EmailSendError,
    AccountLockedError, WeakPasswordError, DatabaseError
)

def create_auth_blueprint(auth_service: AuthService, name: str = 'auth', limiter=None) -> Blueprint:
    """
    Factory function that creates a Flask blueprint with auth endpoints.

    Why a factory? Because it receives the AuthServiceInstance as a parameter, which means we can confugure different services for different environments (test vs. production) and use dependency injection.

    Args:
       auth_service: The AuthService instance to handle business logic
       name: Blueprint name (also used as URL prefix)
       limiter: Optional Flask-limiter for rate limiting
    """

    bp = Blueprint(name, __name__)
    # Helper to conditionally apply rate limiting
    def apply_limit(limit_string):
        def decorator(f):
            if limiter:
                return limiter.limit(limit_string)(f)
            return f
        return decorator
    # POST /auth/register 
    @bp.route('/register', methods=['POST'])
    @apply_limit("3 per minute")
    def register():
        """
        Register a new user account
        Request body: {"email": "...", "password": "..."}

        Responses:
        - 201: User created, verification email sent
        - 202: User created, but email sending failed
        - 400: Missing fields or weak password
        - 409: Email already registered
        """
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            result = auth_service.register_user(email, password)
            status = 201 if result['verification_email_sent'] else 202
            return jsonify({
                'message': result['message'],
                'user_id': result['user_id']
                }), status
        except WeakPasswordError as e:
            return jsonify({'error': str(e)}), 400
        except UserAlreadyExistsError as e:
            return jsonify({'error': str(e)}), 409
        except Exception as e:
            return jsonify({'error': str(e)}), 500


        # POST /auth/login
    @bp.route('/login', methods=['POST'])
    @apply_limit("5 per minute")
    def login():
        """
        Authenticate and receive tokens.

        Request body: {"email": "...", "password": "..."}

        Responses:
        - 200: {access_token, refresh_token, user}
        - 401: Wrong email or password
        - 403: Email not verified
        - 429: Account locked
        """
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({
                    'error': 'Email and password are required'
                    }), 400

            result = auth_service.login_user(email, password)
            return jsonify({'access_token': result['access_token'],
                            'refresh_token': result['refresh_token'],
                            'user': result['user']
                            }), 200
        except (UserNotFoundError, InvalidCredentialsError):
            # Same error message for both - prevents user enumeration
            return jsonify({'error': 'Invalid email or password'
                            }), 401
        except AccountLockedError as e:
            return jsonify({'error': str(e)}), 429
        except EmailNotVerifiedError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    #  Get /auth/verify-email?token=...
    @bp.route('/verify-email', methods=['GET'])
    @apply_limit("10 per minute")
    def verify_email():
       """
       Verify email with the token from the verification link

       Query params: ?token=...
       """
       try:
           token = request.args.get('token')
           if not token:
               return jsonify({
                   'error': 'Verification token is required'
                   }), 400
           result = auth_service.verify_email(token)
           return jsonify(result), 200
       except UserNotFoundError:
           return jsonify({
               'error': 'Invalid verification token'
           }), 400
       except TokenExpiredError as e:
           return jsonify({
               'error': str(e)
           }), 400
       except Exception as e:
           return jsonify({'error': str(e)}), 500

    # POST /auth/resend-verification
    @bp.route('/resend-verification', methods=['POST'])
    @apply_limit("2 per minute")
    def resend_verification():
        """
        Resend the verification email.
        
        Request body: {"email": "..."}
        Always returns success to prevent user enumeration.
        """
        try:
            data = request.json
            email = data.get('email')
            if not email:
                return jsonify({'error': 'Email is required'}), 400

            result = auth_service.resend_verification(email)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # POST /auth/refresh
    @bp.route('/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """
        Get a new access token using a refresh token.

        The refresh token must be sent in the Authorization header:
        Authorization: Bearer <refresh_token>

        Returns new access_token and refresh_token (token_rotation).
        """

        try:
            current_user = get_jwt_identity()
            # Extract the refresh token from the header
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                refresh_token_string = auth_header[7:]
            else:
                return jsonify({
                    'error': 'Invalid authorization header'
                    }), 401
            result = auth_service.refresh_access_token(current_user, refresh_token_string)
            return jsonify(result), 200

        except (UserNotFoundError, InvalidCredentialsError):
            return jsonify({'error': 'Invalid refresh token'}), 401

        except Exception as e:
            return jsonify({'error': str(e)}),500

    # GET /auth/profile
    @bp.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """
        Get the current user's profile.
        Requires Access token in Authorization header.
        """
        try:
            current_user_email = get_jwt_identity()
            user = auth_service.get_user_by_email(current_user_email)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({'user': user.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return bp
            
