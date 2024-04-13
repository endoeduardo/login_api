"""Possuí as funções utilizadas pelas api"""
from datetime import datetime, timedelta
import json
import hashlib
import jwt

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


def decode_jwt(token: str, secret_key: str) -> str:
    """Decode a jwt token"""
    try:
        result = jwt.decode(jwt=token, key=secret_key, algorithms=["HS256"])
    except jwt.exceptions.InvalidSignatureError as e:
        result = {
            "message": "Invalid Token!",
            "exception": str(e)
        }

    except jwt.exceptions.DecodeError as e:
        result = {
            "message": "Error in decoding a token!",
            "exception": str(e)
        }

    except jwt.exceptions.ExpiredSignatureError as e:
        result = {
            "message": "Expired Token!",
            "exception": str(e)
        }

    return result
