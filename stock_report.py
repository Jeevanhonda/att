import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import chardet

def app():
    # Sidebar menu
    with st.sidebar:
        select_fun = option_menu("Menu", ["Stock Report Quarter Wise","Current Stock","Transit"])

    st.title("Stock Report")
    st.title("Quarterly Wise")

    # Use session state to manage file upload
    if select_fun == "Stock Report Quarter Wise":
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], key="file_uploader")

        # Button to trigger calculation
        if st.button("Calculate"):
            if uploaded_file is not None:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)

                # Check for required columns
                required_columns = ["Model Name", "Model Variant", "Manufacturing Date"]
                if not all(col in df.columns for col in required_columns):
                    st.error(f"File must contain these columns: {required_columns}")
                    return
                
                # Extract necessary columns
                df2 = df[required_columns]

                # Convert 'Manufacturing Date' to datetime
                df2['Manufacturing Date'] = pd.to_datetime(df2['Manufacturing Date'], errors='coerce')

                # Drop rows with invalid dates
                df2 = df2.dropna(subset=['Manufacturing Date'])

                # Get the min and max manufacturing dates
                max_date = df2['Manufacturing Date'].max()
                min_date = df2['Manufacturing Date'].min()

                # List to store years
                years = list(range(min_date.year, max_date.year + 1))

                # Create a DataFrame with unique Model Names
                df3 = pd.DataFrame(df2["Model Name"].unique(), columns=["Model Name"])

                # Add Quarter columns dynamically
                for year in years:
                    for quarter in range(1, 5):
                        # Define start and end dates for each quarter
                        start_month = (quarter - 1) * 3 + 1
                        end_month = quarter * 3
                        start_date = pd.Timestamp(f"{year}-{start_month:02d}-01")
                        end_date = pd.Timestamp(f"{year}-{end_month:02d}-{pd.Timestamp(year=year, month=end_month, day=1).days_in_month}")

                        # Create a column for each quarter
                        quarter_col = f"{year}_Quarter{quarter}"
                        df3[quarter_col] = df3["Model Name"].apply(
                            lambda model: df2[
                                (df2["Manufacturing Date"].between(start_date, end_date)) & 
                                (df2["Model Name"] == model)
                            ].shape[0]
                        )

                # Add a "Total" column
                df3["Total"] = df3.iloc[:, 1:].sum(axis=1)

                # Create total row and add it to the DataFrame
                total_row = df3.iloc[:, 1:].sum()  # Sum for all columns except "Model Name"
                total_row["Model Name"] = "Total"  # Add "Model Name" for the total row
                df3 = pd.concat([df3, pd.DataFrame([total_row])], ignore_index=True)

                # Remove columns where the total row is zero
                df_cleaned = df3.loc[:, (df3.iloc[-1] != 0) | (df3.columns == "Model Name")]

                # Reset the index to start at 1
                df_cleaned.index = range(1, len(df_cleaned) + 1)

                # Store cleaned DataFrame in session state
                st.session_state['cleaned_df'] = df_cleaned
                st.session_state['original_df'] = df

                # Display the cleaned DataFrame
                st.write(df_cleaned)

        # Check if cleaned DataFrame is in session state
        if 'cleaned_df' in st.session_state:
            df_cleaned = st.session_state['cleaned_df']
            col_lis = list(df_cleaned.columns)
            lis = [i for i in col_lis if i.startswith("20")]

            # Dropdown to select a quarter
            option = st.select_slider("Choose a quarter", options=lis, key="quarter_selector")

            # Define start and end dates based on the selected quarter
            if "Quarter1" in option:
                start_date = f"{option[:4]}-01-01"
                end_date = f"{option[:4]}-03-31"
            elif "Quarter2" in option:
                start_date = f"{option[:4]}-04-01"
                end_date = f"{option[:4]}-06-30"
            elif "Quarter3" in option:
                start_date = f"{option[:4]}-07-01"
                end_date = f"{option[:4]}-09-30"
            elif "Quarter4" in option:
                start_date = f"{option[:4]}-10-01"
                end_date = f"{option[:4]}-12-31"

            # Filter the original DataFrame for the selected quarter
            df = st.session_state['original_df']
            df["Manufacturing Date"] = pd.to_datetime(df["Manufacturing Date"], errors='coerce')
            df_filtered = df[
                df["Manufacturing Date"].between(start_date, end_date)
            ][["Model Name", "Model Variant","Color","Network Name", "Frame Number","Engine Number","Manufacturing Date","Dispatch Date","Number Of Vehicles"]]
            df_filtered.index=range(1,len(df_filtered)+1)
            # Display the filtered DataFrame
            st.dataframe(df_filtered)


    if "select_fun" in locals() and select_fun == "Transit":
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], key="file_uploader")
    
        if st.button("Calculate"):
            if uploaded_file is not None:
                try:
                    # Detect file encoding
                    rawdata = uploaded_file.getvalue()
                    result = chardet.detect(rawdata)
                    encoding = result["encoding"]
    
                    # Reset file pointer
                    uploaded_file.seek(0)
    
                    # Read CSV with auto delimiter detection
                    df = pd.read_csv(uploaded_file, encoding=encoding, engine="python")
    
                    # Ensure required columns exist
                    required_cols = {"Model Name", "Model Variant", "Color"}
                    if not required_cols.issubset(df.columns):
                        st.error(f"Missing columns! Expected columns: {required_cols}, but got {df.columns}")
                        st.stop()
    
                    # Selecting required columns
                    df = df[list(required_cols)]  # Keep only necessary columns
    
                    # Create Pivot Table (count occurrences)
                    pivot_df = df.pivot_table(index=["Model Name", "Model Variant"], columns="Color", aggfunc="size", fill_value=0)


    
                    # Display Pivot Table
                    st.write("### Model Count Table")
                    st.write(pivot_df)
    
                    # Display Original DataFrame
                    st.write("### Uploaded Data")
                    st.dataframe(df)
    
                except Exception as e:
                    st.error(f"Error reading file: {e}")

            



        
        
if __name__ == "__main__":
    app()
