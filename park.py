from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key


# Create a simple SQLite database for users
def connect_to_database():
    return sqlite3.connect('users.db')


def create_users_table():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (name TEXT, id TEXT)''')
    conn.commit()
    conn.close()


create_users_table()


# Create a simple SQLite database for licenses
def connect_to_license_database():
    return sqlite3.connect('data.db')


def create_license_table():
    conn = connect_to_license_database()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS licenses (license_number TEXT)''')
    conn.commit()
    conn.close()


create_license_table()


@app.route('/')
def login():
    return render_template('index.html')


@app.route('/auth', methods=['POST'])
def auth():
    name = request.form['Name']
    iden = request.form['Police ID']

    # Connect to the database
    try:
        with connect_to_database() as conn:
            cursor = conn.cursor()
            # Check if the user exists in the database
            cursor.execute('SELECT * FROM users WHERE name = ? AND id = ?', (name, iden))
            user = cursor.fetchone()

        if user:
            # Store user data in session
            session['Name'] = name
            return redirect('/dashboard')
        else:
            return render_template('index.html', message='Invalid login credentials.')

    except sqlite3.Error as e:
        # Handle database errors
        print("Database error:", e)
        return render_template('index.html', message='An error occurred while processing your request.')


@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'Name' in session:
        return render_template('dashboard.html', username=session['Name'])
    else:
        return redirect('/')


@app.route('/logout')
def logout():
    # Remove user data from session
    session.pop('Name', None)
    return redirect('/')


@app.route('/check_license', methods=['POST'])
def check_license():
    license_number = request.json['license_number']

    # Query the database to check if the license number exists
    conn = connect_to_license_database()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM licenses WHERE license_number=?', (license_number,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        status = '✅'
    else:
        status = '❌'

    return jsonify({'status': status})


if __name__ == '__main__':
    app.run(debug=True)
