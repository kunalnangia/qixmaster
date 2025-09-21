@echo off
echo Initializing Docker Newman...
echo Pulling postman/newman Docker image...
docker pull postman/newman
if %errorlevel% == 0 (
    echo Docker Newman image is ready.
) else (
    echo Failed to pull Docker Newman image.
    exit /b %errorlevel%
)

echo Testing Docker Newman...
docker run --rm -t postman/newman --version
if %errorlevel% == 0 (
    echo Docker Newman is working correctly.
) else (
    echo Docker Newman test failed.
    exit /b %errorlevel%
)

echo Docker Newman initialization complete.