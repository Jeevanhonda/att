import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

def app():
    mydb = sqlite3.connect("attendance.db", check_same_thread=False)
    mycur = mydb.cursor()
    df=pd.read_sql("select * from staff_detail",mydb)
    df["Acc_no"] = "'" + df["Acc_no"].astype(str)
    

    st.write(df)