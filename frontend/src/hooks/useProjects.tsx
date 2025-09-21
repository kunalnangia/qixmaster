import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';
import { API_ENDPOINTS, getApiUrl } from '@/config/api';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  team_id: string | null;
  created_by: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  test_case_count?: number;
  environment_count?: number;
  last_execution?: string | null;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  team_id?: string;
  is_active?: boolean;
}

export interface ProjectUpdate extends Partial<ProjectCreate> {
  id: string;
}

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const getAuthHeaders = useCallback(() => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
  }, []);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // First try the authenticated endpoint
      const endpoint = getApiUrl(API_ENDPOINTS.PROJECTS);
      console.log('Fetching projects from:', endpoint);
      
      const response = await fetch(endpoint, {
        headers: getAuthHeaders()
      });
      
      console.log('Projects response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Projects data received:', data);
        setProjects(Array.isArray(data) ? data : []);
        setError(null);
        return;
      }
      
      // If authenticated endpoint fails, try the test endpoint
      console.log('Authenticated endpoint failed, trying test endpoint...');
      const testEndpoint = getApiUrl('/projects-test');
      const testResponse = await fetch(testEndpoint);
      
      if (testResponse.ok) {
        const testData = await testResponse.json();
        console.log('Test projects data received:', testData);
        setProjects(Array.isArray(testData) ? testData : []);
        setError(null);
      } else {
        const errorData = await testResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${testResponse.status}: Failed to fetch projects`);
      }
    } catch (err) {
      console.error('Error in fetchProjects:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch projects';
      setError(errorMessage);
      setProjects([]); // Clear projects on error
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders]);

  const createProject = async (projectData: ProjectCreate) => {
    try {
      setLoading(true);
      const response = await fetch(getApiUrl(API_ENDPOINTS.PROJECTS), {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          ...projectData,
          is_active: projectData.is_active ?? true
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create project');
      }
      
      await fetchProjects();
      setError(null);
      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create project';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const updateProject = async ({ id, ...updateData }: ProjectUpdate) => {
    try {
      setLoading(true);
      const response = await fetch(getApiUrl(`${API_ENDPOINTS.PROJECTS}/${id}`), {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to update project');
      }
      
      await fetchProjects();
      setError(null);
      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update project';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (id: string) => {
    try {
      setLoading(true);
      const response = await fetch(getApiUrl(`${API_ENDPOINTS.PROJECTS}/${id}`), {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (!response.ok && response.status !== 204) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to delete project');
      }
      
      await fetchProjects();
      setError(null);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete project';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const getProjectById = useCallback(async (id: string) => {
    try {
      setLoading(true);
      const response = await fetch(getApiUrl(`${API_ENDPOINTS.PROJECTS}/${id}`), {
        headers: getAuthHeaders()
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch project');
      }
      
      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch project';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders]);

  useEffect(() => {
    console.log('useProjects effect triggered');
    console.log('User:', user);
    console.log('Projects:', projects);
    console.log('Loading:', loading);
    console.log('Error:', error);
    
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    getProjectById,
    clearError: () => setError(null)
  };
}