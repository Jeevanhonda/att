import os
import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Set the directory where photos will be saved
SAVE_DIRECTORY = "E:/StaffPhotos"  # Change this to your desired folder path

# Ensure the directory exists
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

# CSV file to log saved photos
LOG_FILE = os.path.join(SAVE_DIRECTORY, "photo_log.csv")

# Initialize the log file if it doesn't exist
if not os.path.exists(LOG_FILE):
    df = pd.DataFrame(columns=["Staff Name", "File Name", "Upload Time"])
    df.to_csv(LOG_FILE, index=False)

# Streamlit App
st.title("Staff Aadhar Upload Portal")

# File uploader widget
uploaded_file = st.file_uploader("Upload a photo", type=["png", "jpg", "jpeg"])

# Staff name input
staff_name = st.text_input("Enter Staff Name")

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Photo Preview", use_column_width=True)

# Upload button
if st.button("Save Aadhar"):
    if uploaded_file is not None and staff_name:
        # Validate staff name
        if not re.match(r"^[a-zA-Z0-9_ ]+$", staff_name):
            st.error("Staff name contains invalid characters! Use only letters, numbers, spaces, or underscores.")
        else:
            # Generate a unique file name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(uploaded_file.name)[1]
            file_name = f"{staff_name}_aadhar_{timestamp}{file_extension}"
            save_path = os.path.join(SAVE_DIRECTORY, file_name)

            # Save the uploaded photo
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Log the details into the CSV file
            df = pd.read_csv(LOG_FILE)
            new_entry = {"Staff Name": staff_name, "File Name": file_name, "Upload Time": timestamp}
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(LOG_FILE, index=False)

            st.success(f"Aadhar photo for {staff_name} saved successfully as {file_name} in {SAVE_DIRECTORY}")
    else:
        st.error("Please upload a photo and enter the staff name.")

# Download log file option
if os.path.exists(LOG_FILE):
    st.download_button(
        label="Download Log File",
        data=open(LOG_FILE, "rb"),
        file_name="photo_log.csv",
        mime="text/csv",
    )
