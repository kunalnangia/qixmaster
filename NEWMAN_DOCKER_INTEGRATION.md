# Newman Docker Integration

This document explains how the Newman Docker integration works in the IntelliTest platform.

## Overview

The IntelliTest platform uses Docker to run Postman collections via Newman, allowing users to execute API tests without needing to install Newman locally.

## Prerequisites

1. Docker must be installed and running on the system
2. Internet access to pull the `postman/newman` Docker image

## How It Works

1. When the application starts, it automatically:
   - Checks if Docker is available
   - Pulls the `postman/newman` Docker image if not already present
   - Tests the Newman installation

2. When a user runs a Newman test:
   - The application constructs a Docker command to run Newman
   - The command includes the collection URL and any environment variables
   - The Docker container executes the test and returns results

## Running Newman Tests

### Via the API

Send a POST request to `/api/v1/newman/run` with the following JSON body:

```json
{
  "collection_url": "https://api.getpostman.com/collections/COLLECTION_ID?apikey=API_KEY",
  "api_key": "YOUR_POSTMAN_API_KEY",
  "test_case_id": "OPTIONAL_TEST_CASE_ID",
  "environment": {
    "variable1": "value1",
    "variable2": "value2"
  }
}
```

### Via the Web Interface

1. Navigate to the API Testing page
2. Go to the "Newman Test" tab
3. Enter the Collection URL and API Key
4. Optionally add environment variables
5. Click "Execute Newman Test"

## Example Usage

To run a specific Postman collection with the ID `47463989-8d6cec84-fb64-48dc-8d71-7c2e6ba45c28`:

```bash
docker run -t postman/newman run "https://api.getpostman.com/collections/47463989-8d6cec84-fb64-48dc-8d71-7c2e6ba45c28?apikey=PMAK-68bc06cf8e88740001889312-b50afdd3066958a44f1a7d8ed5e48cf10d"
```

## Troubleshooting

### Docker Not Found

If Docker is not installed or not in the PATH:
1. Install Docker Desktop
2. Ensure Docker is running
3. Restart the application

### Newman Image Pull Fails

If the Newman image fails to pull:
1. Check internet connectivity
2. Try manually pulling the image: `docker pull postman/newman`
3. Check Docker disk space

### Test Execution Issues

If tests fail to execute:
1. Verify the collection URL is correct
2. Ensure the API key is valid
3. Check that the collection is accessible
4. Verify environment variables are correctly formatted

## Scripts

The following scripts are available to help with Newman initialization:

- `backend/scripts/init_newman.bat` - Windows batch script
- `backend/scripts/init_newman.ps1` - PowerShell script

## Security Notes

- API keys are passed securely through the request body
- Docker containers are run with minimal privileges
- Containers are automatically removed after execution (`--rm` flag)