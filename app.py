from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session handling
app.config['UPLOAD_FOLDER'] = 'static/images'

# Function to load users data from the JSON file
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            return json.load(file)
    return []

# Function to save users data to the JSON file
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

# Function to load cars data from the JSON file
def load_cars():
    if os.path.exists('cars.json'):
        with open('cars.json', 'r') as file:
            return json.load(file)
    return []

# Function to save cars data to the JSON file
def save_cars(cars):
    with open('cars.json', 'w') as file:
        json.dump(cars, file)

# Home page
@app.route('/')
def index():
    cars = load_cars()
    return render_template('index.html', cars=cars)

# Submit a car for rent
@app.route('/submit_car', methods=['GET', 'POST'])
def submit_car():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        price_per_day = request.form['price_per_day']
        description = request.form['description']
        car_type = request.form['car_type']
        model_year = request.form['model_year']
        
        images = []
        for file in request.files.getlist('car_images'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            images.append(file.filename)

        cars = load_cars()
        car = {
            'id': len(cars) + 1,
            'name': name,
            'location': location,
            'price_per_day': price_per_day,
            'description': description,
            'car_type': car_type,
            'model_year': model_year,
            'images': images
        }
        cars.append(car)
        save_cars(cars)
        return redirect(url_for('owner_dashboard'))
    
    return render_template('submit_car.html')

# Owner dashboard to manage cars
@app.route('/owner_dashboard')
def owner_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    cars = load_cars()
    return render_template('owner_dashboard.html', cars=cars)

# Edit car details
@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cars = load_cars()
    car = next((c for c in cars if c['id'] == car_id), None)
    if not car:
        return redirect(url_for('owner_dashboard'))

    if request.method == 'POST':
        car['name'] = request.form['name']
        car['location'] = request.form['location']
        car['price_per_day'] = request.form['price_per_day']
        car['description'] = request.form['description']
        car['car_type'] = request.form['car_type']
        car['model_year'] = request.form['model_year']
        
        images = []
        for file in request.files.getlist('car_images'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            images.append(file.filename)

        car['images'] = images
        save_cars(cars)
        return redirect(url_for('owner_dashboard'))

    return render_template('edit_car.html', car=car)

# Delete a car
@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cars = load_cars()
    cars = [car for car in cars if car['id'] != car_id]
    save_cars(cars)
    return redirect(url_for('owner_dashboard'))

# Car details page
@app.route('/car_details/<int:car_id>')
def car_details(car_id):
    cars = load_cars()
    car = next((c for c in cars if c['id'] == car_id), None)
    return render_template('car_details.html', car=car)

# Sign up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        if any(user['username'] == username for user in users):
            # Return error via JSON response for AJAX handling
            return jsonify({"error": "Username already taken. Please choose a different one."}), 400

        users.append({'username': username, 'password': password})
        save_users(users)

        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('owner_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['username'] = username
            return redirect(url_for('owner_dashboard'))
        else:
            # Return error via JSON response for AJAX handling
            return jsonify({"error": "Invalid credentials. Please try again."}), 400

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
