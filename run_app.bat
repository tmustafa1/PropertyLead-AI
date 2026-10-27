@echo off
title PropertyLead AI - Real Estate CRM
echo ========================================================
echo   Launching PropertyLead AI...
echo   SQLite + Streamlit + AI Rule-Based Scoring Engine
echo ========================================================
echo.

IF EXIST "C:\Users\Admin\anaconda3\python.exe" (
    echo Using Anaconda Python environment...
    "C:\Users\Admin\anaconda3\python.exe" -m streamlit run app.py
) ELSE (
    echo Using system Python...
    python -m streamlit run app.py
)

pause
