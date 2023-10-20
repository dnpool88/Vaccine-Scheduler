from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import re


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length of the tokens has to be exactly 3
    if len(tokens) != 3:
        print("Failed to create user.")
        return
    
    user = tokens[1]
    password = tokens[2]
    # check 2: the username does not exist in the system
    if username_exists_patient(user):
        print("Username taken, try again!")
        return

    # check 3: the password is a strong one, and passes a few tests
    check = 0
    len_check = 0
    num_check = 0
    spe_check = 0
    if len(password) >= 8:
        len_check = 1
    for char in password: 
        if ord(char) >= 48 and ord(char) <=57:# check for numbers
            num_check = 1
        elif ord(char)==64 or ord(char)==33 or ord(char)==35 or ord(char)==63:
            # check for special characters
            spe_check = 1
    
    check = len_check + num_check + spe_check
    if check != 3:
        print("Password is not strong enough, try again!")
        print("A Password needs at least 8 characters, a Capital letter,")
        print("A number, and one of 4 special characters (!, @, #, ?)")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

     # create the patient
    patient = Patient(user, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", user)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # check 3: the password is a strong one, and passes a few tests
    check = 0
    len_check = 0
    num_check = 0
    spe_check = 0
    if len(password) >= 8:
        len_check = 1
    for char in password: 
        if ord(char) >= 48 and ord(char) <=57:# check for numbers
            num_check = 1
        elif ord(char)==64 or ord(char)==33 or ord(char)==35 or ord(char)==63:
            # check for special characters
            spe_check = 1
    
    check = len_check + num_check + spe_check
    if check != 3:
        print("Password is not strong enough, try again!")
        print("A Password needs at least 8 characters, a Capital letter,")
        print("A number, and one of 4 special characters (!, @, #, ?)")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # check 1: either a caregiver or patient is logged in
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    # check 2: length of tokens must be exactly 2
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    date_tokens = date.split("-")
    # check 3: tokens inputted is a date
    if len(date_tokens) != 3:
        print("Invalid Format, try again!")
        return
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # gets all rows from availability table at an inputted date, as well as all vaccine names and doses
    check_availability = "Select A.Username, V.name, V.doses From Availabilities as A, Vaccines as V where A.time = %d Order By A.Username;"
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(check_availability, (d))
        all_caregivers = []
        caregivers = []
        vaccine_name = []
        vaccine_num = []

        for row in cursor:
            all_caregivers.append(row[0])
            vaccine_name.append(row[1])
            vaccine_num.append(row[2])

        # removes duplicate caregivers while also retaining the order
        [caregivers.append(x) for x in all_caregivers if x not in caregivers]

        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        raise
    finally:
        cm.close_connection()
    
    if not caregivers:
        print("Sorry, No Caregivers Available!")
    else:
        print("Caregivers Available:")
        print(*caregivers)
        print("Vaccines & Doses Available:")
        for name, num in zip(vaccine_name, vaccine_num):
            print(name + ": " + str(num))


def reserve(tokens):
    global current_caregiver
    global current_patient
    # check 1: patient is logged in
    if current_caregiver is not None:
        print("Please login as a patient!")
        return
    elif current_patient is None:
        print("Please login first!")
        return

    # check 2: length of tokens is exactly 3
    if len(tokens) != 3:
        print("Please try again!")
        return

    
    

    date = tokens[1]
    vaccine_name = tokens[2]
    date_tokens = date.split("-")
    # check 3: inputed tokens is in correct format:
    if len(date_tokens) != 3:
        print("Invalid Format, try again!")
        return

    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    caregiver = None
    vaccine_doses = None

    reserve = "Select A.Username, V.doses From Availabilities as A, Vaccines as V where A.time = %d And V.name = %s Order By A.Username DESC;"
    try:    
        d = datetime.datetime(year, month, day)
        cursor.execute(reserve, (d, vaccine_name))

        for row in cursor:
            caregiver = row[0]
            vaccine_doses = row[1]
        
        if not caregiver:
            print("No Caregiver is available!")
            return
        vaccine = Vaccine(vaccine_name, vaccine_doses).get()
        
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        raise
  
    # check 4: there are enough doses of the vaccine
    if vaccine.get_available_doses == 0:
        print("Not enough available doses!")

    current_patient.make_appointment(caregiver, d, vaccine_name)
    vaccine.decrease_available_doses(1)

    # drops caregiver date from availabilties table
    drop_date = "Delete From Availabilities Where time = %d And Username = %s"
    try:
        cursor.execute(drop_date, (d, caregiver))    

        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        raise

    # gets the appointment id
    get_id = "Select Appointment_ID from Appointments where time = %d And Caregiver_user = %s;"
    try:
        cursor.execute(get_id, (d, caregiver))    
        for row in cursor:
            id = row[0]

        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        raise
    finally:
        cm.close_connection()

    print("Successfully Reserved Appointment!")
    print("Appointment ID: " + str(id) + ", Caregiver username: " + caregiver)


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    global current_caregiver
    global current_patient
    # check 1: either patient or caregiver is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # don't need to check for token length because this method is not taking in any data
    
    if current_caregiver is not None:
        name = current_caregiver.get_username()
        schedule = "Select Appointment_ID, time, Patient_User, Vaccine_Name from Appointments where Caregiver_user = %s Order By Appointment_ID;"
    else:
        name = current_patient.get_username()
        schedule = "Select Appointment_ID, time, Caregiver_User, Vaccine_Name from Appointments where Patient_user = %s Order By Appointment_ID;"

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    # gets all the rows from the Appointment table with the name of the user logged in
    try:
        cursor.execute(schedule, (name))
        
        for row in cursor:
            id = row[0]
            date = row[1]
            other_name = row[2]
            vaccine_name = row[3]

            print("Appointment ID: " + str(id) + " Vaccine: " + vaccine_name + " Date: " + str(date) + " Caregiver/Patient: " + other_name)
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        raise
    finally:
        cm.close_connection()

def logout(tokens):
    global current_caregiver
    global current_patient
    # check 1: either patient or caregiver is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # don't need to check for token length because this method is not taking in any data

    try:
        current_caregiver = None
        current_patient = None
    except Exception as e:
        print("Please try again!")
        return
    
    print("Successfully logged out!")


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()