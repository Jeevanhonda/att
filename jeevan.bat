@echo off
cd /d "C:\Users\HRD\jeevan"

:: Activate the Anaconda base environment
call "C:\Users\HRD\us\anaconda3\Scripts\activate.bat"
call conda activate base  || conda activate your_env_name



:: Run Streamlit app
streamlit run amutham.py


