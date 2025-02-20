import pandas as pd
import streamlit as st
import sqlite3
import calendar
import os
from streamlit_option_menu import option_menu
from datetime import time
import numpy as np

# Function to extract year and month from a string and get the number of days
def get_days_in_month_from_string(date_str):
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8, "September": 9,
        "October": 10, "November": 11, "December": 12
    }
    for month_name in months:  # Iterate over month names
        if month_name in date_str:
            month = months[month_name]
            year = int(date_str.replace(month_name, "").strip())
            break
    else:
        raise ValueError("Invalid date string format. Expected format like 'December24'")
    return calendar.monthrange(year, month)[1]

# Streamlit application
def app():
    st.title("Salary Calculation")  # App title
    
    # Database connection
    mydb = sqlite3.connect("attendance.db", check_same_thread=False)
    mycur = mydb.cursor()
    with st.sidebar:
        select_fun = option_menu("Menu", ["Salary","Sunday"])

    if select_fun=="Salary":
            
    
        # Query to list all tables
        mycur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in mycur.fetchall()]
        table_list = [t for t in tables if any(t.startswith(month) for month in calendar.month_name[1:])]
    
        table_name = st.selectbox("Select the table to calculate the salary", table_list)
        
        if st.button("Calculate"):
            # Read attendance data
            df = pd.read_sql(f"SELECT * FROM {table_name}", mydb)
            attendance_columns = df.columns[5:]  # Attendance columns start after the 5th column
            dayss = len(df.columns) - 5
            
            # Calculating attendance categories
            df['No_of_P'] = df[attendance_columns].apply(lambda row: (row == 'P').sum(), axis=1)
            df['No_of_LP'] = df[attendance_columns].apply(lambda row: (row == 'LP').sum(), axis=1)
            df['No_of_HLP'] = df[attendance_columns].apply(lambda row: (row == 'HLP').sum(), axis=1)
            df["No_of_CL"] = df[attendance_columns].apply(lambda row: (row == 'CL').sum(), axis=1)
            df["No_of_COF"] = df[attendance_columns].apply(lambda row: (row == 'COF').sum(), axis=1)
            df["No_of_LOP"] = df["No_of_LP"] + (df["No_of_HLP"] / 2)
            
            if table_name:
                # Extract month and year from table name (e.g., "January24")
                month_name, year_suffix = table_name[:-2], table_name[-2:]
                month_number = list(calendar.month_name).index(month_name)
                year_full = 2000 + int(year_suffix)
                _, days = calendar.monthrange(year_full, month_number)
                df["No_of_days"] = days
            
            # Calculate Paid_days
            df["Paid_days"] = dayss - df["No_of_LOP"]
    
            # Read staff details
            df2 = pd.read_sql("SELECT * FROM staff_detail", mydb)
            df2 = df2[["E_Code", "Name", "ACTUAL_GROSS", "DATE_OF_JOIN", "ESI", "Acc_no", "Ifsc_code", "Bank_Name"]]
            
            df22 = pd.read_sql("SELECT * FROM staff_left_detail", mydb)
            df22 = df22[["E_Code", "Name", "ACTUAL_GROSS", "DATE_OF_JOIN", "ESI", "Acc_no", "Ifsc_code", "Bank_Name"]]
            
            # Combine staff details
            df_combined = pd.concat([df2, df22], ignore_index=True)
            
            # Merge attendance with staff details
            df3 = pd.merge(df, df_combined, on="E_Code", how="inner")
    
            # Salary calculation
            df3["Salary_as_per_Attendance"] = round(df3["ACTUAL_GROSS"] / df3["No_of_days"] * df3["Paid_days"], 0)
            df3["BASIC"] = round(df3["Salary_as_per_Attendance"] * 0.60, 0)
            df3["DA"] = round(df3["Salary_as_per_Attendance"] * 0.10, 0)
            df3["HRA"] = round(df3["Salary_as_per_Attendance"] * 0.30, 0)
    
            # Apply ESI and PF conditions
            df3.loc[df3["ESI"] == "Yes", "PF AMT"] = round((df3["BASIC"] + df3["DA"]) * 0.12, 0)
            df3.loc[df3["ESI"] == "Yes", "ESI AMT"] = round((df3["BASIC"] + df3["DA"] + df3["HRA"]) * 0.0075, 0)
            df3.loc[(df3["ESI"] == "Yes") & ((df3["BASIC"] + df3["DA"]) > 15000), "ESI AMT"] = 0
            df3.loc[(df3["ESI"] == "Yes") & ((df3["BASIC"] + df3["DA"]) > 15000), "PF AMT"] = 1800
            df3.loc[df3["ESI"] == "Noo", ["PF AMT", "ESI AMT"]] = 0
    
            df3["Net_Salary"] = df3["Salary_as_per_Attendance"] - df3["PF AMT"] - df3["ESI AMT"]
    
            # Merge with deduction table
            df4 = pd.read_sql("SELECT * FROM Deduction", mydb)
            df4 = df4[df4["Month"] == table_name]
            df3.rename(columns={"Name_x": "Name"}, inplace=True)
            df5 = pd.merge(df3, df4, how="outer", on="Name")
            df5.rename(columns={"Amount": "Deduction"}, inplace=True)
            df5["Deduction"] = df5["Deduction"].fillna(0)
            df5["Net_Salary"] = df5["Net_Salary"] - df5["Deduction"]
    
            df5 = df5.drop_duplicates(subset="E_Code", keep="first")
            df5 = df5[df5["Net_Salary"] > 0]
    
            # Final DataFrame columns
            df5 = df5[[
                "E_Code", "Name", "BRANCH", "DEPT", "DESIGNATION", "DATE_OF_JOIN", "ACTUAL_GROSS",
                "Acc_no", "Ifsc_code", "Bank_Name", "No_of_P", "No_of_LP", "No_of_HLP", "No_of_CL",
                "No_of_COF", "No_of_LOP", "No_of_days", "Paid_days", "Salary_as_per_Attendance",
                "BASIC", "DA", "HRA", "ESI", "PF AMT", "ESI AMT", "Deduction", "Remark", "Net_Salary"
            ]]
    
            df5.index = range(1, len(df5) + 1)
           
            # Extract month and year from selection
            selected_month_name = ''.join([c for c in table_name if not c.isdigit()])  # Extract month name
            selected_year_suffix = ''.join([c for c in table_name if c.isdigit()])  # Extract year
            selected_month = list(calendar.month_name).index(selected_month_name)  # Month number
            selected_year = int("20" + selected_year_suffix)  # Full year
            
            # Function to highlight rows based on selected month and year
            def highlight_rows(row):
                # Ensure 'DATE_OF_JOIN' is in datetime format
                row['DATE_OF_JOIN'] = pd.to_datetime(row['DATE_OF_JOIN'], errors='coerce')
                if pd.notnull(row['DATE_OF_JOIN']) and row['DATE_OF_JOIN'].month == selected_month and row['DATE_OF_JOIN'].year == selected_year:
                    return ['background-color: yellow' for _ in row]
                else:
                    return ['' for _ in row]
            
            # Apply the styling
            attendance_df_styled = df5.style.apply(highlight_rows, axis=1)
            
            # Display the styled DataFrame
            st.write(attendance_df_styled)
            total_salary = df5["Net_Salary"].sum()
            footer_style = f"""<style>.footer {{position: fixed;bottom: 0;right: 0;color: #ff0004;background-color: #c1ee6e;padding: 10px;font-size: 25px;border-radius: 10px;}}</style><div class="footer">NET SALARY AMOUNT : ₹{total_salary}</div>"""

            
            st.markdown("Save the file as month and year as like this (November24)")
            st.markdown("Save in this folder E:\share\salary report")
            st.markdown(footer_style, unsafe_allow_html=True)
            
    
    
           
    if "temp_data" not in st.session_state:
        st.session_state.temp_data = []
    
    if select_fun == "Sunday":
        # Fetch data from the database
        df = pd.read_sql("SELECT * FROM staff_detail", mydb)
        
        # Selectbox for existing names
        col1, col2 = st.columns(2)
        with col1:
            selected_name = st.selectbox("Select the Name", df["Name"], key="selectbox_name")  
        with col2:
            No_of_days = st.number_input("Enter the No of Days", value=30)
    
        # Filter data for the selected name
        df_sal = df[df["Name"] == selected_name]
        st.write(df_sal)
        
        # Get the default values
        salary_default = df_sal["ACTUAL_GROSS"].iloc[0] if not df_sal.empty else 0
        dept = df_sal["DEPT"].iloc[0] if not df_sal.empty else ""
        des = df_sal["DESIGNATION"].iloc[0] if not df_sal.empty else ""
        
        # Input for additional data
        col1, col2 = st.columns(2)
        with col1:
            custom_name = st.text_input("Or Enter a New Name", key="textinput_name")
            in_time = st.time_input("Select the In Time", value=time(9, 0), step=60)
            Department = st.text_input("Enter The Department", value=dept)
        with col2:
            salary = st.number_input("Enter the Salary", value=salary_default)
            out_time = st.time_input("Select the Out Time", value=time(14, 0))
            Designation = st.text_input("Enter the Designation", value=des)
        
        # Final name logic
        final_name = custom_name if custom_name else selected_name
    
        # Add and Clear buttons
        cols1, cols2, cols3 = st.columns(3)
        with cols2:
            if st.button("ADD"):
                st.session_state.temp_data.append({
                    "Name": final_name,
                    "Department": Department,
                    "Designation": Designation,                    
                    "In Time": in_time.strftime("%H:%M"),
                    "Out Time": out_time.strftime("%H:%M"),
                    "Salary": salary,
                })
                st.success("Data added temporarily!")
        
        if st.button("Clear Data"):
            st.session_state.temp_data = []
            st.success("Temporary data cleared!")
        
        # Display and process data
        if st.session_state.temp_data:
            df4 = pd.DataFrame(st.session_state.temp_data)
            
            # Convert 'In Time' and 'Out Time' to datetime format
            df4["In Time"] = pd.to_datetime(df4["In Time"], format='%H:%M', errors='coerce')
            df4["Out Time"] = pd.to_datetime(df4["Out Time"], format='%H:%M', errors='coerce')
            
            # Calculate Working Hours
            df4["Working Hours"] = (df4["Out Time"] - df4["In Time"]).dt.total_seconds() / 3600
            
            # Convert Working Hours to time format (HH:MM:SS)
            df4["Working Hours"] = df4["Working Hours"].apply(
                lambda x: f"{int(x):02}:{int((x % 1) * 60):02}:{int(((x % 1) * 60 % 1) * 60):02}"
            )
            
            # Calculate Sunday Salary
            df4["Sun_Sal"] = np.where(
                df4["Working Hours"].str[:2].astype(int) > 4.75,
                round((df4["Salary"] / No_of_days) * 1),
                round((df4["Salary"] / No_of_days) / 2)
            )
            
            # Apply rounding logic
            def round_to_nearest_10(value):
                last_digit = value % 10
                if last_digit == 0:
                    return value
                elif last_digit < 5:
                    return value - last_digit
                else:
                    return value + (10 - last_digit)
            
            df4["Sun_Sal"] = df4["Sun_Sal"].apply(round_to_nearest_10)
            df4["In Time"] = df4["In Time"].dt.strftime('%H:%M:%S')
            df4["Out Time"] = df4["Out Time"].dt.strftime('%H:%M:%S')
            df4.index=range(1,len(df4)+1)
            
            # Display the updated dataframe
            st.write(df4)





if __name__ == "__main__":
    
    app()
