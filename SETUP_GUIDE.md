# Complete Setup Guide for AI Perf Tester

This guide will help you set up Java and JMeter required for running performance tests.

## Prerequisites

- Windows 10 or later
- Administrator privileges (for some setup steps)

## Step-by-Step Setup

### 1. Install Java JDK 24

1. Download OpenJDK 24 from [https://adoptium.net/](https://adoptium.net/)
2. Run the installer and follow the installation wizard
3. Install to the default location (`C:\Program Files\Java\jdk-24`)

### 2. Download and Extract JMeter

Option A - Automatic (Recommended):
1. Run the PowerShell script to download and extract JMeter:
   ```powershell
   .\download_jmeter.ps1
   ```

Option B - Manual:
1. Download Apache JMeter from [https://jmeter.apache.org/download_jmeter.cgi](https://jmeter.apache.org/download_jmeter.cgi)
2. Extract to a folder named `apache-jmeter-5.6.3` in this directory

### 3. Install Docker Desktop

1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the installation wizard
3. Restart your computer after installation
4. Start Docker Desktop and ensure it's running

### 4. Configure Environment Variables

Option A - Automatic (Recommended):
1. Run the complete setup script:
   ```powershell
   .\complete_setup.bat
   ```

Option B - Manual:
1. Set JAVA_HOME:
   - Open System Properties → Advanced → Environment Variables
   - Under System Variables, click "New"
   - Variable name: `JAVA_HOME`
   - Variable value: `C:\Program Files\Java\jdk-24`
   - Click OK to save

2. Set JMETER_HOME:
   - In the same Environment Variables window, click "New"
   - Variable name: `JMETER_HOME`
   - Variable value: Full path to your JMeter installation (e.g., `C:\Users\kunal\Downloads\qix-master\qix-master\apache-jmeter-5.6.3`)
   - Click OK to save

3. Add to PATH:
   - In the same Environment Variables window, find and select "Path", then click "Edit"
   - Click "New" and add: `%JAVA_HOME%\bin`
   - Click "New" and add: `%JMETER_HOME%\bin`
   - Click "New" and add: `C:\Program Files\Docker\Docker\resources\bin` (if Docker is installed in default location)
   - Click OK to save

### 4. Restart Your Terminal

Close all PowerShell/command prompt windows and open a new one.

### 5. Verify Installation

Run the verification script:
```powershell
.\verify_setup.ps1
```

Or manually verify:
```powershell
java -version
jmeter --version
docker --version
```

You should see output similar to:
```
openjdk version "24" 2024-03-19
OpenJDK Runtime Environment (build 24+36-2426)
OpenJDK 64-Bit Server VM (build 24+36-2426, mixed mode, sharing)

Apache JMeter 5.6.3

Docker version 20.10.21, build baeda1f
```

### 6. Initialize Docker Newman

The system will automatically initialize Docker Newman when you start the services, but you can manually initialize it:

```powershell
cd backend
.\scripts\init_newman.ps1
```

Or on Windows Command Prompt:
```cmd
cd backend
scripts\init_newman.bat
```

## Running Performance Tests

Once setup is complete:

1. Start all services using the batch script:
   ```cmd
   .\start-all-services.bat
   ```

2. Open your browser to [http://localhost:5175](http://localhost:5175)

3. Navigate to the API Testing page to run Newman tests:
   - Go to the "Newman Test" tab
   - Enter your Postman collection URL and API key
   - Click "Execute Newman Test"

## Troubleshooting

### Issue: "java is not recognized as an internal or external command"

Solution:
1. Verify Java is installed in `C:\Program Files\Java\jdk-24`
2. Ensure JAVA_HOME is set correctly
3. Ensure `%JAVA_HOME%\bin` is in your PATH
4. Restart your terminal

### Issue: "jmeter is not recognized as an internal or external command"

Solution:
1. Verify JMeter is extracted to `apache-jmeter-5.6.3` directory
2. Ensure JMETER_HOME is set correctly
3. Ensure `%JMETER_HOME%\bin` is in your PATH
4. Restart your terminal

### Issue: "docker is not recognized as an internal or external command"

Solution:
1. Verify Docker Desktop is installed
2. Ensure Docker is running
3. Ensure Docker's bin directory is in your PATH
4. Restart your terminal

### Issue: "Not able to find Java executable or version"

Solution:
1. Verify Java installation
2. Check that JAVA_HOME points to the correct directory
3. Ensure the `bin` directory exists under JAVA_HOME

### Issue: "Newman tests are not working"

Solution:
1. Verify Docker is installed and running
2. Check that the `postman/newman` Docker image is available:
   ```cmd
   docker image ls | findstr newman
   ```
3. If not available, pull the image manually:
   ```cmd
   docker pull postman/newman
   ```

## Additional Resources

- Java Documentation: [https://adoptium.net/documentation.html](https://adoptium.net/documentation.html)
- JMeter Documentation: [https://jmeter.apache.org/usermanual/index.html](https://jmeter.apache.org/usermanual/index.html)
- Docker Documentation: [https://docs.docker.com/](https://docs.docker.com/)
- Postman Newman Documentation: [https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/](https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/)
- AI Perf Tester Documentation: [ai-perf-tester/README.md](ai-perf-tester/README.md)