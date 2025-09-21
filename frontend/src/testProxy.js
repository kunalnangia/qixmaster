// Simple test to verify proxy configuration
console.log('Testing proxy configuration...');

// This should be proxied to http://127.0.0.1:8002/api/v1/projects
fetch('/api/v1/projects')
  .then(response => {
    console.log('Proxy test successful:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Projects data:', data);
  })
  .catch(error => {
    console.error('Proxy test failed:', error);
  });

// This should be proxied to http://127.0.0.1:8002/api/v1/test-cases
fetch('/api/v1/test-cases')
  .then(response => {
    console.log('Proxy test successful:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Test cases data:', data);
  })
  .catch(error => {
    console.error('Proxy test failed:', error);
  });