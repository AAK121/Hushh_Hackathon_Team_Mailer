@echo off
cd /d "C:\Users\Dell\Downloads\Pda_mailer\Pda_mailer"
set PYTHONPATH=.
echo Starting HushhMCP API Server on port 8002...
python api.py
pause
