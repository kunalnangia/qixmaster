// Base URL for API requests - Using relative URL for proxy support
export const API_BASE_URL = '/api/v1';

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  PROJECTS: '/projects',
  TEST_CASES: '/test-cases',
  TEST_EXECUTIONS: '/test-executions',
  TEAMS: '/teams',
  EXECUTIONS: '/executions',
  COMMENTS: '/comments',
  ATTACHMENTS: '/attachments',
  ENVIRONMENTS: '/environments',
  AI: '/ai',
  NEWMAN: '/newman',
  TEST_PLANS: '/test-plans', // Added missing TEST_PLANS endpoint
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  // Don't add base URL if it's already included or if it's a relative URL for proxy
  if (endpoint.startsWith('http') || endpoint.startsWith('/api')) {
    // For proxy requests, return the endpoint directly if it starts with /api
    if (endpoint.startsWith('/api')) {
      return endpoint;
    }
    return endpoint;
  }
  return `${API_BASE_URL}${endpoint}`;
};