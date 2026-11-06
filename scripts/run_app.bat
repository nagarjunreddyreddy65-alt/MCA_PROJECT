@echo off
title AI-Driven CI/CD Optimization - FastAPI & Dashboard
echo ===================================================================
echo Starting AI-Driven CI/CD Optimization API and Web Dashboard...
echo Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
echo ===================================================================
start "" http://127.0.0.1:8000
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
pause
