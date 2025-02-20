import pandas as pd
import streamlit as st
from fpdf import FPDF
import io
import base64
import os
from num2words import num2words
from decimal import Decimal

from decimal import Decimal
from num2words import num2words

def amount_in_words(amount):
    # Ensure the amount is converted to a Python int first, then to Decimal
    amount = Decimal(int(amount))  # Convert numpy.int64 to int, then to Decimal
    # Convert the amount into words with formatting for Indian Rupees
    return num2words(amount, lang='en', to='currency').replace("euro", "rupees").replace("cents", "paise")


def generate_payslip_pdf(df, name, file_name):
    # Employee-specific details
    employee_data = df[df["Name"] == name].iloc[0]
    name = employee_data["Name"]
    emp_code = employee_data["E_Code"]
    date_of_joining = employee_data["DATE_OF_JOIN"]
    bank_name = employee_data["Bank_Name"]
    des = employee_data["DESIGNATION"]
    dep = employee_data["DEPT"]
    branch = employee_data["BRANCH"]
    acc_no = employee_data["Acc_no"]
    no_of_days = employee_data["No_of_days"]
    total_salary = employee_data["Net_Salary"]
    basic_salary = employee_data["BASIC"]
    act = employee_data["ACTUAL_GROSS"]
    hra = employee_data["HRA"]
    da = employee_data["DA"]
    pf_amt = employee_data["PF AMT"]
    esi_amt = employee_data["ESI AMT"]
    lop = employee_data["No_of_days"] - employee_data["Paid_days"]
    eff=employee_data["Paid_days"]
    det = employee_data["Deduction"]

    class PDF(FPDF):
        def header(self):
            logo_path = r"C:\Users\HRD\jeevan\images.png"  # Update the path to your logo file
            self.image(logo_path, 10, 8, 33)  # Position and size of the logo (x, y, width)
            self.set_font('Arial', 'B', 18)
            self.cell(0, 10, 'Jeevan Auto Moto Pvt Ltd', ln=True, align='C')
            self.set_font('Arial', 'B', 12)
            self.cell(0, 5, '144/1, Tirupparankunram Rd,', ln=True, align='C')
            self.cell(0, 5, ' Palangantham,Madurai - 625003.', ln=True, align='C')
            self.cell(0, 5, '', ln=True, align='C')
            self.set_font('Arial', 'B', 16)
            self.cell(0, 20, f"Payslip For the Month of {file_name}", align="C")
            self.ln(20)

        def footer(self):
            self.set_y(-40)
            self.set_font('Arial', 'I', 10)
            self.cell(0, 5, 'This is a system-generated payslip and does not require a signature.', ln=True, align='C')

    # Create the PDF
    pdf = PDF()
    pdf.add_page()

    # Add employee details
    pdf.set_font('Arial', '', 12)  # Reduced font size to 10

    label_width = 38
    colon_width = 7
    value_width = 65

    pdf.cell(label_width, 8, "Name", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(value_width, 8, f"{name}", align='L')
    pdf.cell(label_width, 8, "Roll No", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(0, 8, f"{emp_code}", align='L')
    pdf.ln(8)

    pdf.cell(label_width, 8, "Date of Joining", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(value_width, 8, f"{date_of_joining}", align='L')
    pdf.cell(label_width, 8, "Bank Name", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(0, 8, f"{bank_name}", align='L')
    pdf.ln(8)

    pdf.cell(label_width, 8, "Designation", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(value_width, 8, f"{des}", align='L')
    pdf.cell(label_width, 8, "Bank Account No", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(0, 8, f"{acc_no}", align='L')
    pdf.ln(8)

    pdf.cell(label_width, 8, "Department", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(value_width, 8, f"{dep}", align='L')
    pdf.cell(label_width, 8, "Effective Work Days", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(0, 8, f"{eff}", align='L')
    pdf.ln(8)

    pdf.cell(label_width, 8, "Location", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(value_width, 8, f"{branch}", align='L')
    pdf.cell(label_width, 8, "LOP", align='L')
    pdf.cell(colon_width, 8, ":", align='C')
    pdf.cell(0, 8, f"{lop}", align='L')
    pdf.ln(8)
    pdf.cell(0, 30, f"", ln=True, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(38, 10, "Earnings ", border=1, align='C')
    pdf.cell(38, 10, "(Full)", border=1, align='C')
    pdf.cell(38, 10, "(Actual)", border=1, align='C')
    pdf.cell(38, 10, "Deductions", border=1, align='C')
    pdf.cell(38, 10, "Actual", border=1, ln=True, align='C')

    pdf.set_font('Arial', '', 12)

    pdf.cell(38, 10, "Basic Salary", border=1, align='C')
    pdf.cell(38, 10, f"{(act * 0.60):.2f}", border=1, align='C')
    pdf.cell(38, 10, f"{basic_salary:.2f}", border=1, align='C')
    pdf.cell(38, 10, "PF Amount", border=1, align='C')
    pdf.cell(38, 10, f"{pf_amt:.2f}", border=1, ln=True, align='C')

    pdf.cell(38, 10, "HRA", border=1, align='C')
    pdf.cell(38, 10, f"{(act * 0.50):.2f}", border=1, align='C')
    pdf.cell(38, 10, f"{hra:.2f}", border=1, align='C')
    pdf.cell(38, 10, "ESI Amount", border=1, align='C')
    pdf.cell(38, 10, f"{esi_amt:.2f}", border=1, ln=True, align='C')

    pdf.cell(38, 10, "DA", border=1, align='C')
    pdf.cell(38, 10, f"{(act * 0.10):.2f}", border=1, align='C')
    pdf.cell(38, 10, f"{da:.2f}", border=1, align='C')
    pdf.cell(38, 10, "Loan Amount", border=1, align='C')
    pdf.cell(38, 10, f"{det:.2f}", border=1, ln=True, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(38, 10, "Total Earnings", border=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(38, 10, f"{act:.2f}", border=1, align='C')
    pdf.cell(38, 10, f"{basic_salary + da + hra:.2f}", border=1, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(38, 10, "Total Deduction", border=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(38, 10, f"{pf_amt + esi_amt + det:.2f}", border=1, ln=True, align='C')

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(140, 10, "Net Salary", border=1, align='C')
    pdf.cell(50, 10, f"{total_salary:.2f}", border=1, align='C')
    pdf.ln(10)
    list_S = amount_in_words(total_salary).upper()
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 30, f"Net pay for the month is {total_salary}({list_S[:-12]}.)", ln=True, align='C')

    buffer = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    buffer.write(pdf_output)
    buffer.seek(0)
    return buffer

def pdf_to_base64(pdf_buffer):
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    return pdf_base64

def app():
    st.title("Payslip Generator")

    directory_path = r"E:\\share\\salary report"

    files = os.listdir(directory_path)

    list_name = [file.removesuffix(".csv") for file in files if file.endswith('.csv')]
    file_name = st.selectbox("Select the month to create Payslip", list_name)

    df = pd.read_csv(f"{directory_path}\\{file_name}.csv")

    name = st.selectbox("Select the name to create payslip", df["Name"])
    df2 = df[df["Name"] == name]
    st.write(df2)

    if st.button("Generate Payslip"):
        pdf_buffer = generate_payslip_pdf(df2, name, file_name)
        pdf_base64 = pdf_to_base64(pdf_buffer)

        st.download_button(
            label="Download Payslip PDF",
            data=pdf_buffer,
            file_name=f"{name}_payslip_{file_name}.pdf",
            mime="application/pdf"
        )

        pdf_data_uri = f"data:application/pdf;base64,{pdf_base64}"
        st.markdown(f'<iframe src="{pdf_data_uri}" width="700" height="500"></iframe>', unsafe_allow_html=True)

if __name__ == "__main__":
    app()
