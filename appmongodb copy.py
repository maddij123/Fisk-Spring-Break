from flask import Flask, render_template, json, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask import request
from flask import jsonify


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

        return render_template('dashboarddb.html', user=user_data, destinations=destinations)
    else:
        return redirect(url_for('login.html'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():  # Rename the function
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']

        admin_collection = db['admin']
        admin = admin_collection.find_one({"email": email})

        if admin and admin['password_hash'] == password:
            session['admin_id'] = str(admin['_id'])  # Store admin ID in session
            return redirect(url_for('admin_dashboard'))  # Redirect to admin panel
        else:
            return render_template('adminlogin.html', message='Invalid email or password.')

    return render_template('adminlogin.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' in session:  
        users_collection = db['users']
        trips_collection = db['trip']  # Adjust collection name to 'trip'

        user_trip_data = users_collection.aggregate([
            {
                "$lookup": {
                    "from": "trip",  # Adjust collection name to 'trip'
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "user_trips"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "first_name": 1,
                    "last_name": 1,
                    "num_trips": { "$size": "$user_trips" }  # Count the number of trips
                }
            }
        ])

        return render_template('admindb.html', user_trip_data=list(user_trip_data))
    else:
        return redirect(url_for('adminlogin'))



# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' in session:
#         # Fetch user data from database using session['user_id']
#         users_collection = db['users']
#         user_data = users_collection.find_one({"_id": ObjectId(session['user_id'])})

#         # Fetch destinations data from database
#         destinations_collection = db['destinations']
#         destinations = list(destinations_collection.find())

#         return render_template('dashboard.html', user=user_data, destinations=destinations)
#     else:
#         return redirect(url_for('login'))
    
@app.route('/add_trip', methods=['POST'])
def add_trip():
    if 'user_id' in session:
        try:
            _destination_id = request.form['destination_id']
            _start_date = request.form['start_date']
            _end_date = request.form['end_date']
            _user_id = session['user_id']

            # Convert _destination_id to ObjectId
            _destination_id = ObjectId(_destination_id)

            selected_trip_data = db.destinations.find_one({"_id": _destination_id}, {"name": 1, "image_url": 1})
            selected_trip_name = selected_trip_data['name']
            image_url = selected_trip_data['image_url']

            # Insert trip into the database
            trip_id = db.trip.insert_one({"destination_id": _destination_id, "user_id": _user_id, "start_date": _start_date, "end_date": _end_date}).inserted_id

            # Fetch activities for the destination
            activities = list(db.activities.find({"destination_id": _destination_id}, {"name": 1, "description": 1, "price": 1}))

            return render_template('tripplandb.html', trip_name=selected_trip_name, image_url=image_url, activities=activities, trip_id=str(trip_id))
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return redirect(url_for('login'))

@app.route('/expenses')
def expenses():
    # You can add any necessary data to pass to the expenses.html template here
    return render_template('expenses.html')

@app.route('/flight-page')
def flight_page():
    return render_template('flight.html')

@app.route('/drive')
def drive():
    return render_template('drive.html')

@app.route('/calculate_expenses', methods=['POST'])
def calculate_expenses():
    try:
        _trip_id = request.form['trip_id']
        _num_people = int(request.form['num_people'])

        trip = db.trip.find_one({"_id": ObjectId(_trip_id)})
        destination = db.destinations.find_one({"_id": ObjectId(trip.get('destination_id'))})

        if destination:
            flight_price = destination['flight_price']
            hotel_price = destination['hotel_price']

            total_expenses = _num_people * (flight_price + hotel_price)

            return render_template('flight-expensesdb.html', destination=destination, num_people=_num_people,
                                   total_expenses=total_expenses)
        else:
            return 'Destination not found for the given trip ID.'

    except Exception as e:
        return str(e)

@app.route('/drive-expenses', methods=['POST'])
def drive_expenses():
    try:
        trip_id = request.form['trip_id']

        trip = db.trip.find_one({"_id": ObjectId(trip_id)})
        destination = db.destinations.find_one({"_id": ObjectId(trip['destination_id'])})

        num_miles = destination['distance']
        hotel_price = destination['hotel_price']

        return render_template('drive-expenses.html', num_miles=num_miles, hotel_price=hotel_price)
    except Exception as e:
        return str(e)

@app.route('/your_trips')
def your_trips():
    if 'user_id' in session:
        user_id = session['user_id']

        trips_data = list(db.trips.find({"user_id": ObjectId(user_id)}))
        trips = [{
            'trip_id': str(trip['_id']),
            'destination_id': str(trip['destination_id']),
            'user_id': str(trip['user_id']),
            'start_date': trip['start_date'].strftime('%Y-%m-%d'),  # Convert date object to string
            'end_date': trip['end_date'].strftime('%Y-%m-%d'),    # Convert date object to string
            'destination_name': db.destinations.find_one({"_id": ObjectId(trip['destination_id'])})['name']
        } for trip in trips_data]

        return render_template('your_trips.html', trips=trips)
    else:
        return redirect(url_for('login'))

@app.route('/delete-user', methods=['POST'])
def delete_user():
    if 'admin_id' in session:
        user_id = request.form.get('user_id')  # Fetch user_id from the form data
        
        if user_id:
            # Convert user_id to ObjectId
            user_id = ObjectId(user_id)

            # Delete associated trip records
            db.trip.delete_many({'user_id': user_id})  # Adjust collection name to 'trip'

            # Now delete the user
            db.users.delete_one({'_id': user_id})

            return redirect(url_for('admin_dashboard'))  # Redirect the user to the admin dashboard
        else:
            return "User ID not provided."
    else:
        return redirect(url_for('adminlogin'))


@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['password']

        # Check if the user exists
        user = db.users.find_one({'email': email})

        if user:
            # Update the user's password
            db.users.update_one({'_id': user['_id']}, {'$set': {'password_hash': generate_password_hash(new_password)}})
            return redirect(url_for('login'))  # Redirect the user to the login page
        else:
            return render_template('password.html', message='User not found.')

    return render_template('password.html')

@app.route('/activities')
def activities():
    destination_names = [destination['name'] for destination in db.destinations.find()]
    return render_template('activities.html', destination_names=destination_names)

@app.route('/add_activity', methods=['POST'])
def add_activity():
    try:
        _activity_name = request.form['name']
        _activity_description = request.form['description']
        _price = float(request.form['price'])
        _destination_name = request.form['destination_name']

        if _destination_name and _activity_name and _activity_description and _price:

            # Get the destination ID based on the provided destination name
            destination = db.destinations.find_one({'name': _destination_name})

            if destination:
                # Insert the activity into the ACTIVITIES collection
                db.activities.insert_one({
                    'destination_id': destination['_id'],
                    'name': _activity_name,
                    'description': _activity_description,
                    'price': _price
                })

                # Redirect the user to the success page with destination name as parameter
                return redirect(url_for('activity_success', destination_name=_destination_name))
            else:
                return jsonify({'error': 'Destination not found.'})
        else:
            return jsonify({'error': 'Enter all the required fields.'})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/activity_success/<destination_name>')
def activity_success(destination_name):
    try:
        # Join the DESTINATIONS collection with the PACKING_LIST collection to get the success message
        destination = db.destinations.find_one({'name': destination_name})
        packing_list = db.packing_list.find_one({'destination_id': destination['_id']})

        if packing_list:
            success_message = f"When going to {destination['name']}, make sure you bring {packing_list['necessity']}!"
            return render_template('activity_success.html', success_message=success_message)
        else:
            return "No success message found for this destination."

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
