"""Possuí as funções utilizadas pelas api"""
import os
from functools import wraps
from datetime import datetime, timedelta
import json
import hashlib
import jwt
from flask import jsonify, request

def validate_user_data(data: json) -> bool:
    """Verifica se os campos estão presentes"""
    required_fields = ['name', 'age', 'email', 'username']
    for field in required_fields:
        if field not in data:
            return False
        # Check if age is an integer
        if field == 'age' and not isinstance(data[field], int):
            return False
        # Check if other fields are strings
        if field != 'age' and not isinstance(data[field], str):
            return False
    return True


def generate_hash(password: str):
    """Gera um hash"""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    return hashed_password


def generate_jwt(payload: dict, secret_key: str) -> str:
    """Gera um JWT"""
    payload['exp'] = datetime.now() + timedelta(minutes=15)
    token = jwt.encode(payload=payload, key=secret_key, algorithm="HS256")

    return token


def token_required(fn):
    @wraps(fn)
    def decode_jwt(*args, **kwargs):
        """Decode a jwt token"""
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'missing token'}), 403

        try:
            _ = jwt.decode(jwt=token, key=os.getenv('SECRET_KEY'), algorithms=["HS256"])

        except Exception as e:
            return jsonify({
                'message': 'Authentication failed',
                'exception': str(e)
            }), 401

        return fn(*args, **kwargs)
    return decode_jwt
