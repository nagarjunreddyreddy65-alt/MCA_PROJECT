# PowerShell Script to Connect and Push to GitHub Remote
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "AI-Driven CI/CD Pipeline Optimization - GitHub Remote Integration" -ForegroundColor Cyan
Write-Host "Student: NAGARJUNREDDY (1DS25MC052), DSCE Bangalore" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan

Write-Host "`nInstructions:" -ForegroundColor Yellow
Write-Host "1. Create a new empty repository on https://github.com/new"
Write-Host "   (Leave README, .gitignore, and license UNCHECKED)"
Write-Host "2. Copy your repository HTTPS URL (e.g. https://github.com/USERNAME/REPO_NAME.git)`n"

$repoUrl = Read-Host "Enter your GitHub Repository URL"

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Host "[!] No URL provided. Aborting." -ForegroundColor Red
    exit 1
}

Write-Host "`n[*] Configuring Git remote origin..." -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin $repoUrl.Trim()

Write-Host "[*] Ensuring main branch..." -ForegroundColor Cyan
git branch -M main

Write-Host "[*] Pushing repository to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n===================================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Repository successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Check the 'Actions' tab on GitHub to see the baseline & AI workflows!" -ForegroundColor Green
    Write-Host "===================================================================" -ForegroundColor Green
} else {
    Write-Host "`n[!] Push encountered an issue. Ensure your credentials or Personal Access Token (PAT) are configured." -ForegroundColor Red
}
