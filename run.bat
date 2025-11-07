@echo off
rem This script is for Windows (cmd and PowerShell)
rem Command to Run: .\run.bat

ECHO Starting the application for Windows...
call www\python\venv\Scripts\activate.bat && python www\python\src\app.py