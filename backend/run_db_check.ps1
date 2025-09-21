# PowerShell script to run the database connection checker
Write-Host "Running Database Connection Checker..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Change to the backend directory
Set-Location -Path "c:\Users\kunal\Downloads\qix-master\qix-master\backend"

# Run the database connection checker
python check_db_connection.py

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")