from flask import Flask, render_template, json, request, redirect, url_for, session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify


# mysql = MySQL()
# app = Flask(__name__)

# # MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'skippero56'
# app.config['MYSQL_DATABASE_DB'] = 'travel_planner'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)


# @app.route('/')
# def main():
#     return render_template('index.html')


# @app.route('/signup')
# def showSignUp():
#     return render_template('signup.html')



# @app.route('/api/signup', methods=['POST'])
# def signUp():
#     try:
#         _first = request.form['inputfName']
#         _last = request.form['inputlName']
#         _email = request.form['inputEmail']
#         _number = request.form['inputNumber']
#         _password = request.form['inputPassword']


#         # validate the received values
#         if _first and _last and _email and _password and _number:

#             # All Good, let's call MySQL

#             conn = mysql.connect()
#             cursor = conn.cursor()
#             _hashed_password = generate_password_hash(_password)
#             cursor.callproc('sp_createUser', (_first, _last, _email, _password, _number))
#             data = cursor.fetchall()

#             if len(data) == 0:
#                 conn.commit()
#                 return json.dumps({'message': 'User created successfully !'})
#             else:
#                 return json.dumps({'error': str(data[0])})
#         else:
#             return json.dumps({'error': 'Enter all required fields'})

#     except Exception as e:
#         print("Error:", e)
#         return json.dumps({'error': 'An error occurred while processing your request'})

#     finally:
#         cursor.close()
#         conn.close()


# if __name__ == "__main__":
#     app.run()

mysql = MySQL()
app = Flask(__name__)

app.secret_key = 'secret'
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'skippero56'
app.config['MYSQL_DATABASE_DB'] = 'test'
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
            _num_people = request.form['num_people']
            _price_per_person = request.form['price_per_person']
            _user_id = session['user_id']  # Get USER_ID from session

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO TRIP (DESTINATION_ID, START_DATE, END_DATE, NUM_PEOPLE, PRICE_PER_PERSON, USER_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                           (_destination_id, _start_date, _end_date, _num_people, _price_per_person, _user_id))
            conn.commit()

            return render_template('tripplan.html')
        except Exception as e:
            return jsonify({'error': str(e)})
        finally:
            cursor.close()
            conn.close()
    else:
        return render_template('index.html')

@app.route('/trip_info')
def trip_info():
    if 'user_id' in session:
        try:
            # Fetch trip information from the database
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TRIP WHERE USER_ID = %s", (session['user_id'],))
            trips = cursor.fetchall()  # Fetch all trips for the logged-in user
            cursor.close()
            conn.close()

            return render_template('tripplan.html', trips=trips)
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)
