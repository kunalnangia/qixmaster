import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import { API_ENDPOINTS, getApiUrl } from '@/config/api';
import { TestCase } from './useTestCases';

export interface TestExecution {
  id: string;
  test_case_id: string;
  test_case: TestCase;
  start_time: string;
  end_time?: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  result?: 'pass' | 'fail' | 'error' | 'skipped';
  execution_time?: number; // in seconds
  error_message?: string;
  logs?: string[];
  screenshots?: string[];
  created_by?: string;
  project_id: string;
}

export function useTestExecutions(projectId?: string) {
  const [executions, setExecutions] = useState<TestExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchExecutions = async (forceRefresh = false) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const url = projectId 
        ? `${API_ENDPOINTS.TEST_EXECUTIONS}?project_id=${projectId}`
        : API_ENDPOINTS.TEST_EXECUTIONS;
      
      const fullUrl = getApiUrl(url);
      console.log('Fetching test executions from:', fullUrl);
      
      // For demo purposes, we'll simulate API response with mock data
      // In a real application, this would be an actual API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Mock data based on stored executions from localStorage
      const storedExecutions = localStorage.getItem('test_executions');
      const mockExecutions = storedExecutions ? JSON.parse(storedExecutions) : [];
      
      // Ensure we never exceed 10 records
      const limitedExecutions = mockExecutions.slice(0, 10);
      
      // If the stored data had more than 10 records, update localStorage
      if (mockExecutions.length > 10) {
        localStorage.setItem('test_executions', JSON.stringify(limitedExecutions));
      }
      
      setExecutions(limitedExecutions);
      return limitedExecutions;
    } catch (err) {
      console.error('Error in fetchExecutions:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      return [];
    } finally {
      setLoading(false);
    }
  };

  const executeTest = async (testCase: TestCase): Promise<TestExecution> => {
    try {
      // Start execution - in a real app, this would be an API call
      console.log('Executing test case:', testCase);
      
      // Create a new execution record
      const newExecution: TestExecution = {
        id: `exec-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
        test_case_id: testCase.id,
        test_case: testCase,
        start_time: new Date().toISOString(),
        status: 'running',
        project_id: testCase.project_id,
        created_by: user?.id,
        logs: ['Initializing test environment...', 'Starting test execution...']
      };
      
      // Update local state
      setExecutions(prev => [newExecution, ...prev]);
      
      // Store in localStorage for demo persistence, limited to 10 records
      const storedExecutions = localStorage.getItem('test_executions');
      const allExecutions = storedExecutions ? JSON.parse(storedExecutions) : [];
      
      // Limit to 10 records (including the new one)
      const limitedExecutions = [newExecution, ...allExecutions].slice(0, 10);
      localStorage.setItem('test_executions', JSON.stringify(limitedExecutions));
      
      // Simulate test execution time
      const executionTime = Math.floor(Math.random() * 10) + 2; // 2-12 seconds
      await new Promise(resolve => setTimeout(resolve, executionTime * 1000));
      
      // Generate a random result
      const resultOptions: TestExecution['result'][] = ['pass', 'fail', 'error', 'skipped'];
      const randomResult = Math.random();
      let result: TestExecution['result'];
      let errorMessage = '';
      
      if (randomResult > 0.75) {
        result = 'fail';
        errorMessage = 'Test assertion failed: Expected element to be visible';
      } else if (randomResult > 0.9) {
        result = 'error';
        errorMessage = 'Error during test execution: Element not found';
      } else if (randomResult > 0.95) {
        result = 'skipped';
      } else {
        result = 'pass';
      }
      
      // Update execution with results
      const updatedExecution: TestExecution = {
        ...newExecution,
        end_time: new Date().toISOString(),
        status: result === 'error' ? 'failed' : 'completed',
        result,
        execution_time: executionTime,
        error_message: errorMessage,
        logs: [
          ...newExecution.logs || [],
          'Test execution in progress...',
          result === 'pass' 
            ? 'All test steps passed successfully.' 
            : `Test ${result}: ${errorMessage}`
        ]
      };
      
      // Update local state
      setExecutions(prev => 
        prev.map(exec => exec.id === newExecution.id ? updatedExecution : exec)
      );
      
      // Update localStorage, maintaining the 10 record limit
      const updatedStoredExecutions = allExecutions.map(exec => 
        exec.id === newExecution.id ? updatedExecution : exec
      );
      
      // Ensure we're still limited to 10 records
      const updatedLimitedExecutions = updatedStoredExecutions.slice(0, 10);
      localStorage.setItem('test_executions', JSON.stringify(updatedLimitedExecutions));
      
      return updatedExecution;
    } catch (err) {
      console.error('Error executing test:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute test';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const clearExecutionHistory = () => {
    setExecutions([]);
    localStorage.removeItem('test_executions');
  };

  // Load executions on mount
  useEffect(() => {
    fetchExecutions();
  }, [projectId]);

  return { 
    executions, 
    loading, 
    error, 
    executeTest, 
    fetchExecutions, 
    clearExecutionHistory 
  };
}