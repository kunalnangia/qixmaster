import { useState } from 'react'
import { supabase } from '@/integrations/supabase/client'
import { useToast } from '@/hooks/use-toast'
import { API_ENDPOINTS, getApiUrl } from '@/config/api'

export const useAI = () => {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isDebugging, setIsDebugging] = useState(false)
  const { toast } = useToast()

  const generateTests = async (prompt: string, projectId: string) => {
    setIsGenerating(true)
    try {
      const { data, error } = await supabase.functions.invoke('ai-generate-tests', {
        body: { prompt, projectId }
      })

      if (error) throw error

      toast({
        title: "Success",
        description: "AI test cases generated successfully",
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to generate test cases",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsGenerating(false)
    }
  }

  const generateTestsFromUrl = async (url: string, projectId: string) => {
    setIsGenerating(true)
    try {
      // Validate URL format
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        throw new Error('Invalid URL format. URL must start with http:// or https://')
      }
      
      // Use the proxy URL for URL-based test case generation
      const backendUrl = getApiUrl(`${API_ENDPOINTS.TEST_CASES}/generate-from-url`)
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      
      console.log(`Generating test cases from URL: ${url} for project: ${projectId}`)
      
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          url,
          project_id: projectId,
          test_count: 5
        })
      })

      if (!response.ok) {
        // Try to parse error response
        let errorMessage = 'Failed to generate test cases from URL'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          // If JSON parsing fails, use status text
          errorMessage = `HTTP ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      let data
      try {
        data = await response.json()
        console.log('Generated test cases successfully:', data)
      } catch (jsonError) {
        console.error('Failed to parse JSON response:', jsonError)
        throw new Error('Failed to parse response from server. The response may be malformed.')
      }

      toast({
        title: "Success",
        description: `Generated ${data.generated_test_cases?.length || 0} test cases from URL successfully`,
      })

      // Return the data in the format expected by the frontend
      return { tests: { testCases: data.generated_test_cases } }
    } catch (error: any) {
      console.error('Error generating test cases from URL:', error)
      toast({
        title: "Error Generating Test Cases",
        description: error.message || "Failed to generate test cases from URL",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsGenerating(false)
    }
  }

  const debugTest = async (testCaseId: string, errorDescription: string, logs?: any) => {
    setIsDebugging(true)
    try {
      const { data, error } = await supabase.functions.invoke('ai-debug-tests', {
        body: { testCaseId, errorDescription, logs }
      })

      if (error) throw error

      toast({
        title: "Success", 
        description: "AI debugging analysis completed",
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to debug test case",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsDebugging(false)
    }
  }

  return {
    generateTests,
    generateTestsFromUrl,
    debugTest,
    isGenerating,
    isDebugging
  }
}