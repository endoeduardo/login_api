"""Código de rotas""" 
import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from utils.db_functions import create_connection

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


app = Flask(__name__)


@app.route('/')
def home():
    return "Server está online!"


@app.route('/login', methods=['POST'])
def login():
    """enpoint de login e retorna um jwt após a autenticação"""
    data = request.get_json()

    connection = create_connection(
        db_name=DB_NAME,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    )

    cursor = connection.cursor()

    query_user = """SELECT name FROM users WHERE name = %s"""

    cursor.execute(query_user, (data['user'], ))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result:
        token = {
            'jwt': 'random_token'
        }
        return jsonify(token)
    return "Login failed"


@app.route('/user_list', methods=['GET'])
def get_user_list():
    """retorna uma lista de usuários cadastrados no banco de dados"""
    print(DB_HOST)
    connection = create_connection(
        db_name=DB_NAME,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    )

    cursor = connection.cursor()

    query_user = """SELECT * FROM users"""

    cursor.execute(query_user)

    column_names = [col[0] for col in cursor.description]

    # Fetch user data
    users_data = cursor.fetchall()

    cursor.close()
    connection.close()

    # Combine column names and user data into a dictionary
    user_list = []
    for user in users_data:
        user_dict = dict(zip(column_names, user))
        user_list.append(user_dict)

    return json.dumps(user_list)



if __name__ == "__main__":
    app.run(
        host=os.getenv('API_HOST'),
        port=os.getenv('API_PORT'),
        debug=os.getenv('DEBUG')
    )
