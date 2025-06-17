# Importing necessary libraries
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

# Creating the Flask app instance
app = Flask(__name__)

# Function to establish a connection to the database
def get_database_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'hotel_management.db')
    return sqlite3.connect(db_path)

# Function to execute SQL queries
def execute_query(query, parameters=None):
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        conn.commit()
        result = cursor.fetchall()
        return result
    except sqlite3.OperationalError as e:
        print("OperationalError:", e)
        conn.rollback()
    finally:
        conn.close()

# Function to create database tables if they don't exist
def create_tables():
    create_rooms_table = '''
        CREATE TABLE IF NOT EXISTS Rooms (
            room_number INTEGER PRIMARY KEY,
            room_type TEXT NOT NULL,
            rate REAL NOT NULL,
            occupancy INTEGER DEFAULT 0,
            check_in_date DATE,
            check_out_date DATE
        )
    '''

    create_guests_table = '''
        CREATE TABLE IF NOT EXISTS Guests (
            guest_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE
        )
    '''

    create_bookings_table = '''
        CREATE TABLE IF NOT EXISTS Bookings (
            booking_id INTEGER PRIMARY KEY,
            guest_id INTEGER NOT NULL,
            room_number INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
            FOREIGN KEY (room_number) REFERENCES Rooms(room_number)
        )
    '''

    execute_query(create_rooms_table)
    execute_query(create_guests_table)
    execute_query(create_bookings_table)

# Flask route to display booked rooms
@app.route('/show_booked_rooms')
def show_booked_rooms():
    # Query the database for booked rooms with check-in and check-out dates
    booked_rooms = execute_query('SELECT room_number, guest_id, check_in_date, check_out_date FROM Bookings WHERE check_in_date IS NOT NULL AND check_out_date IS NOT NULL')
    return render_template('show_booked_rooms.html', booked_rooms=booked_rooms)

# Flask route to remove a guest
@app.route('/remove_guest/<int:guest_id>')
def remove_guest(guest_id):
    execute_query('DELETE FROM Guests WHERE guest_id = ?', (guest_id,))
    return redirect(url_for('show_guests'))

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for adding a new guest
@app.route('/add_guest', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        execute_query('INSERT INTO Guests (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
        return redirect(url_for('index'))
    return render_template('add_guest.html')

# Route for booking a room
@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    if request.method == 'POST':
        room_number = request.form['room_number']
        guest_id = request.form['guest_id']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']

        # Insert booking into the database
        execute_query('INSERT INTO Bookings (guest_id, room_number, check_in_date, check_out_date) VALUES (?, ?, ?, ?)', 
                      (guest_id, room_number, check_in_date, check_out_date))

        return redirect(url_for('index'))
    
    # Fetch available guests to suggest
    guests = execute_query('SELECT * FROM Guests')
    return render_template('book_room.html', guests=guests)


# Route to display the list of guests
@app.route('/show_guests')
def show_guests():
    guests = execute_query('SELECT * FROM Guests')
    return render_template('show_guests.html', guests=guests)

# Main block to run the app
if __name__ == "__main__":
    create_tables()
    app.run(debug=True, port=500)
