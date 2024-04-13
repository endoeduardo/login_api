"""Possuí as funções utilizadas pelas api"""
import json
import hashlib


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


if __name__ == "__main__":
    print(generate_hash("secreto"))
