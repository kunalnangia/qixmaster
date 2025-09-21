#!/bin/bash

echo "Initializing Docker Newman..."
echo "Pulling postman/newman Docker image..."

docker pull postman/newman
if [ $? -eq 0 ]; then
    echo "Docker Newman image is ready."
else
    echo "Failed to pull Docker Newman image."
    exit 1
fi

echo "Testing Docker Newman..."
docker run --rm -t postman/newman --version
if [ $? -eq 0 ]; then
    echo "Docker Newman is working correctly."
else
    echo "Docker Newman test failed."
    exit 1
fi

echo "Docker Newman initialization complete."