@echo off
title GitHub Repository Setup & Push
echo ===================================================================
echo AI-Driven CI/CD Pipeline Optimization - GitHub Remote Integration
echo Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore
echo ===================================================================
echo.
echo Step 1: Create a new repository on https://github.com/new
echo         Name it: AI-Driven-CICD-Pipeline-Optimization (or any name you prefer)
echo         Do NOT initialize it with README, license, or .gitignore (we already have them!)
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/your-username/repo.git): "

if "%REPO_URL%"=="" (
    echo [!] No URL provided. Aborting.
    pause
    exit /b 1
)

echo.
echo [*] Configuring Git remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [*] Renaming default branch to main...
git branch -M main

echo [*] Pushing repository and history to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================================
    echo [SUCCESS] Repository successfully pushed to GitHub!
    echo Visit your repository on GitHub to see the workflows running!
    echo ===================================================================
) else (
    echo.
    echo [!] Push failed. Please verify your GitHub credentials, URL, and personal access token.
)
pause
