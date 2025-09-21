import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import { API_ENDPOINTS, getApiUrl } from '@/config/api';

export interface Attachment {
  id: string;
  file_name: string;
  file_path: string;
  file_size: number;
  file_type: string;
  entity_type: string;
  entity_id: string;
  uploaded_by: string;
  description?: string;
  created_at: string;
}

export function useAttachments(entityType: string, entityId: string) {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchAttachments = async () => {
    if (!user || !entityType || !entityId) {
      return;
    }
    
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const url = `${API_ENDPOINTS.ATTACHMENTS}/${entityType}/${entityId}`;
      const fullUrl = getApiUrl(url);
      
      const response = await fetch(fullUrl, {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include',
        cache: 'no-store'
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch attachments');
      }
      
      const data = await response.json();
      setAttachments(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const uploadAttachment = async (file: File, description?: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('entity_type', entityType);
      formData.append('entity_id', entityId);
      formData.append('file', file);
      if (description) {
        formData.append('description', description);
      }

      const response = await fetch(getApiUrl(API_ENDPOINTS.ATTACHMENTS + '/upload'), {
        method: 'POST',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to upload attachment');
      }

      const data = await response.json();
      setAttachments(prev => [data, ...prev]);
      return { data, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload attachment';
      setError(errorMessage);
      return { data: null, error: errorMessage };
    }
  };

  const deleteAttachment = async (id: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(getApiUrl(`${API_ENDPOINTS.ATTACHMENTS}/${id}`), {
        method: 'DELETE',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to delete attachment');
      }

      setAttachments(prev => prev.filter(att => att.id !== id));
      return { error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete attachment';
      setError(errorMessage);
      return { error: errorMessage };
    }
  };

  useEffect(() => {
    fetchAttachments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entityType, entityId, user]);

  return {
    attachments,
    loading,
    error,
    uploadAttachment,
    deleteAttachment,
    refetch: fetchAttachments
  };
}