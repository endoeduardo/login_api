"""Código de rotas""" 
import os
import json, random
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from faker import Faker
import psycopg2.extras
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
        # Convert UUIDs to strings before serializing to JSON
        for key, value in user_dict.items():
            if isinstance(value, uuid.UUID):
                user_dict[key] = str(value)
        user_list.append(user_dict)

    return json.dumps(user_list)


@app.route('/erase_all_users', methods=['GET'])
def erase_db():
    """apaga toda a tabela de usuários"""
    connection = create_connection(
        db_name=DB_NAME,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    )

    cursor = connection.cursor()

    query = """
    DELETE FROM USERS *
    """
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

    return make_response({'message': 'Deleted all users from users!'}, 200)


@app.route('/create_random_users', methods=['GET'])
def create_users():
    connection = create_connection(
        db_name=DB_NAME,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    )
    #When working with uuids
    psycopg2.extras.register_uuid()
    cursor = connection.cursor()

    query = """
    INSERT INTO users (ID, NAME, PASSWORD, EMAIL, USERNAME, AGE)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    fake = Faker()

    for i in range(0, 10):
        user_id = uuid.uuid4()
        name = fake.name()
        passowrd = random.randint(100, 999)
        email = name.lower().replace(' ', '_') + '@gmail.com'
        username = name.split()[1] + str(random.randint(1, 10))
        age = random.randint(18, 110)

        cursor.execute(query, (user_id, name, passowrd, email, username, age))
    
    connection.commit()
    cursor.close()
    connection.close()


    return make_response({'message': 'created 10 users!'}, 200)


if __name__ == "__main__":
    app.run(
        host=os.getenv('API_HOST'),
        port=os.getenv('API_PORT'),
        debug=os.getenv('API_DEBUG')
    )
