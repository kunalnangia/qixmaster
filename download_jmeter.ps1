# PowerShell script to download and extract JMeter

Write-Host "Downloading Apache JMeter..." -ForegroundColor Green

# JMeter download URL
$jmeterUrl = "https://dlcdn.apache.org/jmeter/binaries/apache-jmeter-5.6.3.zip"
$jmeterZip = "apache-jmeter-5.6.3.zip"

try {
    # Download JMeter
    Write-Host "Downloading JMeter from $jmeterUrl" -ForegroundColor Yellow
    Invoke-WebRequest -Uri $jmeterUrl -OutFile $jmeterZip
    Write-Host "Download completed: $jmeterZip" -ForegroundColor Green
    
    # Extract JMeter
    Write-Host "Extracting JMeter..." -ForegroundColor Yellow
    Expand-Archive -Path $jmeterZip -DestinationPath "." -Force
    Write-Host "Extraction completed!" -ForegroundColor Green
    
    # Clean up zip file
    Remove-Item $jmeterZip
    Write-Host "Cleaned up temporary files" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "JMeter has been successfully downloaded and extracted!" -ForegroundColor Green
    Write-Host "Directory: $(Get-Location)\apache-jmeter-5.6.3" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Run complete_setup.bat to configure environment variables" -ForegroundColor Yellow
    Write-Host "2. Restart your PowerShell terminal" -ForegroundColor Yellow
    Write-Host "3. Verify installation with: jmeter --version" -ForegroundColor Yellow
}
catch {
    Write-Host "Error occurred during JMeter setup:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Please manually download JMeter from https://jmeter.apache.org/download_jmeter.cgi" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")