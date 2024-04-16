from flask import Flask, render_template, json, request, redirect, url_for, session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

mysql = MySQL()
app = Flask(__name__)

app.secret_key = 'secret'
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'skippero56'
app.config['MYSQL_DATABASE_DB'] = 'test2'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


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

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser', (_first, _last, _email, _password, _phone))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE EMAIL = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user[4] == password:
            session['user_id'] = user[0]  # Store user ID in session
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message='Invalid email or password.')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        # Fetch user data from database using session['user_id']
        user_data = session['user_id']  # Placeholder for user data (replace with actual user data retrieval)
        
        # Fetch destinations data from database
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DESTINATIONS")
        destinations = cursor.fetchall()  # Fetch all rows
        cursor.close()
        conn.close()
        
        return render_template('dashboard.html', user=user_data, destinations=destinations)
    else:
        return redirect(url_for('login'))


@app.route('/add_trip', methods=['POST'])
def add_trip():
    if 'user_id' in session:
        try:
            _destination_id = request.form['destination_id']
            _start_date = request.form['start_date']
            _end_date = request.form['end_date']
            _user_id = session['user_id']  # Get USER_ID from session

            # Fetch selected trip name
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT NAME FROM DESTINATIONS WHERE DESTINATION_ID = %s", (_destination_id,))
            selected_trip_name = cursor.fetchone()[0]
            conn.close()

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO TRIP (DESTINATION_ID, USER_ID, START_DATE, END_DATE) VALUES (%s, %s, %s, %s)",
                           (_destination_id, _user_id, _start_date, _end_date))
            conn.commit()

            return render_template('tripplan.html', trip_name=selected_trip_name)  # Pass trip name to the success page
        except Exception as e:
            return jsonify({'error': str(e)})
        finally:
            cursor.close()
            conn.close()
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

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT DESTINATIONS.FLIGHT_PRICE, DESTINATIONS.HOTEL_PRICE FROM DESTINATIONS "
                       "JOIN TRIP ON DESTINATIONS.DESTINATION_ID = TRIP.DESTINATION_ID "
                       "WHERE TRIP.TRIP_ID = %s", (_trip_id,))
        
        destination = cursor.fetchone()

        if destination:
            flight_price = destination[0]
            hotel_price = destination[1]

            total_expenses = _num_people * (flight_price + hotel_price)
            cursor.close()
            conn.close()

            return render_template('flight-expenses.html', destination=destination, num_people=_num_people,
                                   total_expenses=total_expenses)
        else:
            return 'Destination not found for the given trip ID.'

    except Exception as e:
        return str(e)



if __name__ == "__main__":
    app.run(debug=True)
