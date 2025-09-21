# Add JMeter alias to PowerShell profile
# This script adds an alias for 'jmeter' that points to 'jmeter.bat'

# Get the user's PowerShell profile path
$profilePath = $PROFILE

# Create the profile file if it doesn't exist
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force
}

# Check if the alias already exists in the profile
$profileContent = Get-Content $profilePath -ErrorAction SilentlyContinue
$aliasExists = $profileContent -match "Set-Alias -Name jmeter -Value.*jmeter.bat"

if (-not $aliasExists) {
    # Add the alias to the profile
    Add-Content -Path $profilePath -Value ""
    Add-Content -Path $profilePath -Value "# JMeter alias"
    Add-Content -Path $profilePath -Value "Set-Alias -Name jmeter -Value '$(Resolve-Path 'apache-jmeter-5.6.3\bin\jmeter.bat')'"
    Write-Host "JMeter alias added to PowerShell profile. Please restart your PowerShell session."
} else {
    Write-Host "JMeter alias already exists in PowerShell profile."
}