@echo off
echo Starting Backend Server on Port 8001...
cd /d "c:\Users\kunal\Downloads\qix-master\qix-master\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug
pause