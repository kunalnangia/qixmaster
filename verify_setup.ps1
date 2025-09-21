# PowerShell script to verify Java and JMeter setup

Write-Host "Verifying Java and JMeter Setup..." -ForegroundColor Green
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param ([string]$command)
    try {
        $null = Get-Command $command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Check if we're in the right directory
if (-not (Test-Path "apache-jmeter-5.6.3")) {
    Write-Host "Warning: JMeter directory not found in current location." -ForegroundColor Yellow
}

# Check Java installation
Write-Host "Checking Java installation..." -ForegroundColor Yellow
$javaAvailable = $false
try {
    $javaVersion = java -version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Java found:" -ForegroundColor Green
        $javaVersion | ForEach-Object { Write-Host "  $_" }
        $javaAvailable = $true
    } else {
        Write-Host "Java not found in PATH" -ForegroundColor Red
    }
} catch {
    Write-Host "Java not found in PATH" -ForegroundColor Red
}

# Check JAVA_HOME environment variable
$javaHome = $env:JAVA_HOME
if ($javaHome) {
    Write-Host "JAVA_HOME is set to: $javaHome" -ForegroundColor Green
    if (Test-Path $javaHome) {
        Write-Host "  JAVA_HOME directory exists" -ForegroundColor Green
    } else {
        Write-Host "  Warning: JAVA_HOME directory does not exist" -ForegroundColor Yellow
    }
} else {
    Write-Host "JAVA_HOME is not set" -ForegroundColor Yellow
}

# Check JMeter installation
Write-Host ""
Write-Host "Checking JMeter installation..." -ForegroundColor Yellow
$jmeterAvailable = $false

# Try jmeter command
try {
    $jmeterVersion = jmeter --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "JMeter found in PATH:" -ForegroundColor Green
        Write-Host "  $jmeterVersion" -ForegroundColor Green
        $jmeterAvailable = $true
    } else {
        Write-Host "JMeter not found in PATH" -ForegroundColor Yellow
    }
} catch {
    Write-Host "JMeter not found in PATH" -ForegroundColor Yellow
}

# Try JMETER_HOME
if (-not $jmeterAvailable) {
    $jmeterHome = $env:JMETER_HOME
    if ($jmeterHome) {
        Write-Host "JMETER_HOME is set to: $jmeterHome" -ForegroundColor Green
        $jmeterExec = Join-Path $jmeterHome "bin\jmeter.bat"
        if (Test-Path $jmeterExec) {
            Write-Host "  JMeter executable found at: $jmeterExec" -ForegroundColor Green
            # Try running JMeter with full path
            try {
                $jmeterVersion = & $jmeterExec --version 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  JMeter runs successfully:" -ForegroundColor Green
                    Write-Host "    $jmeterVersion" -ForegroundColor Green
                    $jmeterAvailable = $true
                } else {
                    Write-Host "  JMeter failed to run" -ForegroundColor Red
                }
            } catch {
                Write-Host "  JMeter failed to run: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  JMeter executable not found at: $jmeterExec" -ForegroundColor Red
        }
    } else {
        Write-Host "JMETER_HOME is not set" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
if ($javaAvailable) {
    Write-Host "  ✓ Java is properly installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Java is not installed or not in PATH" -ForegroundColor Red
    Write-Host "    Please install Java from https://adoptium.net/" -ForegroundColor Yellow
}

if ($jmeterAvailable) {
    Write-Host "  ✓ JMeter is properly configured" -ForegroundColor Green
} else {
    Write-Host "  ✗ JMeter is not properly configured" -ForegroundColor Red
    Write-Host "    Please ensure JMeter is installed and either:" -ForegroundColor Yellow
    Write-Host "    1. Added to PATH, or" -ForegroundColor Yellow
    Write-Host "    2. JMETER_HOME is set correctly" -ForegroundColor Yellow
}

Write-Host ""
if ($javaAvailable -and $jmeterAvailable) {
    Write-Host "Setup is complete! You can now run performance tests." -ForegroundColor Green
} else {
    Write-Host "Setup is incomplete. Please follow the instructions above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Quick setup options:" -ForegroundColor Cyan
    Write-Host "1. Run download_jmeter.ps1 to automatically download JMeter" -ForegroundColor Yellow
    Write-Host "2. Run complete_setup.bat to set all environment variables" -ForegroundColor Yellow
    Write-Host "3. Manually add Java and JMeter to your system PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")