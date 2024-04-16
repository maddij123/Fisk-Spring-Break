from flask import Flask, render_template, json, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)

app.secret_key = 'secret'

# MongoDB configurations
client = MongoClient('mongodb://localhost:27017/')
db = client['test2']

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/signup')
def showSignUp():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signUp():
    try:
        _first = request.form['inputFirst']
        _last = request.form['inputLast']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _phone = request.form['inputPhone']

        # validate the received values
        if _first and _last and _email and _password and _phone:
            users_collection = db['users']
            existing_user = users_collection.find_one({'email': _email})
            
            if existing_user:
                return json.dumps({'error': 'User already exists with this email'})
            else:
                hashed_password = generate_password_hash(_password)
                users_collection.insert_one({'first_name': _first, 'last_name': _last, 'email': _email, 'password': hashed_password, 'phone': _phone})
                return json.dumps({'message': 'User created successfully !'})
        else:
            return json.dumps({'error': 'Enter all required fields'})

    except Exception as e:
        return json.dumps({'error': str(e)})

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']

        users_collection = db['users']
        user = users_collection.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])  # Store user ID in session
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid email or password.')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        # Fetch user data from database using user_id
        users_collection = db['users']
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})

        # Fetch destinations data from database
        destinations_collection = db['destinations']
        destinations = destinations_collection.find()

        return render_template('dashboard.html', user=user_data, destinations=destinations)
    else:
        return redirect(url_for('login'))

# Add other routes as needed...

if __name__ == "__main__":
    app.run(debug=True)
