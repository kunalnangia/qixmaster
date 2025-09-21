import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import { API_ENDPOINTS, getApiUrl } from '@/config/api';

export interface TestCase {
  // Basic Information
  id: string;
  title: string;
  description?: string;
  requirement_reference?: string; // Jira/Requirement ID
  project_id: string;
  test_type: 'functional' | 'regression' | 'smoke' | 'uat' | 'performance' | 'security' | 'api' | 'visual' | 'integration' | 'unit';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'draft' | 'ready' | 'pass' | 'fail' | 'blocked' | 'not_run';
  module_feature?: string; // Area of the application
  tags: string[];
  version_build?: string; // Application version being tested
  
  // Execution-Focused Fields
  preconditions?: string; // Setup/data/environment required
  test_data?: Record<string, any>; // Inputs, files, parameters, credentials
  expected_result?: string;
  actual_result?: string;
  environment?: 'dev' | 'qa' | 'staging' | 'prod';
  automation_status?: 'manual' | 'automated' | 'candidate';
  
  // Ownership and Tracking
  created_by: string;
  assigned_to?: string;
  owner?: string; // Who created/owns the test
  
  // AI and System Fields
  ai_generated: boolean;
  self_healing_enabled: boolean;
  
  // Collaboration & Reporting Fields
  linked_defects: string[]; // Integration with bug tracker
  attachments: string[]; // Screenshots, logs, API payloads, UX mocks
  
  // Timestamps
  created_at: string;
  updated_at: string;
  
  // Test Steps
  steps?: any;
}

export interface TestStep {
  id: string;
  test_case_id: string;
  step_number: number;
  description: string;
  expected_result: string;
  actual_result?: string;
  created_at: string;
  updated_at: string;
}

export function useTestCases(projectId?: string) {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchTestCases = async (forceRefresh = false) => {
    if (!user) {
      console.log('No user found, skipping test cases fetch');
      return;
    }
    
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const url = projectId 
        ? `${API_ENDPOINTS.TEST_CASES}?project_id=${projectId}`
        : API_ENDPOINTS.TEST_CASES;
      
      const fullUrl = getApiUrl(url);
      console.log('Fetching test cases from:', fullUrl);
      console.log('Using token:', token ? 'Token available' : 'No token found');
      
      const response = await fetch(fullUrl, {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include',  // Important for cookies/sessions if using them
        // Add cache control headers to prevent caching
        cache: forceRefresh ? 'no-cache' : 'no-store',
        // Add additional headers to prevent caching
        ...(forceRefresh && {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        })
      });
      
      console.log('Test cases response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error response:', errorData);
        throw new Error(errorData.detail || 'Failed to fetch test cases');
      }
      
      const data = await response.json();
      console.log('Test cases data:', data);
      setTestCases(data || []);
    } catch (err) {
      console.error('Error in fetchTestCases:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const createTestCase = async (testCaseData: Omit<TestCase, 'id' | 'created_at' | 'updated_at' | 'created_by'>) => {
    try {
      const token = localStorage.getItem('access_token');
      console.log('Creating test case with data:', testCaseData);
      
      const response = await fetch(getApiUrl(API_ENDPOINTS.TEST_CASES), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          ...testCaseData,
          created_by: user?.id
        })
      });
      
      console.log('Create test case response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error response from create test case:', errorData);
        
        // Show specific error message for authentication issues
        if (response.status === 401) {
          throw new Error('Authentication required. Please log in to create test cases.');
        }
        
        throw new Error(errorData.detail || 'Failed to create test case');
      }
      
      const data = await response.json();
      console.log('Created test case:', data);
      setTestCases(prev => [data, ...prev]);
      return { data, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create test case';
      console.error('Error in createTestCase:', errorMessage);
      setError(errorMessage);
      return { data: null, error: errorMessage };
    }
  };

  const updateTestCase = async (id: string, updates: Partial<TestCase>) => {
    try {
      const token = localStorage.getItem('access_token');
      console.log('Updating test case with id:', id, 'Updates:', updates);
      
      const response = await fetch(getApiUrl(`${API_ENDPOINTS.TEST_CASES}/${id}`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(updates)
      });
      
      console.log('Update test case response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error response from update test case:', errorData);
        
        // Show specific error message for authentication issues
        if (response.status === 401) {
          throw new Error('Authentication required. Please log in to update test cases.');
        }
        
        throw new Error(errorData.detail || 'Failed to update test case');
      }
      
      const data = await response.json();
      console.log('Updated test case:', data);
      setTestCases(prev => prev.map(tc => tc.id === id ? data : tc));
      return { data, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update test case';
      console.error('Error in updateTestCase:', errorMessage);
      setError(errorMessage);
      return { data: null, error: errorMessage };
    }
  };

  const deleteTestCase = async (id: string) => {
    try {
      const token = localStorage.getItem('access_token');
      console.log('Deleting test case with id:', id);
      
      const response = await fetch(getApiUrl(`${API_ENDPOINTS.TEST_CASES}/${id}`), {
        method: 'DELETE',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      });
      
      console.log('Delete test case response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error response from delete test case:', errorData);
        
        // Show specific error message for authentication issues
        if (response.status === 401) {
          throw new Error('Authentication required. Please log in to delete test cases.');
        }
        
        throw new Error(errorData.detail || 'Failed to delete test case');
      }
      
      console.log('Test case deleted successfully');
      setTestCases(prev => prev.filter(tc => tc.id !== id));
      return { error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete test case';
      console.error('Error in deleteTestCase:', errorMessage);
      setError(errorMessage);
      return { error: errorMessage };
    }
  };

  const refetch = async () => {
    await fetchTestCases(true); // Force refresh
  };

  useEffect(() => {
    fetchTestCases();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, user]);

  return {
    testCases,
    loading,
    error,
    createTestCase,
    updateTestCase,
    deleteTestCase,
    refetch
  };
}