
# !pip install -q flask-ngrok
# !pip install -q pyngrok
# !pip install -q flask-cors

# !ngrok authtoken 2wN1bUm4T1abPXfcukEYL2IYSoC_vVPG7pMoyenRmdTzG3Mu


from Model.BIOModel import predict_play_probability

# Import required libraries
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from pyngrok import ngrok
import logging
from werkzeug.utils import secure_filename
import os
import datetime
import mimetypes
import uuid
import json


AllEndpoints = {
  "User Endpoints": {
    "message": "User Endpoints:",
    "Summary": "There are 6 endpoints for user {GET: 2 ['/user', '/user/get_all'], POST: 4 ['/user/add', '/user/get', '/user/update', '/user/del']}",
    "endpoints": [
      {
        "endpoint": "/user/add",
        "method": "POST",
        "description": "Add a new user.",
        "required_parameters": ["email", "pass"]
      },
      {
        "endpoint": "/user/get",
        "method": "POST",
        "description": "Get a user's data by email.",
        "required_parameters": ["email"]
      },
      {
        "endpoint": "/user/update",
        "method": "POST",
        "description": "Update user data by email.",
        "required_parameters": ["email"],
        "optional_parameters": ["name", "user_name", "pass"]
      },
      {
        "endpoint": "/user/del",
        "method": "POST",
        "description": "Delete a user by email.",
        "required_parameters": ["email"]
      },
      {
        "endpoint": "/user/get_all",
        "method": "GET",
        "description": "Get all users' data."
      }
    ]
  },
  "Medical Model Endpoint": {
    "message": "Medical Model Endpoint:",
    "Summary": "There is 1 endpoint for the medical model {POST: 1 ['/BModel']}",
    "endpoints": [
      {
        "endpoint": "/BModel",
        "method": "POST",
        "description": "Run prediction using BIO medical model.",
        "required_parameters": ["data (in form-data)"],
        "notes": "Model can load data from fixed Excel file if data file didn`t exist."
      }
    ]
  },
  "Video Model Endpoints": {
    "message": "Video Model Endpoints:",
    "Summary": "There are 2 endpoints for video model {POST: 2 ['/upload', '/get']}",
    "endpoints": [
      {
        "endpoint": "/upload",
        "method": "POST",
        "description": "Upload a video and process it based on selected model type.",
        "required_parameters": ["file (in form-data)", "type (in form-data)"],
        "optional_parameters": [],
        "notes": "Supports model types: 'Players', 'Teams', 'Offside', 'Goal'"
      },
      {
        "endpoint": "/get",
        "method": "POST",
        "description": "Retrieve the processed annotated video by file_id.",
        "required_parameters": ["file_id"]
      }
    ]
  }
}


UserEndpoints = {
  "message": "User Endpoints:",
  "Summary": "There are 6 endpoints for user {GET: 2 ['/user', '/user/get_all'], POST: 4 ['/user/add', '/user/get', '/user/update', '/user/del']}",
  "endpoints": [
    {
      "endpoint": "/user/add",
      "method": "POST",
      "description": "Add a new user.",
      "required_parameters": ["email", "pass"]
    },
    {
      "endpoint": "/user/get",
      "method": "POST",
      "description": "Get a user's data by email.",
      "required_parameters": ["email"]
    },
    {
      "endpoint": "/user/update",
      "method": "POST",
      "description": "Update user data by email.",
      "required_parameters": ["email"],
      "optional_parameters": ["name", "user_name", "pass"]
    },
    {
      "endpoint": "/user/del",
      "method": "POST",
      "description": "Delete a user by email.",
      "required_parameters": ["email"]
    },
    {
      "endpoint": "/user/get_all",
      "method": "GET",
      "description": "Get all users' data."
    }
  ]
}


# Configure Flask logging
logging.basicConfig(level=logging.INFO)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/', methods=['GET'])
def home():
    return jsonify(AllEndpoints)


users = []

# Generate unique user ID
def generate_user_id():
    while True:
        user_id = str(uuid.uuid4()).replace('-', '')[:10]
        if not any(user['id'] == user_id for user in users):
            return user_id

@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.get_json()
    required_fields = ['email', 'pass']

    for field in required_fields:
        if field not in data or data[field] == '':
            return jsonify({'error': f'Missing required field: {field}'}), 400

    new_user = {
        'id': generate_user_id(),
        'name': data['name'],
        'user_name': data['user_name'],
        'email': data['email'],
        'pass': data['pass']
    }
    users.append(new_user)
    return jsonify({'message': 'User added successfully', 'user_id': new_user['id']}), 201

@app.route('/user/get', methods=['POST'])
def get_user():
    data = request.get_json()
    user_email = data.get('email')

    if not user_email:
        return jsonify({'error': 'email is required'}), 400

    user = next((user for user in users if user['email'] == user_email), None)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/user/update', methods=['POST'])
def update_user():
    data = request.get_json()
    user_email = data.get('email')

    if not user_email:
        return jsonify({'error': 'email is required'}), 400

    user = next((user for user in users if user['email'] == user_email), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    for field in ['name', 'user_name', 'pass']:
        if field in data and data[field]:
            user[field] = data[field]

    return jsonify({'message': 'User updated successfully', 'updated_user': user}), 200

@app.route('/user/del', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_email = data.get('email')

    if not user_email:
        return jsonify({'error': 'email is required'}), 400

    global users
    users = [user for user in users if user['email'] != user_email]
    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/user/get_all', methods=['GET'])
def get_all_users():
    ALL_Users = {
        'Total': f"{len(users)} Users Founded",
        'Users': users
    }
    return jsonify(ALL_Users), 200

@app.route('/user', methods=['GET'])
def user():
    return jsonify(UserEndpoints), 200



@app.route('/BModel', methods=['POST'])
def BIO_Model():
    try :
        if 'data' not in request.files:
          try:
            Data = ".\\Model\\DefualtData.xlsx"
          except Exception as err:
            return jsonify({'error': 'No data part in the request'}), 400
        else :
            Data = request.files['data']
        
        J_Res = predict_play_probability(Data)
        return jsonify(J_Res), 200
    except Exception as err:
        return jsonify({'error':'Error on Medecal Model'})



# Function to start ngrok
def run_with_ngrok():
    public_url = ngrok.connect(5000)
    # print (file_store)
    print(f' * Public URL: {public_url}')

if __name__ == '__main__':
    run_with_ngrok()
    # app.run(port=5000)
    app.run(port=5000, use_reloader=False, debug=True)
