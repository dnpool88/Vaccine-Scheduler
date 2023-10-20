CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

Create Table Patients (
    Username varchar(255),
    Salt Binary(16),
    Hash Binary(16),
    Primary Key (Username)
);

Create Table Appointments (
    Appointment_ID int IDENTITY(1,1),
    Time date,
    Patient_user varchar(255) References Patients,
    Caregiver_user varchar(255) References Caregivers,
    Vaccine_name varchar(255) References Vaccines, 
    Primary Key (Appointment_ID)
);