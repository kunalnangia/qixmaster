# start-jmeter-server.ps1
# Script to start JMeter server from the correct directory with custom configuration

# Change to the JMeter bin directory
Set-Location "C:\Users\kunal\Downloads\qix-master\qix-master\apache-jmeter-5.6.3\bin"

# Set the server port environment variable
$env:SERVER_PORT = "54000"

# Start the JMeter server with custom properties including RMI configuration
.\jmeter-server.bat -Dserver_port=54000 -Jserver.rmi.localport=54000 -Jserver.rmi.port=54000 -Jserver.rmi.create=true -Jclient.rmi.localport=54000 -Jserver_port=54001 -Djava.rmi.server.hostname=127.0.0.1