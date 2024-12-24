from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_secret_key')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subscription_level = db.Column(db.String(20), nullable=False)
    account_status = db.Column(db.String(20), nullable=False)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    access_level = db.Column(db.String(20), nullable=False)
    available_hours = db.Column(db.String(20), nullable=False)

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API!"}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        subscription_level=data['subscription_level'],
        account_status=data['account_status']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

def check_account_status(user):
    if user.account_status != 'active':
        return jsonify({"message": "Account is not active"}), 403

@app.route('/resources', methods=['POST'])
@jwt_required()
def add_resource():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    response = check_account_status(user)
    if response:
        return response

    data = request.get_json()
    new_resource = Resource(
        name=data['name'],
        access_level=data['access_level'],
        available_hours=data['available_hours']
    )
    db.session.add(new_resource)
    db.session.commit()
    return jsonify({"message": "Resource added successfully"}), 201

@app.route('/resources', methods=['GET'])
@jwt_required()
def get_resources():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    response = check_account_status(user)
    if response:
        return response

    current_time = datetime.now().strftime("%H:%M")
    resources = Resource.query.all()
    accessible_resources = []

    for resource in resources:
        start_time, end_time = resource.available_hours.split('-')
        if user.subscription_level == 'premium' or (user.subscription_level == 'basic' and resource.access_level == 'basic'):
            if start_time <= current_time <= end_time:
                accessible_resources.append({"name": resource.name, "access_level": resource.access_level})

    return jsonify({"resources": accessible_resources}), 200

@app.route('/resources/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_resource(resource_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    response = check_account_status(user)
    if response:
        return response

    current_time = datetime.now().strftime("%H:%M")
    resource = Resource.query.get(resource_id)
    if not resource:
        return jsonify({"message": "Resource not found"}), 404

    start_time, end_time = resource.available_hours.split('-')
    if user.subscription_level == 'premium' or (user.subscription_level == 'basic' and resource.access_level == 'basic'):
        if start_time <= current_time <= end_time:
            return jsonify({"name": resource.name, "access_level": resource.access_level}), 200

    return jsonify({"message": "Access denied"}), 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)