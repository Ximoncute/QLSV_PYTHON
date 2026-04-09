@echo off
echo Starting Modern UniMS (FastAPI + Modular Tkinter)...

:: Initialize DB (Drops and recreates with fresh seeds)
echo Initializing fresh database...
python backend1/init_db.py

:: Start Backend in background
start /b python backend1/run.py

echo Waiting for API to start...
timeout /t 5

:: Start Frontend
python frontend/main.py

echo App session finished.
pause
