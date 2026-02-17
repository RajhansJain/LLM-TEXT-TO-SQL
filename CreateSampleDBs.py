import sqlite3
# TestDB.py
def create_modern_db():
    conn = sqlite3.connect('business.db')
    cursor = conn.cursor()
    
    # Create Tables
    cursor.execute("CREATE TABLE IF NOT EXISTS PRODUCTS(ID INT, NAME TEXT, CATEGORY TEXT, PRICE REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS SALES(ID INT, PRODUCT_ID INT, QUANTITY INT, TOTAL_PRICE REAL, DATE TEXT)")
    
    # Insert Sample Data
    cursor.executemany("INSERT INTO PRODUCTS VALUES (?,?,?,?)", [
        (1, 'Laptop', 'Electronics', 1200.00),
        (2, 'Mouse', 'Electronics', 25.00),
        (3, 'Desk Chair', 'Furniture', 150.00)
    ])
    
    cursor.executemany("INSERT INTO SALES VALUES (?,?,?,?,?)", [
        (101, 1, 2, 2400.00, '2026-01-15'),
        (102, 2, 5, 125.00, '2026-01-20'),
        (103, 3, 1, 150.00, '2026-02-05')
    ])
    
    conn.commit()
    conn.close()

def create_ecommerce_db():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS USERS(ID INT, NAME TEXT, EMAIL TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ORDERS(ID INT, USER_ID INT, PRODUCT TEXT, AMOUNT REAL)")
    
    cursor.executemany("INSERT INTO USERS VALUES (?,?,?)", [
        (1, 'Anjali', 'anjali@email.com'),
        (2, 'Rohit', 'rohit@email.com'),
        (3, 'Meera', 'meera@email.com')
    ])
    
    cursor.executemany("INSERT INTO ORDERS VALUES (?,?,?,?)", [
        (201, 1, 'Smartphone', 15000),
        (202, 2, 'Headphones', 2000),
        (203, 3, 'Keyboard', 1200)
    ])
    
    conn.commit()
    conn.close()

def create_library_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS BOOKS(ID INT, TITLE TEXT, AUTHOR TEXT, AVAILABLE INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS MEMBERS(ID INT, NAME TEXT, JOIN_DATE TEXT)")
    
    cursor.executemany("INSERT INTO BOOKS VALUES (?,?,?,?)", [
        (1, 'Python Basics', 'John Doe', 5),
        (2, 'Data Science 101', 'Jane Smith', 3),
        (3, 'AI Revolution', 'Elon Writer', 2)
    ])
    
    cursor.executemany("INSERT INTO MEMBERS VALUES (?,?,?)", [
        (1, 'Amit', '2026-01-01'),
        (2, 'Neha', '2026-01-15'),
        (3, 'Suresh', '2026-02-01')
    ])
    
    conn.commit()
    conn.close()

def create_ecommerce_db():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS USERS(ID INT, NAME TEXT, EMAIL TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ORDERS(ID INT, USER_ID INT, PRODUCT TEXT, AMOUNT REAL)")
    
    cursor.executemany("INSERT INTO USERS VALUES (?,?,?)", [
        (1, 'Anjali', 'anjali@email.com'),
        (2, 'Rohit', 'rohit@email.com'),
        (3, 'Meera', 'meera@email.com')
    ])
    
    cursor.executemany("INSERT INTO ORDERS VALUES (?,?,?,?)", [
        (201, 1, 'Smartphone', 15000),
        (202, 2, 'Headphones', 2000),
        (203, 3, 'Keyboard', 1200)
    ])
    
    conn.commit()
    conn.close()

def create_hospital_db():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS PATIENTS(ID INT, NAME TEXT, AGE INT, DISEASE TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS APPOINTMENTS(ID INT, PATIENT_ID INT, DOCTOR TEXT, DATE TEXT)")
    
    cursor.executemany("INSERT INTO PATIENTS VALUES (?,?,?,?)", [
        (1, 'Rahul', 45, 'Diabetes'),
        (2, 'Sneha', 30, 'Flu'),
        (3, 'Vikram', 60, 'Hypertension')
    ])
    
    cursor.executemany("INSERT INTO APPOINTMENTS VALUES (?,?,?,?)", [
        (101, 1, 'Dr. Sharma', '2026-02-10'),
        (102, 2, 'Dr. Mehta', '2026-02-11'),
        (103, 3, 'Dr. Rao', '2026-02-12')
    ])
    
    conn.commit()
    conn.close()

def create_student_db():
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    
    # Create Tables
    cursor.execute("CREATE TABLE IF NOT EXISTS STUDENTS(ID INT, NAME TEXT, AGE INT, COURSE TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS MARKS(STUDENT_ID INT, SUBJECT TEXT, SCORE INT)")
    
    # Insert Sample Data
    cursor.executemany("INSERT INTO STUDENTS VALUES (?,?,?,?)", [
        (1, 'Aman', 20, 'Computer Science'),
        (2, 'Riya', 21, 'Mechanical'),
        (3, 'Karan', 19, 'Electrical')
    ])
    
    cursor.executemany("INSERT INTO MARKS VALUES (?,?,?)", [
        (1, 'Maths', 85),
        (2, 'Physics', 78),
        (3, 'Circuits', 88)
    ])
    
    conn.commit()
    conn.close()

def create_banking_db():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS CUSTOMERS(ID INT, NAME TEXT, BALANCE REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS TRANSACTIONS(ID INT, CUSTOMER_ID INT, TYPE TEXT, AMOUNT REAL, DATE TEXT)")
    
    cursor.executemany("INSERT INTO CUSTOMERS VALUES (?,?,?)", [
        (1, 'Raj', 50000.00),
        (2, 'Simran', 75000.00),
        (3, 'Arjun', 30000.00)
    ])
    
    cursor.executemany("INSERT INTO TRANSACTIONS VALUES (?,?,?,?,?)", [
        (1001, 1, 'Deposit', 10000, '2026-02-01'),
        (1002, 2, 'Withdrawal', 5000, '2026-02-03'),
        (1003, 3, 'Deposit', 7000, '2026-02-05')
    ])
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_modern_db()
    create_ecommerce_db()
    create_library_db()
    create_hospital_db()
    create_student_db()
    create_banking_db()
