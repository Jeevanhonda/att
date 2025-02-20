import pandas as pd
import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu

def app():
    st.title("Remove the Existing Staff")
    # Create a new SQLite connection for the current thread
    mydb = sqlite3.connect("attendance.db")
    mycursor = mydb.cursor()

    # Load data from `staff_detail`
    df = pd.read_sql("SELECT * FROM staff_detail", mydb)

    # Select Employee Name from dropdown
    dele = st.selectbox("Select the Employee Name", df["Name"])
    left_date = st.date_input("Staff Left Date")

    # Filter the data for the selected name
    df1 = df[df["Name"] == dele]
    df1.index = range(1, len(df1) + 1)
    st.write(df1)

    if st.button("Delete"):
        # Create the `staff_left_detail` table with the new columns if it doesn't exist
        create_query = '''
        CREATE TABLE IF NOT EXISTS staff_left_detail (
            E_Code VARCHAR(50), 
            Name VARCHAR(50),
            BRANCH VARCHAR(50), 
            DEPT VARCHAR(50), 
            DESIGNATION VARCHAR(50), 
            ACTUAL_GROSS INTEGER,
            ESI VARCHAR(50), 
            Acc_no BIGINT,
            Ifsc_code VARCHAR(50),
            Bank_Name VARCHAR(50),
            DATE_OF_JOIN DATE,
            phone_no VARCHAR(15),
            working_status TEXT DEFAULT 'INACTIVE',
            left_date DATE
        )'''
        mycursor.execute(create_query)
        mydb.commit()

        # Ensure `df1` has exactly one row for insertion
        if not df1.empty:
            for index, row in df1.iterrows():
                # Extract data as a tuple
                values = (
                    row["E_Code"], row["Name"], row["BRANCH"], row["DEPT"], row["DESIGNATION"], row["ACTUAL_GROSS"],
                    row["ESI"], row["Acc_no"], row["Ifsc_code"], row["Bank_Name"], row["DATE_OF_JOIN"],
                    row["Phone_Number"],  # Fetching phone number
                    "INACTIVE", left_date.strftime('%Y-%m-%d')  # Convert to string in 'YYYY-MM-DD' format
                )

                # Insert the data into `staff_left_detail`
                insert_query = """INSERT INTO staff_left_detail (
                    E_Code, Name, BRANCH, DEPT, DESIGNATION, ACTUAL_GROSS,
                    ESI, Acc_no, Ifsc_code, Bank_Name, DATE_OF_JOIN, phone_no, working_status, left_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                mycursor.execute(insert_query, values)
                mydb.commit()

            # Delete the selected staff detail from `staff_detail`
            delete_query = "DELETE FROM staff_detail WHERE Name = ?"
            mycursor.execute(delete_query, (dele,))
            mydb.commit()

            st.success(f"Successfully deleted the staff detail of {dele} and moved it to 'staff_left_detail'.")
        else:
            st.error(f"No details found for {dele}. Please select a valid name.")

    # Display the updated `staff_left_detail` table
    st.markdown("### Left Staff Detail")
    df5 = pd.read_sql("SELECT * FROM staff_left_detail", mydb)
    df5.index = range(1, len(df5) + 1)
    st.write(df5)
