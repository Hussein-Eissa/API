# !pip install -q flask-ngrok
# !pip install -q pyngrok

!ngrok authtoken 2tJaGHYqjzpQwPCAimXaP1KeugU_67adGzz2KYop3QPnYkC1t

# Import required libraries
from flask import Flask, request, jsonify
from pyngrok import ngrok
import uuid

# Initialize Flask app
app = Flask(__name__)

# Default user data
users = [
    {
        'id': 'knsu17wu',
        'name': "Full Name Here",
        'user_name': 'unique_user_name',
        'email': "Example_1@gmail.com",
        'pass': 'Password_1'
    },
    {
        'id': 'isduj8wjw',
        'name': "Full Name Here",
        'user_name': 'unique_user_name',
        'email': "Example_2@gmail.com",
        'pass': 'Password_2'
    },
    {
        'id': 'ls6y3h8sj',
        'name': "Full Name Here",
        'user_name': 'unique_user_name',
        'email': "Example_3@gmail.com",
        'pass': 'Password_3'
    },
    {
        'id': 'diwj8oiu3',
        'name': "Full Name Here",
        'user_name': 'unique_user_name',
        'email': "Example_4@gmail.com",
        'pass': 'Password_4'
    },
    {
        'id': '8932nd8djs',
        'name': "Full Name Here",
        'user_name': 'unique_user_name',
        'email': "Example_5@gmail.com",
        'pass': 'Password_5'
    }
]


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
        
    # if not all(field in data for field in required_fields) and all(field in data for field != ""):
    #     return jsonify({'error': 'Missing required fields'}), 400

    # if any(user['user_name'] == data['user_name'] for user in users):
    #     return jsonify({'error': 'user_name must be unique'}), 400

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
    if user :
        return jsonify(user), 200
    else :
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

@app.route('/')
def home():
    return jsonify({
        "message": "API Endpoints:",
        "Summary": "There are 6 endpionts for user {GET : 2 ['/' , '/user/get_all'],POST : 4 ['/user/add' , '/user/get' , '/user/update', '/user/del']}",
        "endpoints": [
            {
                "endpoint": "/user/add",
                "method": "POST",
                "description": "Add a new user.",
                "required_parameters": ["email", "pass"],
                "returns": {"message": "User added successfully", "user_id": "string"}
            },
            {
                "endpoint": "/user/get",
                "method": "POST",
                "description": "Get a user's data by email.",
                "required_parameters": ["email"],
                "returns": {"id": "string", "name": "string", "user_name": "string", "email": "string", "pass": "string"}
            },
            {
                "endpoint": "/user/update",
                "method": "POST",
                "description": "Update user data by email.",
                "required_parameters": ["email"],
                "optional_parameters": ["name", "user_name", "pass"],
                "returns": {"message": "User updated successfully", "updated_user": "object"}
            },
            {
                "endpoint": "/user/del",
                "method": "POST",
                "description": "Delete a user by email.",
                "required_parameters": ["email"],
                "returns": {"message": "User deleted successfully"}
            },
            {
                "endpoint": "/user/get_all",
                "method": "GET",
                "description": "Get all users' data.",
                "required_parameters": [],
                "returns": {"users": "list of user objects"}
            }
        ]
    }), 200

# Function to start ngrok
def run_with_ngrok():
    public_url = ngrok.connect(5080)
    print(f' * Public URL: {public_url}')

if __name__ == '__main__':
    run_with_ngrok()
    app.run(port=5080, use_reloader=False, debug=True)

app = Flask(__name__)

def handler(request):
    return app(request)

