from flask import jsonify
import numpy as np


def success_response(data, message=None):
    """Format successful API response"""
    response = {'success': True, 'data': data}
    if message:
        response['message'] = message
    return jsonify(response)


def error_response(message, status_code=400):
    """Format error API response"""
    response = {'success': False, 'error': message}
    return jsonify(response), status_code


def numpy_to_list(obj):
    """Convert numpy arrays to lists for JSON serialization"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: numpy_to_list(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [numpy_to_list(item) for item in obj]
    return obj
