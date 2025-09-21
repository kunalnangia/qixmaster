# start-jmeter.ps1
# PowerShell script to start JMeter server properly

# Define the JMeter installation directory
$jmeterDir = "C:\Users\kunal\Downloads\qix-master\qix-master\apache-jmeter-5.6.3"

# Check if JMeter directory exists
if (-not (Test-Path $jmeterDir)) {
    Write-Host "Error: JMeter directory not found at $jmeterDir"
    Write-Host "Please make sure JMeter is installed at the correct location."
    exit 1
}

# Change to the JMeter bin directory
Set-Location "$jmeterDir\bin"

# Check if jmeter-server.bat exists
if (-not (Test-Path "jmeter-server.bat")) {
    Write-Host "Error: jmeter-server.bat not found in $jmeterDir\bin"
    exit 1
}

# Display startup message
Write-Host "Starting JMeter Server..."
Write-Host "JMeter Directory: $jmeterDir"
Write-Host "Current Directory: $(Get-Location)"
Write-Host "----------------------------------------"

# Start JMeter server with custom properties
Write-Host "Starting JMeter server with custom configuration..."
.\jmeter-server.bat -Dserver_port=1099 -Djava.rmi.server.hostname=127.0.0.1