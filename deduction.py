import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime
import pytz

from streamlit_option_menu import option_menu

def app():
    mydb = sqlite3.connect("attendance.db", check_same_thread=False)
    mycur = mydb.cursor()

    st.title("Deduction")
    with st.sidebar:
        select_fun = option_menu("Menu", ["Deduct", "View Deduct Detail"])
    
    if select_fun=="Deduct":
        
        df = pd.read_sql("SELECT * FROM staff_detail", mydb)
        
        # Select name from the DataFrame
        name = st.selectbox("Select the name", df["Name"])
        
        # List of months
        months = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        
        col1, col2 = st.columns(2)  # Creates 2 columns
        
        # Use the first column for the first select box
        with col1:
            month = st.selectbox("Select the month", months)
        
        # Use the second column for the second select box
        with col2:
            year = st.number_input("Select the year", min_value=2024, max_value=3000, value=datetime.now().year)
            year=str(year)
        
        # Input fields for the amount and remark
        amt = st.number_input("Enter the amount",step=1)
        remark = st.text_area("Enter the detail")
        
        # Display the selected month and year
        current_year = datetime.now().year  # Define the current year
        st.write(f"Selected Month and Year: {month}{year[2:]}")
        month=month+year[2:]
        
        # Button to save the deduction to the database
        if st.button("Save Deduction"):
            # Insert the deduction record into the Deduction table
            mycur.execute("""
                CREATE TABLE IF NOT EXISTS Deduction (
                    Name TEXT,
                    Month TEXT,               
                    Amount INTEGER,
                    Remark TEXT
                );
            """)
            
            mycur.execute("""
                INSERT INTO Deduction (Name, Month,  Amount, Remark)
                VALUES (?, ?, ?,  ?)
            """, (name, month, amt, remark))
            
            mydb.commit()  # Commit the transaction
            st.success("Deduction record saved successfully.")

    if select_fun=="View Deduct Detail":
        col1, col2 = st.columns(2)  # Creates 2 columns
         # List of months
        months = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        
        # Use the first column for the first select box
        with col1:
            month = st.selectbox("Select the month", months)
        
        # Use the second column for the second select box
        with col2:
            year = st.number_input("Select the year", min_value=2024, max_value=3000, value=datetime.now().year)
            year=str(year)
        mn=month+year[2:]
        df=pd.read_sql("select * from Deduction",mydb)
        df=df[df["Month"]==mn]
        df.index=range(1,len(df)+1)
        st.write(df)

if __name__ == "__main__":
    app()
