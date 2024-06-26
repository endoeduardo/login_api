"""Código de rotas""" 
import os
import json
import random
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from faker import Faker
import psycopg2.extras
from utils.db_functions import create_connection, find_user
from utils.api_functions import validate_user_data, generate_jwt, token_required, generate_hash, role_required


load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


app = Flask(__name__)

@app.route('/')
def home():
    """Retorna se o server está online"""
    return jsonify({"message": "O servidor está online!"})


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

    #query o usuário selecionado e retorna a sua senha
    query_user = """SELECT username, password FROM users WHERE username = %s"""
    cursor.execute(query_user, (data['username'], ))
    result = cursor.fetchone()

    cursor.close()
    connection.close()
    if not result:
        return jsonify({"message": "User not found"}), 400

    username, password = result
    hashed_password = generate_hash(str(data['password']))
    if password == hashed_password:
        payload_data = {
            'username': username,
            'password': password
        }

        token = generate_jwt(payload=payload_data, secret_key=os.getenv('SECRET_KEY'))
        response_data = {
            'Message': 'Success',
            'data': {'jwt': token}
        }
        return jsonify(response_data), 200
    return jsonify({"message": "Login Failed"}), 400


@app.route('/user_list', methods=['GET'])
@token_required
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
@token_required
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


@app.route('/generate_admin_user', methods=["GET"])
def generate_admin_user():
    """Cria um super usuário"""
    connection = create_connection(
        db_name=DB_NAME,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    )
    cursor = connection.cursor()
    query = """INSERT INTO users (NAME, USERNAME, PASSWORD, EMAIL, AGE, ROLE)
    VALUES (%s, %s, %s, %s, %s, %s);"""

    hashed_password = generate_hash('1234')
    cursor.execute(query, ('eduardo', 'eduardo07', hashed_password, 'eduardo.t.endo@gmail.com', 26, 'admin'))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'message': 'success'}), 200


@app.route('/create_random_users', methods=['GET'])
@token_required
def create_users():
    """"Cria 10 usuários randomicamente"""
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

    for _ in range(0, 10):
        user_id = uuid.uuid4()
        name = fake.name()
        passowrd = generate_hash(str(random.randint(100, 999)))
        email = name.lower().replace(' ', '_') + '@gmail.com'
        username = name.split()[1] + str(random.randint(1, 10))
        age = random.randint(18, 110)

        cursor.execute(query, (user_id, name, passowrd, email, username, age))

    connection.commit()
    cursor.close()
    connection.close()

    return make_response({'message': 'created 10 users!'}, 200)


@app.route('/register_user', methods=['POST'])
@token_required
def register_user():
    """Endpoint que registra um usuário no banco de dados"""
    connection = create_connection(
        db_name=DB_NAME,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    )
    cursor = connection.cursor()

    #Check se foram enviados todos os dados para ser registrado
    data = request.json
    if not data or not validate_user_data(data):
        cursor.close()
        connection.close()
        return jsonify({'error': 'Invalid or missing data'}), 400

    #Check se o usuário não é repetido
    if find_user(cursor, data['username']):
        cursor.close()
        connection.close()
        return jsonify({"message": "Failed to register, user already exists!"}), 400

    query = """INSERT INTO users (NAME, USERNAME, PASSWORD, EMAIL, AGE)
    VALUES (%s, %s, %s, %s, %s);
    """

    #Cria uma hash para a senha antes
    password = generate_hash(data['password'])
    insertion_values = (
        data['name'], data['username'], password, data['email'], data['age']
    )
    cursor.execute(query, insertion_values)
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({'message': 'Successfully registered a user'}), 200


@app.route('/delete_user', methods=['POST'])
@token_required
def delete_user():
    """Deleta um usuário da base de usuários"""
    connection = create_connection(
        db_name=DB_NAME,
        db_host=DB_HOST,
        db_port=DB_PORT,
        db_user=DB_USER,
        db_password=DB_PASSWORD
    )
    cursor = connection.cursor()
    data = request.json

    query = """DELETE FROM users WHERE username = %s"""
    if data:
        cursor.execute(query, (data['username'], ))
        connection.commit()

        return jsonify({"message": f"Successfully delete the user {data['username']}"})

    cursor.close()
    connection.close()

    return jsonify({"message": "Invalid values"}), 400


@app.route('/test-admin', methods=['GET'])
@role_required(['admin'])
@token_required
def test_admin():
    """endpoint para testar o papel de Admin"""
    return jsonify({'Message': 'Você é um Admin!'})


if __name__ == "__main__":
    app.run(
        host=os.getenv('API_HOST'),
        port=os.getenv('API_PORT'),
        debug=os.getenv('API_DEBUG')
    )
