# Import statements
import sqlite3
from datetime import datetime
import db_base as db
import csv
import os

# Connection to the database
conn = sqlite3.connect('hotel_reservation.db')
c = conn.cursor()

# Customer Class
class Customer(db.DBbase):
    def __init__(self, db_name):
        super().__init__(db_name)
        self.create_table()

    def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Customer (
            cust_id INTEGER PRIMARY KEY NOT NULL,
                 first_name TEXT NOT NULL,
                 last_name TEXT NOT NULL,
                 dob date NOT NULL,
                 phone int(12) NOT NULL
        );
        """
        self.execute_script(sql)

    def add_customer(self, cust_id, first_name, last_name, dob, phone):
        sql = "INSERT OR IGNORE INTO Customer (cust_id, first_name, last_name, dob, phone) VALUES (?, ?, ?, ?, ?)"
        values = (cust_id, first_name, last_name, dob, phone)
        self.get_cursor.execute(sql, values)
        self.get_connection.commit()
        return self.get_cursor.lastrowid

    def add_to_db(self):
        # Open CSV file and read rows
        csv_file = os.path.join(os.path.dirname(__file__), 'customer.csv')
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            # Skip header row
            next(reader)
            # Iterate over rows and insert into table
            for row1 in reader:
                cust_id, first_name, last_name, dob, phone = row1
                self.add_customer(cust_id, first_name, last_name, dob, phone)
        print('Data from customer.csv file has been added to the database')

Customer = Customer('hotel_reservation.db')
Customer.add_to_db()

# Creating tables for database
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS rooms
                 (room_number INTEGER PRIMARY KEY,
                  room_type TEXT NOT NULL,
                  rate INTEGER NOT NULL,
                  available BOOL NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS reservations
                 (reservation_id INTEGER PRIMARY KEY,
                  customer_name TEXT NOT NULL,
                  room_number INTEGER NOT NULL,
                  check_in_date TEXT NOT NULL,
                  check_out_date TEXT NOT NULL,
                  total_cost INTEGER NOT NULL,
                  FOREIGN KEY(room_number) REFERENCES rooms(room_number))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Customer(
                 cust_id INTEGER PRIMARY KEY NOT NULL,
                 first_name TEXT NOT NULL,
                 last_name TEXT NOT NULL,
                 dob date NOT NULL,
                 phone int(12) NOT NULL )''')

    conn.commit()

# Function to check available rooms for booking
def check_availability(room_number, check_in_date, check_out_date):
    try:

        c.execute('''SELECT available FROM rooms WHERE room_number = ?''', (room_number,))
        available = c.fetchone()[0]

        c.execute('''SELECT EXISTS(SELECT 1 FROM reservations
                                     WHERE room_number = ?
                                     AND ((check_in_date <= ? AND check_out_date >= ?)
                                          OR (check_in_date >= ? AND check_in_date <= ?)))''',
                  (room_number, check_in_date, check_in_date, check_in_date, check_out_date))
        reserved = c.fetchone()[0]

        if not available:
            return False
        elif reserved:
            return False
        else:
            return True

    except Exception as e:
            print("An error has occurred : {}".format(e))

# Function to calculate the total cost after reservation
def calculate_cost(room_type, check_in_date, check_out_date):
    try:

        c.execute('''SELECT rate FROM rooms WHERE room_type = ?''', (room_type,))
        rate = c.fetchone()[0]

        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
        num_nights = (check_out_date - check_in_date).days

        total_cost = num_nights * rate
        return total_cost

    except Exception as e:
            print("An error has occurred : {}".format(e))

# Function to make a new reservation
def make_reservation(customer_name, room_number, check_in_date, check_out_date, total_cost):
    # try:

        c.execute('''INSERT INTO reservations(customer_name, room_number, check_in_date, check_out_date, total_cost)
                     VALUES (?, ?, ?, ?, ?)''', (customer_name, room_number, check_in_date, check_out_date, total_cost))

        c.execute('''UPDATE rooms SET available = 0 WHERE room_number = ?''', (room_number,))
        conn.commit()

    # except Exception as e:
    #         print("An error has occurred : {}".format(e))


# Function to update the existing reservation
def update_reservation(reservation_id, room_number, check_in_date, check_out_date, total_cost):
    try:

        # Update the reservation record in the database
        c.execute(
            '''UPDATE reservations SET room_number = ?, check_in_date = ?, check_out_date = ?, total_cost = ? WHERE reservation_id = ?''',
            (room_number, check_in_date, check_out_date, total_cost, reservation_id))

        # Update the available status of the previously reserved room
        c.execute(
            '''UPDATE rooms SET available = 1 WHERE room_number = (SELECT room_number FROM reservations WHERE reservation_id = ?)''',
            (reservation_id,))

        # Update the available status of the newly reserved room
        c.execute('''UPDATE rooms SET available = 0 WHERE room_number = ?''', (room_number,))

        conn.commit()

    except Exception as e:
            print("An error has occurred : {}".format(e))

# Function to delete the reservation
def delete_reservation(reservation_id):
    try:

        # Get the room number of the reservation to delete4
        c.execute('''SELECT room_number FROM reservations WHERE reservation_id = ?''', (reservation_id,))
        room_number = c.fetchone()[0]

        # Update the available status of the room
        c.execute('''UPDATE rooms SET available = 1 WHERE room_number = ?''', (room_number,))

        # Delete the reservation record from the database
        c.execute('''DELETE FROM reservations WHERE reservation_id = ?''', (reservation_id,))

        conn.commit()

    except Exception as e:
            print("An error has occurred : {}".format(e))


# Interactive User Menu for customers
def user_menu():
    print('****** Welcome to the Hotel Room Reservation System!******')
    while True:

            print('Please choose an option:')
            print('1. View Available Rooms')
            print('2. Make a Reservation')
            print('3. Update Reservation')
            print('4. Delete Reservation')
            print('5. View Reservations')
            print('6. Exit')
            print('Enter your choice:')

            choice = input()

            if choice == '1':
                c.execute('''SELECT room_number, room_type, rate FROM rooms WHERE available = 1''')
                available_rooms = c.fetchall()

                if not available_rooms:
                    print('No rooms are currently available.')
                else:
                    print('Available Rooms:')
                    for room in available_rooms:
                        print(f'Room Number: {room[0]} - Room Type: {room[1]} - Rate: ${room[2]}')

            elif choice == '2':
                customer_name = input('Please enter your name: ')

                c.execute('''SELECT room_number, room_type, rate FROM rooms WHERE available = 1''')
                available_rooms = c.fetchall()

                if not available_rooms:
                    print('No rooms are currently available.')
                else:
                    print('Available Rooms are:')
                    for room in available_rooms:
                        print(f'Room Number: {room[0]} - Room Type: {room[1]} - Rate: ${room[2]}')

                    room_number = int(input('Please enter the room number you would like to reserve: '))

                    check_in_date = input('Please enter your check-in date (YYYY-MM-DD): ')
                    check_out_date = input('Please enter your check-out date (YYYY-MM-DD): ')

                    if check_availability(room_number, check_in_date, check_out_date):
                        room_type = c.execute('''SELECT room_type FROM rooms WHERE room_number = ?''', (room_number,)).fetchone()[0]
                        total_cost = calculate_cost(room_type, check_in_date, check_out_date)

                        print(f'The total cost for your reservation is: ${total_cost}')

                        confirm = input('Would you like to confirm your reservation? (y/n): ')

                        if confirm.lower() == 'y':
                            make_reservation(customer_name, room_number, check_in_date, check_out_date, total_cost)
                            print('Wohoo!! Your reservation confirmed!')
                        else:
                            print('Sorry, Your Reservation is canceled.')

                    else:
                        print('Sorry!, the room is not available for the selected dates.')

            elif choice == '3':
                customer_name = input('Please enter your name: ')

                c.execute('''SELECT * FROM reservations WHERE customer_name = ?''', (customer_name,))
                reservations = c.fetchall()

                if not reservations:
                    print('****Sorry! No reservations found under that name****.')
                else:
                    print('Your Reservations:')
                    for reservation in reservations:
                        print(
                            f'Reservation ID: {reservation[0]} - Room Number: {reservation[2]} - Check-In Date: {reservation[3]} - Check-Out Date: {reservation[4]} - Total Cost: ${reservation[5]}')

                    reservation_id = int(input('Please enter the ID of the reservation you would like to update: '))

                    reservation = c.execute('''SELECT * FROM reservations WHERE reservation_id = ?''', (reservation_id,)).fetchone()

                    if reservation:
                        if reservation[5] == 1:
                            print('Reservation has already been canceled.')
                        else:
                            print('Your current reservation:')
                            print(
                                f'Reservation ID: {reservation[0]} - Room Number: {reservation[2]} - Check-In Date: {reservation[3]} - Check-Out Date: {reservation[4]} - Total Cost: ${reservation[5]}')

                            room_number = int(input('Please enter the new room number: '))
                            check_in_date = input('Please enter your new check-in date (YYYY-MM-DD): ')
                            check_out_date = input('Please enter your new check-out date (YYYY-MM-DD): ')

                            if check_availability(room_number, check_in_date, check_out_date):
                                room_type = c.execute('''SELECT room_type FROM rooms WHERE room_number = ?''', (room_number,)).fetchone()[0]
                                total_cost = calculate_cost(room_type, check_in_date, check_out_date)

                                print(f'The total cost for your updated reservation is: ${total_cost}')

                                confirm = input('Would you like to confirm your updated reservation? (y/n): ')

                                if confirm.lower() == 'y':
                                    update_reservation(reservation_id, room_number, check_in_date, check_out_date, total_cost)
                                    print('Your reservation is updated successfully!')
                                else:
                                    print('Sorry! Your reservation update is canceled.')

                            else:
                                print('**** Sorry!, the room is not available for the selected dates.****')

                    else:
                        print('*****Sorry! No reservation found with that ID.*****')

            elif choice == '4':

                customer_name = input('Please enter the customer name: ')

                c.execute('''SELECT * FROM reservations WHERE customer_name = ?''', (customer_name,))
                reservations = c.fetchall()

                if not reservations:
                    print('No reservations found under that name.')

                else:
                    print('Your Reservations:')
                    for reservation in reservations:
                        print(
                            f'Reservation ID: {reservation[0]} - Room Number: {reservation[2]} - Check-In Date: {reservation[3]} - Check-Out Date: {reservation[4]} - Total Cost: ${reservation[5]}')

                reservation_id = int(input('Please enter the reservation ID you would like to delete: '))

                confirm = input(f'Are you sure you want to cancel reservation {reservation_id}? (y/n): ')
                if confirm.lower() == 'y':
                    delete_reservation(reservation_id)
                    print('Your current reservation is cancelled!')
                else:
                    print('Your reservation is not cancelled.')

            elif choice == '5':
                c.execute('''SELECT * FROM reservations ''')
                reservations = c.fetchall()
                if not reservations:
                    print('***** No reservations found *****.')

                else:
                    print('Your Reservations:')
                    for reservation in reservations:
                        print(
                            f'Reservation ID: {reservation[0]} - Customer Name: {reservation[1]} - Room Number: {reservation[2]} - Check-In Date: {reservation[3]} - Check-Out Date: {reservation[4]} - Total Cost: ${reservation[5]}')

            elif choice == '6':
                print('***** Thank you for using the Hotel Room Reservation System!*****')
                break

            else:
                print('Invalid choice. Please choose again.')


# Function to add data for rooms before reservations
# We can also do this with the help of a csv file. We can add this data to rooms.csv file,
# read the data from it and add it to the rooms table in the database.

def populate_data():
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (101, 'Single room', 50, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (102, 'Single room', 50, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (103, 'Single room', 50, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (104, 'Single room', 50, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (105, 'Double room', 100, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (106, 'Double room', 100, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (107, 'Double room', 100, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (108, 'Double room', 100, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (109, 'Penthouse Suite', 300, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (110, 'Penthouse Suite', 300, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (111, 'Penthouse Suite', 300, 1)''')
    c.execute('''INSERT INTO rooms(room_number, room_type, rate, available)
                 VALUES (112, 'Penthouse Suite', 300, 1)''')

    conn.commit()

# Main function
if __name__ == '__main__':
    create_tables()
    populate_data()
    user_menu()
    conn.close()
