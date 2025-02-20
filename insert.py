import pandas as pd
import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu
from datetime import datetime

def app():
    # Connect to SQLite database
    mydb = sqlite3.connect("attendance.db")
    mycursor = mydb.cursor()

    st.subheader("INSERT STAFF DETAIL")
   
    # Input fields for staff details
    e_code = st.text_input("Enter the Employee Code")
    name1 = st.text_input("Enter name:")
    branchs = ["Palanganatham", "Kamarakar Salai", "Thirunagar", "Nagamalai Puthukottai", "Thirumangalam", "Aruppukottai"]
    branch = st.selectbox("Select the branch name", branchs)
    dep = ["Accounts & Admin", "Sales Department", "Service Department"]
    dept = st.selectbox("Select the department name:", dep)
    desg = [
        'AGM', 'Accounts Executive', 'Accounts Manager', 'Accounts cashier', 'Assistant Sales Manager', 'Bodyshop Incharge',
        'Branch Incharge', 'CRE Service', 'CRM', 'Cashier', 'Cashier &  Accounts Exe', 'Delivery Incharge', 'Digital marketing',
        'Direct Marketting ', 'Driver', 'EDP CUM System Admin', 'Electrician', 'Final Inspector', 'Floor Inspection', 'General Manager',
        'HR Executive', 'Insurance Executive', 'Network Manager', 'Outside Job', 'PDI', 'PDI Executive', 'PDI Incharger', 'Parts Assistant',
        'Parts Billing', 'Parts Incharge', 'Parts Manager', 'Purchase Manager', 'RTO Executive', 'Sales Billing', 'Sales Executive',
        'Sales Receptionist', 'Senior Sales Executive', 'Senior Technician', 'Service Advisor', 'Service Billing', 'Service Cashier',
        'Service Incharge', 'Service Manager', 'Service Receptionist', 'Sr.HR Executive', 'Technician', 'Warranty Supervisor', 'Water Wash'
    ]
    des = st.selectbox("Select the designation", desg)
    salary1 = st.number_input("Enter salary:", step=1000)
    esi = st.selectbox("Select the ESI status", ["Yes", "Noo"])
    doj = st.date_input("Select the Date of Joining:")
    acc = st.number_input("Enter the account number:", min_value=0, step=1, format="%d")
    ifsc = st.text_input("Enter the IFSC code")
    banks_in_tamil_nadu = [
                            "AXIS BANK LTD",
                            "BANK OF BARODA",
                            "BANK OF INDIA",
                            "BARB0ANNANA",
                            "CANARA BANK",
                            "CITY UNION BANK",
                            "Canara Bank",
                            "City Union Bank",
                            "HDFC BANK",
                            "HDFC BANK LTD",
                            "ICICI BANK",
                            "ICICI BANK LTD",
                            "INDIAN BANK",
                            "INDIAN OVERSEAS BANK",
                            "INDIAN OVERSES BANK",
                            "Indian Bank",
                            "Indian Overseas Bank",
                            "KARUR VYSYA BANK",
                            "KOTAK MAHINDRA BANK",
                            "Karur Vysya Bank",
                            "STATE BABK OF INDIA",
                            "STATE BANK OF INDIA",
                            "State Bank of India",
                            "TAMILNADU MERCANTILE BANK",
                            "UCO BANK",
                            "UNION BANK",
                            "UNION BANK OF INDIA",
                            "Ujjivan Small Finance Bank Ltd",
                        ]


    bank_name = st.selectbox("Enter the Bank Name",banks_in_tamil_nadu)
    phone_num = st.number_input("Enter The Phone Number", min_value=0, step=1)

    if acc == 0:
        acc = None

    if st.button("Insert staff details"):
        # Create the staff_detail table if it doesn't exist
        create_staff_table = '''
        CREATE TABLE IF NOT EXISTS staff_detail (
            E_Code VARCHAR(50) PRIMARY KEY,
            Name VARCHAR(50),
            BRANCH VARCHAR(50),
            DEPT VARCHAR(50),
            DESIGNATION VARCHAR(50),
            ACTUAL_GROSS INTEGER,
            ESI VARCHAR(50),
            Acc_no VARCHAR(255),
            Ifsc_code VARCHAR(50),
            Bank_Name VARCHAR(50),
            DATE_OF_JOIN DATE,
            Phone_Number INTEGER
        )
        '''
        mycursor.execute(create_staff_table)
        mydb.commit()

        # Insert staff details into staff_detail table
        staff_query = '''
        INSERT INTO staff_detail (
            E_Code, Name, BRANCH, DEPT, DESIGNATION, ACTUAL_GROSS, ESI, Acc_no, Ifsc_code, Bank_Name, DATE_OF_JOIN, Phone_Number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        staff_values = (e_code, name1, branch, dept, des, salary1, esi, acc, ifsc, bank_name, doj, phone_num)

        # Determine attendance table and columns
        current_month_name = doj.strftime("%B")
        current_year = doj.strftime("%y")
        attendance_table = f"{current_month_name}{current_year}"

        # Create attendance table if it doesn't exist
        create_attendance_table = f'''
        CREATE TABLE IF NOT EXISTS {attendance_table} (
            E_Code VARCHAR(50),
            Name VARCHAR(50),
            BRANCH VARCHAR(50),
            DEPT VARCHAR(50),
            DESIGNATION VARCHAR(50)
        )
        '''
        mycursor.execute(create_attendance_table)

        # Add columns dynamically for each day of the month up to DOJ
        total_days = doj.day
        for day in range(1, total_days ):
            column_name = f"'{day:02d}'"  # Format as two-digit day
            try:
                # Check if the column exists
                mycursor.execute(f"PRAGMA table_info({attendance_table})")
                columns = [row[1] for row in mycursor.fetchall()]  # Get column names
                if f"{day:02d}" not in columns:
                    # Add the column if it doesn't exist
                    mycursor.execute(f"ALTER TABLE {attendance_table} ADD COLUMN {column_name} TEXT DEFAULT 'LP'")
            except Exception as e:
                st.error(f"Error adding column {column_name}: {str(e)}")

        # Insert the new staff into the attendance table with LP for all past days
        attendance_columns = ["E_Code", "Name", "BRANCH", "DEPT", "DESIGNATION"] + [f"'{day:02d}'" for day in range(1, total_days + 1)]
        attendance_placeholders = ", ".join(["?"] * len(attendance_columns))
        attendance_query = f"INSERT INTO {attendance_table} ({', '.join(attendance_columns)}) VALUES ({attendance_placeholders})"
        attendance_values = (e_code, name1, branch, dept, des) + tuple(["LP"] * total_days)

        try:
            # Execute both insertions
            mycursor.execute(staff_query, staff_values)
            mycursor.execute(attendance_query, attendance_values)
            mydb.commit()
            st.success(f"Successfully inserted the staff detail of {name1} with salary {salary1}. Attendance initialized.")
        except Exception as e:
            st.error(f"Error inserting data: {str(e)}")

# Run the app
if __name__ == "__main__":
    app()
