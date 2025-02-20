import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime
from streamlit_option_menu import option_menu
import pywhatkit as kit


def app():
    def send_whatsapp_messages(df, selected_date, message_template):
        """Function to send WhatsApp messages and update status."""
        for index, row in df.iterrows():
            if row["Message_Status"] == "OK":
                continue  # Skip if already messaged
    
            phone_number = "+91" + row["Phone_Number"].strip()
            if len(phone_number) == 13 and phone_number.startswith("+91"):
                personalized_message = message_template.format(
                    name=row["Name"], selected_date=selected_date
                )
                try:
                    kit.sendwhatmsg_instantly(
                        phone_no=phone_number,
                        message=personalized_message,
                        wait_time=15,
                        tab_close=True
                    )
                    st.success(f"Message sent to {row['Name']} at {phone_number}")
                    df.at[index, "Message_Status"] = "OK"  # Mark as messaged
                except Exception as e:
                    st.error(f"Failed to send message to {row['Name']}: {e}")
            else:
                st.error(f"Invalid phone number format: {phone_number}")
    
        st.success("Message status updated and saved to the database.")
    
    st.title("Attendance Management System")

    # Connect to SQLite database
    mydb = sqlite3.connect("attendance.db", check_same_thread=False)
    mycur = mydb.cursor()

    # Query to list all tables
    mycur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in mycur.fetchall()]

    # Sidebar for menu options
    with st.sidebar:
        select_fun = option_menu("Menu", ["Attendance","Update to All", "Update Absent", "Send Message","CL_Notification","NOT Eligible for incentive"])

    # Attendance view
    if select_fun == "Attendance":
        # Filter tables by month names
        table_list = [table for table in tables if table.startswith(tuple(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]))]
        
        
    
        table_name = st.selectbox("Select the table to view attendance", table_list)
        attendance_df = pd.read_sql(f"SELECT * FROM {table_name}", mydb)
        attendance_df.index = range(1, len(attendance_df) + 1)
    
        # Month name to numerical mapping
        month_name_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
            "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }
    
        # Assuming the table name format is "MonthYear", e.g., "November24"
        month_name = table_name[:-2]  # First 3 characters represent the month (e.g., 'Nov')
        year = "20" + table_name[-2:]  # Last 2 characters represent the year (e.g., '24' -> '2024')
    
        # Get the numerical month value using the month_name_map
        month = month_name_map.get(month_name, "Unknown")
        year = int(year)
    
        # Ensure that the 'DATE_OF_JOIN' column is in datetime format
        
    
        
        
        # Display the styled dataframe
        st.write(attendance_df)


       
       

   


    elif select_fun == "Update Absent":
        selected_date = st.date_input("Select the date to modify")
        current_date = selected_date.strftime("%d")
        current_month = selected_date.strftime("%m")
        current_year = selected_date.strftime("%y")

        # Map month number to month name
        month_name_map = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December"
        }
        current_month_name = month_name_map.get(current_month, "Unknown")
        create_table_name = f"{current_month_name}{current_year}"

        # Create attendance table if it doesn't exist
        if create_table_name not in tables:
            try:
                staff_df = pd.read_sql("SELECT * FROM staff_detail", mydb)
                attendance_df = staff_df[["E_Code", "Name", "BRANCH", "DEPT", "DESIGNATION"]]
                attendance_df.to_sql(create_table_name, mydb, if_exists="fail", index=False)
                st.success(f"Table '{create_table_name}' created successfully!")
            except Exception as e:
                st.error(f"Error creating table: {e}")

        # Ensure the column for the selected date exists
        mycur.execute(f"PRAGMA table_info({create_table_name})")
        column_names = [column[1] for column in mycur.fetchall()]






        
        

        # Fetch attendance data
        attendance_df = pd.read_sql(f"SELECT * FROM {create_table_name}", mydb)
        selected_name = st.selectbox("Select Name", attendance_df["Name"])
        status = st.selectbox("Select Status", ["P", "LP", "HLP", "CL", "COF", "H"])

        # Update status for all or a specific name
        
        if st.button("Update"):
            mycur.execute(f"UPDATE {create_table_name} SET \"{current_date}\" = ? WHERE Name = ?", (status, selected_name))
            mydb.commit()
            st.success(f"Updated attendance for {selected_name} to {status}.")

    # Send Message functionality
        # Send Message functionality
    elif select_fun == "Send Message":
        selected_date = st.date_input("Select the date to check")
        current_date = selected_date.strftime("%d")
        current_month = selected_date.strftime("%m")
        current_year = selected_date.strftime("%y")
    
        month_name_map = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December"
        }
        current_month_name = month_name_map.get(current_month, "Unknown")
        create_table_name = f"{current_month_name}{current_year}"
    
        if create_table_name in tables:
            df_attendance = pd.read_sql(f"SELECT * FROM {create_table_name}", mydb)
            df_staff = pd.read_sql("SELECT * FROM staff_detail", mydb)[["E_Code", "Phone_Number"]]
            df_staff["Phone_Number"] = df_staff["Phone_Number"].astype(str)
    
            for status, msg_template in [("LP", "Hello {name}, your absence for {selected_date} has been noted."),
                                         ("CL", "Hello {name}, your absence for {selected_date} has been noted."),
                                         ("HLP", "Hello {name}, your Half day absence for {selected_date} has been noted.")]:
                
                if current_date in df_attendance.columns:
                    df_filtered = df_attendance[df_attendance[current_date].isin([status])]
                    df_filtered = df_filtered[["E_Code", "Name", "BRANCH", "DEPT", "DESIGNATION", current_date]]
                    
                    df_merged = pd.merge(df_filtered, df_staff, how="inner", on="E_Code")
                    df_merged.index = range(1, len(df_merged) + 1)
    
                    if "Message_Status" not in df_merged.columns:
                        df_merged["Message_Status"] = "Pending"
    
                    st.write(df_merged)
    
                    if st.button(f"Send {status} Messages"):
                        send_whatsapp_messages(df_merged, selected_date, msg_template)
    
                else:
                    st.warning(f"Date '{current_date}' not found in table '{create_table_name}'.")
    
        else:
            st.error(f"Attendance table '{create_table_name}' does not exist.")



 # Update absent functionality
    if select_fun =="Update to All":    
        selected_date = st.date_input("Select the date to modify")
        current_date = selected_date.strftime("%d")
        current_month = selected_date.strftime("%m")
        current_year = selected_date.strftime("%y")

        # Map month number to month name
        month_name_map = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December"
        }
        current_month_name = month_name_map.get(current_month, "Unknown")
        create_table_name = f"{current_month_name}{current_year}"

        # Create attendance table if it doesn't exist
        if create_table_name not in tables:
            try:
                staff_df = pd.read_sql("SELECT * FROM staff_detail", mydb)
                attendance_df = staff_df[["E_Code", "Name", "BRANCH", "DEPT", "DESIGNATION"]]
                attendance_df.to_sql(create_table_name, mydb, if_exists="fail", index=False)
                st.success(f"Table '{create_table_name}' created successfully!")
            except Exception as e:
                st.error(f"Error creating table: {e}")

        # Ensure the column for the selected date exists
        mycur.execute(f"PRAGMA table_info({create_table_name})")
        column_names = [column[1] for column in mycur.fetchall()]
        

        # Fetch attendance data
        attendance_df = pd.read_sql(f"SELECT * FROM {create_table_name}", mydb)
        #selected_name = st.selectbox("Select Name", attendance_df["Name"])
        status = st.selectbox("Select Status", ["P", "LP", "HLP", "CL", "COF", "H"])

        # Update status for all or a specific name
        if st.checkbox("Select All"):
            if st.button("Update All"):
                if current_date not in column_names:
                    mycur.execute(f"ALTER TABLE {create_table_name} ADD COLUMN \"{current_date}\" TEXT DEFAULT ''")
                for name in attendance_df["Name"]:
                    mycur.execute(f"UPDATE {create_table_name} SET \"{current_date}\" = ? WHERE Name = ?", (status, name))
                mydb.commit()
                st.success("Updated attendance for all names successfully!")

    if select_fun == "CL_Notification":
        # Filter tables that start with month names
        table_list = [table for table in tables if table.startswith(tuple(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]))]
        
        if not table_list:
            st.warning("No attendance tables found.")
            return
    
        # User selects the table
        table_name = st.selectbox("Select the table to view attendance", table_list)
        
        # Read attendance data
        attendance_df = pd.read_sql(f"SELECT * FROM {table_name}", mydb)
        attendance_df.index = range(1, len(attendance_df) + 1)
        
        # Extract attendance columns
        attendance_columns = attendance_df.columns[5:]  # Columns starting from the 6th one are attendance days
        days = len(attendance_columns)
        
        # Add calculated columns for attendance counts
        attendance_df["P"] = attendance_df[attendance_columns].apply(lambda row: (row == 'P').sum(), axis=1)
        attendance_df["LP"] = attendance_df[attendance_columns].apply(lambda row: (row == 'LP').sum(), axis=1)
        attendance_df["HLP"] = attendance_df[attendance_columns].apply(lambda row: (row == 'HLP').sum(), axis=1)
        attendance_df["CL"] = attendance_df[attendance_columns].apply(lambda row: (row == 'CL').sum(), axis=1)
        attendance_df["COF"] = attendance_df[attendance_columns].apply(lambda row: (row == 'COF').sum(), axis=1)
        attendance_df["LOP"] = attendance_df["LP"] + (attendance_df["HLP"]/2)
    
        # Filter rows based on conditions
        out_df = attendance_df[((attendance_df["LP"]>0) | (attendance_df["HLP"]>0)) & (attendance_df["CL"]==0)]        
        # Display the filtered DataFrame
        if out_df.empty:
            st.info("No matching records found for the specified conditions.")
        else:
            st.write(out_df)
    if select_fun == "NOT Eligible for incentive":
        # Filter tables that start with month names
        table_list = [table for table in tables if table.startswith(tuple(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]))]
        
        if not table_list:
            st.warning("No attendance tables found.")
            return
    
        # User selects the table
        table_name = st.selectbox("Select the table to view attendance", table_list)
        
        # Read attendance data
        attendance_df = pd.read_sql(f"SELECT * FROM {table_name}", mydb)
        attendance_df.index = range(1, len(attendance_df) + 1)
        
        # Extract attendance columns
        attendance_columns = attendance_df.columns[5:]  # Columns starting from the 6th one are attendance days
        days = len(attendance_columns)
        
        # Add calculated columns for attendance counts
        attendance_df["P"] = attendance_df[attendance_columns].apply(lambda row: (row == 'P').sum(), axis=1)
        attendance_df["LP"] = attendance_df[attendance_columns].apply(lambda row: (row == 'LP').sum(), axis=1)
        attendance_df["HLP"] = attendance_df[attendance_columns].apply(lambda row: (row == 'HLP').sum(), axis=1)
        attendance_df["CL"] = attendance_df[attendance_columns].apply(lambda row: (row == 'CL').sum(), axis=1)
        attendance_df["COF"] = attendance_df[attendance_columns].apply(lambda row: (row == 'COF').sum(), axis=1)
        attendance_df["LOP"] = attendance_df["LP"] + (attendance_df["HLP"]/2)
    
        # Filter rows based on conditions
        out_df = attendance_df[(attendance_df["LOP"]>=2)]        
        # Display the filtered DataFrame
        if out_df.empty:
            st.info("No matching records found for the specified conditions.")
        else:
            st.write(out_df)

        
        
        

    mydb.close()
# Run the app
if __name__ == "__main__":
    app()