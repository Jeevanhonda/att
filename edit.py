import pandas as pd
import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu

def app():
    st.title("Alter Existing Staff Detail")
    # Create a new SQLite connection for the current thread
    mydb = sqlite3.connect("attendance.db")
    mycursor = mydb.cursor()

    with st.sidebar:
        select_fun = option_menu("Menu", ["Edit Over All Detail"])

    # Menu Option
    if select_fun == "Edit Over All Detail":
        # Read staff details from the database
        df = pd.read_sql("SELECT * FROM staff_detail", mydb)

        # Initialize session state for selected name
        if "selected_name" not in st.session_state:
            st.session_state.selected_name = df["Name"].iloc[0]  # Default to the first name

        # Select Name from dropdown
        name = st.selectbox("Select the Name", df["Name"].unique(), 
                            index=list(df["Name"].unique()).index(st.session_state.selected_name))

        # Update session state when a new name is selected
        if name != st.session_state.selected_name:
            st.session_state.selected_name = name

        # Filter DataFrame for the selected Name
        df1 = df[df["Name"] == st.session_state.selected_name].reset_index(drop=True)

        if not df1.empty:  # Ensure the DataFrame is not empty
            # Extract EMP_CODE for the selected Name
            emp_code = df1["E_Code"].iloc[0]
            
            with st.form("update_form"):
                # Edit the Name (make the text input for the Name field editable)
                new_name = st.text_input("Edit Name", df1["Name"].iloc[0])
                
                # Extract other details for the selected record
                branch = st.text_input("Enter The Branch", df1["BRANCH"].iloc[0])
                dept = st.text_input("Enter The Department", df1["DEPT"].iloc[0])
                designation = st.text_input("Enter The Designation", df1["DESIGNATION"].iloc[0])
                
                salary = (
                    float(df1["ACTUAL_GROSS"].iloc[0]) 
                    if not pd.isnull(df1["ACTUAL_GROSS"].iloc[0]) 
                    else 0.0
                )
                salary = st.number_input("Enter The Salary", value=salary, step=0.01)
                
                acc = (
                    (df1["Acc_no"].iloc[0]) 
                    if not pd.isnull(df1["Acc_no"].iloc[0]) 
                    else 0
                )
                acc = st.text_input("Enter The Account Number", value=acc)
                
                ifsc = st.text_input("Enter The IFSC Code", df1["Ifsc_code"].iloc[0])
                bank_name = st.text_input("Enter The Bank Name", df1["Bank_Name"].iloc[0])
                
                date_of_join = (
                    pd.to_datetime(df1["DATE_OF_JOIN"].iloc[0]).date() 
                    if pd.notnull(df1["DATE_OF_JOIN"].iloc[0]) 
                    else None
                )
                date_of_join = st.date_input("Enter The Date of Join", date_of_join)
                
                esi_st = st.text_input("Enter The ESI Status", df1["ESI"].iloc[0] if not pd.isnull(df1["ESI"].iloc[0]) else "")
                
                phone = (
                    int(df1["Phone_Number"].iloc[0]) 
                    if not pd.isnull(df1["Phone_Number"].iloc[0]) 
                    else 0
                )
                phone = st.number_input("Enter The Phone Number", min_value=0, max_value=99999999999, value=phone, step=1)
                
                # Submit button
                submitted = st.form_submit_button("Update Staff Details")
                
                if submitted:
                    # Prepare the SQL query and values for updating
                    query = """UPDATE staff_detail SET 
                                Name = ?, BRANCH = ?, DEPT = ?, DESIGNATION = ?, ACTUAL_GROSS = ?, ESI = ?, 
                                Acc_no = ?, Ifsc_code = ?, Bank_Name = ?, DATE_OF_JOIN = ?, Phone_Number = ?
                                WHERE E_Code = ?"""
                    values = (
                        new_name, branch, dept, designation, salary, esi_st, 
                        acc, ifsc, bank_name, date_of_join, phone, emp_code
                    )

                    try:
                        # Execute the query with the updated values
                        mycursor.execute(query, values)
                        mydb.commit()  # Commit the changes to the database
                        st.success(f"Successfully updated the staff details for {new_name}")
                        # Update session state to the new name
                        st.session_state.selected_name = new_name
                    except Exception as e:
                        st.error(f"Error updating data: {str(e)}")
        else:
            st.error("No details found for the selected Name.")
        
        # Display updated table
        df5 = pd.read_sql("SELECT * FROM staff_detail", mydb)
        df5.index = range(1, len(df5) + 1)
        st.write(df5)

if __name__ == "__main__":
    app()
