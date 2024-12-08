from flask import Flask, render_template, request, redirect, url_for, session, abort
import mysql.connector
from mysql.connector import Error
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a more secure key
 
# Define allowed hosts
ALLOWED_HOSTS = ["34.247.67.139", "127.0.0.1", "localhost"]  # Add your allowed IPs/domains here
 
# MySQL Connection
try:
    db = mysql.connector.connect(
        host='devopsapp-sanjithsanju2811-a396.e.aivencloud.com',
        user='avnadmin',
        password='AVNS_ZkBFjlfvRTCRdB0ZwQn',
        database='defaultdb',
        port='20552'
    )
except Error as e:
    print("Error while connecting to MySQL:", e)
 
# Middleware to enforce ALLOWED_HOSTS
@app.before_request
def check_allowed_hosts():
    host = request.host.split(':')[0]  # Extract the hostname (ignore port)
    if host not in ALLOWED_HOSTS:
        abort(403)  # Return a 403 Forbidden error if the host is not allowed
 
# Routes and logic remain the same
@app.route('/')
def home():
    return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        session['user_id'] = user[0]  # Store user ID in session
        return redirect(url_for('dashboard'))
    return "Invalid username or password"
 
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect(url_for('home'))  # Redirect to login page after successful registration
    return render_template('user_creation.html')
 
@app.route('/register')  # Added /register route for redirection
def register():
    return redirect(url_for('create_user'))
 
@app.route('/dashboard')
def dashboard():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM measurements WHERE user_id=%s", (session['user_id'],))
    measurements = cursor.fetchall()
    return render_template('dashboard.html', measurements=measurements)
 
@app.route('/add_measurement', methods=['GET', 'POST'])
def add_measurement():
    if request.method == 'POST':
        current = float(request.form['current'])
        voltage = float(request.form['voltage'])
        power_factor = float(request.form['power_factor'])
        item_name = request.form['item_name']
        power = (1.732 * current * voltage * power_factor) / 1000
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO measurements (user_id, current, voltage, power_factor, item_name, power)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (session['user_id'], current, voltage, power_factor, item_name, power))
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_measurement.html')
 
@app.route('/edit/<int:measurement_id>', methods=['GET', 'POST'])
def edit_measurement(measurement_id):
    cursor = db.cursor()
    if request.method == 'POST':
        current = float(request.form['current'])
        voltage = float(request.form['voltage'])
        power_factor = float(request.form['power_factor'])
        item_name = request.form['item_name']
        power = (1.732 * current * voltage * power_factor) / 1000
        cursor.execute("""
            UPDATE measurements
            SET current=%s, voltage=%s, power_factor=%s, item_name=%s, power=%s
            WHERE id=%s
            """, (current, voltage, power_factor, item_name, power, measurement_id))
        db.commit()
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT * FROM measurements WHERE id=%s", (measurement_id,))
    measurement = cursor.fetchone()
    if measurement:
        return render_template('edit_measurement.html', measurement=measurement)
    else:
        return "Measurement not found", 404
 
@app.route('/delete/<int:measurement_id>', methods=['POST'])
def delete_measurement(measurement_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM measurements WHERE id=%s", (measurement_id,))
    db.commit()
    return redirect(url_for('dashboard'))
 
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from the session
    return redirect(url_for('home'))
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
