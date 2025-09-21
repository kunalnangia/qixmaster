# PowerShell script to run performance tests with proper error handling

Write-Host "Starting Performance Test Setup..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "ai-perf-tester")) {
    Write-Host "Error: ai-perf-tester directory not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Check if JMeter is available
Write-Host "Checking JMeter installation..." -ForegroundColor Yellow
$jmeterAvailable = $false
try {
    $jmeterVersion = jmeter --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "JMeter found: $jmeterVersion" -ForegroundColor Green
        $jmeterAvailable = $true
    } else {
        Write-Host "JMeter not found in PATH" -ForegroundColor Red
    }
} catch {
    Write-Host "JMeter not found in PATH" -ForegroundColor Red
}

# If JMeter is not in PATH, check JMETER_HOME
if (-not $jmeterAvailable) {
    if (Test-Path $env:JMETER_HOME) {
        $jmeterExec = Join-Path $env:JMETER_HOME "bin\jmeter.bat"
        if (Test-Path $jmeterExec) {
            Write-Host "JMeter found via JMETER_HOME: $jmeterExec" -ForegroundColor Green
            $jmeterAvailable = $true
        } else {
            Write-Host "JMeter executable not found in JMETER_HOME" -ForegroundColor Red
        }
    } else {
        Write-Host "JMETER_HOME not set or invalid" -ForegroundColor Red
    }
}

if (-not $jmeterAvailable) {
    Write-Host "Please install JMeter and ensure it's available in PATH or set JMETER_HOME" -ForegroundColor Red
    Write-Host "You can:" -ForegroundColor Yellow
    Write-Host "1. Run python setup_jmeter.py to automatically download and set up JMeter" -ForegroundColor Yellow
    Write-Host "2. Manually install JMeter and add it to PATH" -ForegroundColor Yellow
    Write-Host "3. Set JMETER_HOME environment variable" -ForegroundColor Yellow
    exit 1
}

# Start the backend
Write-Host "Starting backend server..." -ForegroundColor Yellow
Set-Location ai-perf-tester/backend
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "start.py"

Write-Host "Backend server started. Please wait a moment for it to initialize." -ForegroundColor Green
Write-Host "You can now run performance tests through the frontend." -ForegroundColor Green
Write-Host "Navigate to http://localhost:5173 in your browser." -ForegroundColor Green

# Keep the script running
Write-Host "Press Ctrl+C to stop the backend server." -ForegroundColor Yellow
try {
    Wait-Process -Id $PID -Timeout 3600
} catch {
    Write-Host "Script terminated." -ForegroundColor Yellow
}