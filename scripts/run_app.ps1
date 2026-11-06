# PowerShell Launcher: Start FastAPI Application & Open Browser
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "Launching AI-Driven CI/CD Optimization Server & Dashboard..." -ForegroundColor Cyan
Write-Host "Candidate: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan

Start-Process "http://127.0.0.1:8000"
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
