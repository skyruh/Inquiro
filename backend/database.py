import mysql.connector

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "inquiro"
}

def get_db(config=None):
    cfg = config or MYSQL_CONFIG
    return mysql.connector.connect(**cfg)

def init_master_db(config=None):
    cfg = (config or MYSQL_CONFIG).copy()
    db_name = cfg.pop("database", "inquiro")

    try:
        # Step 1: Connect to MySQL server and ensure database exists
        server_conn = mysql.connector.connect(**cfg)
        server_cursor = server_conn.cursor()
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        server_conn.commit()
        server_cursor.close()
        server_conn.close()

        # Step 2: Connect to inquiro database and create tables
        cfg["database"] = db_name
        conn = mysql.connector.connect(**cfg)
        cursor = conn.cursor()

        # Domain metadata tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS variants (
            id VARCHAR(50) PRIMARY KEY,
            template_id VARCHAR(50) NOT NULL,
            variant_name VARCHAR(100) NOT NULL,
            FOREIGN KEY (template_id) REFERENCES templates(id)
        );
        """)

        # Hospital domain tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospital_doctors (
            doctor_id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            specialty VARCHAR(100) NOT NULL,
            consultation_fee INT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospital_patients (
            patient_id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT NOT NULL,
            gender VARCHAR(10) NOT NULL,
            city VARCHAR(100) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospital_appointments (
            appointment_id INT PRIMARY KEY,
            doctor_id INT NOT NULL,
            patient_id INT NOT NULL,
            appointment_date DATE NOT NULL,
            bill_amount INT NOT NULL,
            FOREIGN KEY (doctor_id) REFERENCES hospital_doctors(doctor_id),
            FOREIGN KEY (patient_id) REFERENCES hospital_patients(patient_id)
        );
        """)

        # Seed metadata
        cursor.execute("INSERT IGNORE INTO templates VALUES ('hospital', 'Hospital Management', 'Doctors, patients, and appointment billings');")
        cursor.execute("INSERT IGNORE INTO variants VALUES ('hospital_v1', 'hospital', 'Standard Hospital');")

        # Seed doctors
        doctors = [
            (1, 'Dr. Sarah Smith', 'Cardiology', 500),
            (2, 'Dr. Raj Patel', 'Neurology', 700),
            (3, 'Dr. Emily Brown', 'Pediatrics', 400),
            (4, 'Dr. Michael Chen', 'Orthopedics', 600)
        ]
        cursor.executemany("INSERT IGNORE INTO hospital_doctors VALUES (%s, %s, %s, %s);", doctors)

        # Seed patients
        patients = [
            (101, 'John Doe', 45, 'Male', 'New York'),
            (102, 'Alice Walker', 29, 'Female', 'Boston'),
            (103, 'Robert Lee', 62, 'Male', 'Chicago'),
            (104, 'Maria Garcia', 34, 'Female', 'New York'),
            (105, 'David Kim', 51, 'Male', 'Seattle')
        ]
        cursor.executemany("INSERT IGNORE INTO hospital_patients VALUES (%s, %s, %s, %s, %s);", patients)

        # Seed appointments
        appointments = [
            (1001, 1, 101, '2026-03-10', 1200),
            (1002, 2, 103, '2026-03-11', 2500),
            (1003, 3, 102, '2026-03-12', 450),
            (1004, 1, 104, '2026-03-15', 1800),
            (1005, 4, 105, '2026-03-16', 3200),
            (1006, 2, 101, '2026-03-18', 1400)
        ]
        cursor.executemany("INSERT IGNORE INTO hospital_appointments VALUES (%s, %s, %s, %s, %s);", appointments)

        conn.commit()
        cursor.close()
        conn.close()
        print("MySQL master database initialized with hospital domain data.")

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        print("Tip: Ensure your MySQL service (e.g. XAMPP) is running and verify root password in MYSQL_CONFIG.")

if __name__ == "__main__":
    init_master_db()
