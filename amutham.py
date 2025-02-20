import streamlit as st
from streamlit_option_menu import option_menu
import insert, edit, delete,attendance,salary,deduction,payslip,stock_report,staff_detail,backup  # Ensure these modules are correctly defined
st.set_page_config(
    page_title="Jeevan",  # App name
    page_icon="images.png",    # You can use an emoji or a custom logo
    layout="wide"         # Optional: 'centered' or 'wide'
)
class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({"title": title, "function": function})

    def run(self):
        # Sidebar with navigation menu
        with st.sidebar:        
            app = option_menu(
                menu_title='Main Menu',  # Title of the sidebar menu
                options=["Add New Staff", "Edit Existing", "Delete Staff","Attendance","Salary Calculation","Deduction","Payslip","Stock Report","Staff Detail","Back Up"],  # Menu items
                icons=["person-add", 'pencil-square',"person-dash","building-fill-add","cash","sort-down","receipt-cutoff","box-seam","people"],  # Icons for menu items (ensure these paths are correct)
                menu_icon='chat-text-fill',  # Icon for the menu
                default_index=0,  # Default selected menu item
                styles={  # Custom styling
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"}, 
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        if app == "Add New Staff":
            insert.app()  # Ensure insert.app() exists
        elif app == "Edit Existing":
            edit.app()  # Ensure edit.app() exists
        elif app == "Delete Staff":
            delete.app()  # Ensure delete.app() exists
        elif app=="Attendance":
            attendance.app()
        elif app=="Salary Calculation":
            salary.app()
        elif app =="Deduction":
            deduction.app()
        elif app =="Payslip":
            payslip.app()
        elif app=="Stock Report":
            stock_report.app()
        elif app=="Staff Detail":
            staff_detail.app()
        elif app=="Back Up":
            backup.app()
        




# Running the multi-app structure
if __name__ == "__main__":
    app = MultiApp()  # Create instance of MultiApp
    app.run()  # Run the app
