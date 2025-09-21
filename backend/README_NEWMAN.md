# Newman Docker Integration

## Overview
This backend service integrates with Postman Newman via Docker to run API test collections.

## Prerequisites
- Docker must be installed and running
- Internet access to pull the `postman/newman` image

## How It Works
1. On application startup, the system automatically:
   - Verifies Docker is available
   - Pulls the `postman/newman` image if needed
   - Tests Newman functionality

2. When running tests, the system:
   - Constructs Docker commands to run Newman
   - Executes collections with provided parameters
   - Returns results to the client

## Testing
To test Newman functionality directly:

```bash
# Test Newman version
docker run --rm -t postman/newman --version

# Run a specific collection (example)
docker run --rm -t postman/newman run "https://api.getpostman.com/collections/47463989-8d6cec84-fb64-48dc-8d71-7c2e6ba45c28?apikey=YOUR_API_KEY"
```

## API Endpoint
POST `/api/v1/newman/run`

Request body:
```json
{
  "collection_url": "https://api.getpostman.com/collections/COLLECTION_ID?apikey=API_KEY",
  "api_key": "YOUR_POSTMAN_API_KEY",
  "test_case_id": "optional_test_case_id",
  "environment": {
    "var1": "value1",
    "var2": "value2"
  }
}
```

## Scripts
- `scripts/init_newman.bat` - Windows batch initialization script
- `scripts/init_newman.ps1` - PowerShell initialization script

## Troubleshooting
1. Ensure Docker is running
2. Check if `postman/newman` image is available: `docker images | grep newman`
3. Manually pull image if needed: `docker pull postman/newman`