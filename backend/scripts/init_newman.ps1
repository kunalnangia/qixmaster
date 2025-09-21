Write-Host "Initializing Docker Newman..."
Write-Host "Pulling postman/newman Docker image..."

docker pull postman/newman
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker Newman image is ready."
} else {
    Write-Error "Failed to pull Docker Newman image."
    exit $LASTEXITCODE
}

Write-Host "Testing Docker Newman..."
docker run --rm -t postman/newman --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker Newman is working correctly."
} else {
    Write-Error "Docker Newman test failed."
    exit $LASTEXITCODE
}

Write-Host "Docker Newman initialization complete."