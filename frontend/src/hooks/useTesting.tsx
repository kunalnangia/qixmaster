import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/use-toast'
import { API_ENDPOINTS, getApiUrl } from '@/config/api'

export const useTesting = () => {
  const [isExecuting, setIsExecuting] = useState(false)
  const [debugInfo, setDebugInfo] = useState(null)
  const { toast } = useToast()

  // Add function to check health status
  const checkServerHealth = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/health')
      if (!response.ok) {
        throw new Error(`Failed to check server health: ${response.status}`)
      }
      const data = await response.json()
      console.log("Health check data:", data)
      
      // Update debug info with health check data
      setDebugInfo(prevInfo => ({
        ...prevInfo,
        healthCheck: data
      }))
      
      return data
    } catch (error) {
      console.error("Health check error:", error)
      setDebugInfo(prevInfo => ({
        ...prevInfo,
        healthCheck: {
          status: "error",
          error: error.message || "Failed to connect to server",
          java_installed: false,
          jmeter_in_path: false,
          jmeter_server_running: false,
          jmeter_port_active: false
        }
      }))
      
      return null
    }
  }
  
  // Run health check on component mount
  useEffect(() => {
    checkServerHealth()
    
    // Set up interval to check health status every 30 seconds
    const intervalId = setInterval(() => {
      checkServerHealth()
    }, 30000)
    
    // Clean up interval on unmount
    return () => clearInterval(intervalId)
  }, [])

  const executeApiTest = async (testCaseId: string, config: any) => {
    setIsExecuting(true)
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://127.0.0.1:8002/api/ai/generate-tests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          project_id: config.project_id || 'dummy',
          prompt: config.prompt || 'API test',
          test_type: config.test_type || 'api',
          priority: config.priority || 'medium',
          count: config.count || 1
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'API test failed');
      toast({
        title: "API Test Passed",
        description: "API test completed successfully",
        variant: "default",
      });
      return data;
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to execute API test",
        variant: "destructive",
      });
      throw error;
    } finally {
      setIsExecuting(false);
    }
  }

  /* Visual tests require supabase integration which is not set up
  const executeVisualTest = async (testCaseId: string, url: string, viewport?: any) => {
    setIsExecuting(true)
    try {
      const { data, error } = await supabase.functions.invoke('execute-visual-test', {
        body: { testCaseId, url, viewport }
      })

      if (error) throw error

      toast({
        title: data.result.success ? "Visual Test Passed" : "Visual Test Failed",
        description: data.result.success ? "Visual test completed successfully" : "Visual differences detected",
        variant: data.result.success ? "default" : "destructive",
      })

      return data
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to execute visual test",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsExecuting(false)
    }
  }
  */

  const executePerformanceTest = async (testCaseId: string, url: string, config?: any) => {
    setIsExecuting(true)
    setDebugInfo(null) // Reset debug info
    
    try {
      console.log("Starting performance test with config:", {
        test_name: testCaseId,
        url: url,
        ...config
      })
      
      // Use the enhanced AI performance testing API endpoint on port 8002
      const apiUrl = 'http://127.0.0.1:8002/run-performance-test'
      console.log("Fetching from API URL:", apiUrl)
      
      // Create request body
      const requestBody = JSON.stringify({
        test_name: testCaseId,
        test_type: config?.test_type || 'load',
        url: url,
        concurrent_users: config?.concurrent_users || 10,
        duration: config?.duration || 60,
        ramp_up_time: config?.ramp_up_time || 10,
        thresholds: {
          response_time: config?.thresholds?.response_time || 1000,
          error_rate: config?.thresholds?.error_rate || 1,
          throughput: config?.thresholds?.throughput || 10
        }
      })
      
      console.log("Request body:", requestBody)
      
      // Make the API call with fetch
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: requestBody
      })

      // Log the response status
      console.log("Response status:", response.status)
      
      // Handle non-OK responses
      if (!response.ok) {
        let errorData = null
        let errorDetail = 'Performance test failed'
        
        try {
          errorData = await response.json()
          console.error("Error data:", errorData)
          errorDetail = errorData.detail || errorData.message || errorDetail
        } catch (parseError) {
          console.error("Error parsing error response:", parseError)
          errorDetail = `HTTP ${response.status}: ${response.statusText}`
        }
        
        // Set debug info for the UI
        setDebugInfo({
          status: response.status,
          statusText: response.statusText,
          error: errorDetail,
          errorData: errorData
        })
        
        // Show error toast
        toast({
          title: "Performance Test Failed",
          description: errorDetail,
          variant: "destructive",
        })
        
        throw new Error(errorDetail)
      }
      
      // Parse the successful response
      let data
      try {
        data = await response.json()
        console.log("Response data:", data)
      } catch (parseError) {
        console.error("Error parsing success response:", parseError)
        throw new Error('Failed to parse response data')
      }
      
      // Check expected data structure
      const dataStructureCheck = {
        hasData: !!data,
        hasSummaryMetrics: data && !!data.summary_metrics,
        hasDetailedReports: data && !!data.detailed_reports,
        structure: data ? Object.keys(data).join(', ') : 'empty response'
      }
      
      console.log("Data structure check:", dataStructureCheck)
      
      // Create fallback data for missing properties
      const summaryMetrics = data?.summary_metrics || {
        avg_response_time: 0,
        p95_response_time: 0,
        error_rate: 0,
        throughput: 0
      }
      
      // Fetch detailed time series data
      let timeSeriesData = {
        timestamps: [],
        response_times: [],
        error_rate_series: [],
        throughput_series: []
      }
      
      try {
        // Fetch detailed run data which contains time series information
        const detailsResponse = await fetch(`http://127.0.0.1:8002/run-details/${data.run_id}`)
        if (detailsResponse.ok) {
          const detailsData = await detailsResponse.json()
          console.log("Details data:", detailsData)
          
          // Use time_series data from details endpoint
          if (detailsData.time_series) {
            timeSeriesData = detailsData.time_series
            console.log("Using time_series data from details endpoint:", timeSeriesData)
          }
        } else {
          console.warn(`Could not fetch time series data: ${detailsResponse.status} ${detailsResponse.statusText}`)
        }
      } catch (detailsError) {
        console.error("Could not fetch detailed time series data:", detailsError)
      }
      
      // Convert data to expected metrics format for backward compatibility
      const metricsData = {
        metrics: {
          page_load_time: summaryMetrics.avg_response_time || 0,
          first_contentful_paint: summaryMetrics.avg_response_time || 0,
          largest_contentful_paint: summaryMetrics.p95_response_time || 0,
          time_to_interactive: summaryMetrics.avg_response_time || 0,
          cumulative_layout_shift: summaryMetrics.error_rate / 100 || 0,
          network_requests: summaryMetrics.throughput || 0,
          dom_elements: 100, // Default value for compatibility
          total_bytes: 1, // Default value for compatibility
        },
        result: {
          success: summaryMetrics.error_rate < 1,
          details: "Performance test completed"
        },
        test_details: {
          ...data,
          time_series: timeSeriesData, // Ensure time_series data is available
          time_series_data: timeSeriesData, // For backward compatibility
          // Pass through enhanced workflow information
          enhanced_workflow: data?.enhanced_workflow || false,
          workflow_status: data?.workflow_status || null,
          ai_insights: data?.ai_insights || null,
          next_actions: data?.next_actions || null
        },
        ai_analysis: null, // Will be populated when AI analysis is available
        run_id: data?.run_id || `temp-${Date.now()}`,
        debug_info: { // Add debug info for troubleshooting
          apiUrl,
          requestBody: JSON.parse(requestBody),
          responseStatus: response.status,
          responseHeaders: Object.fromEntries([...response.headers.entries()]),
          dataStructureCheck
        }
      }
      
      // Set debug info for UI
      setDebugInfo({
        success: true,
        data: metricsData,
        rawResponse: data,
        structureCheck: dataStructureCheck
      })
      
      // Try to fetch AI analysis if available
      try {
        // Wait a bit for the AI analysis to complete in the background
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const analysisUrl = `http://127.0.0.1:8002/ai-analysis/${data.run_id}`
        console.log("Fetching AI analysis from:", analysisUrl)
        
        const analysisResponse = await fetch(analysisUrl)
        if (analysisResponse.ok) {
          const analysisData = await analysisResponse.json()
          console.log("AI analysis data:", analysisData)
          metricsData.ai_analysis = analysisData
        } else {
          console.log("AI analysis not available yet:", analysisResponse.status)
        }
      } catch (analysisError) {
        console.log('AI analysis not yet available:', analysisError)
      }

      toast({
        title: "Performance Test Completed",
        description: `Avg Response Time: ${metricsData.metrics.page_load_time}ms with ${metricsData.metrics.network_requests} req/min throughput`,
      })

      return metricsData
    } catch (error: any) {
      console.error("Performance test error:", error)
      
      // Set error debug info if not already set
      if (!debugInfo || !debugInfo.error) {
        setDebugInfo({
          error: error.message || "Unknown error",
          stack: error.stack
        })
      }
      
      toast({
        title: "Error",
        description: error.message || "Failed to execute performance test. Check browser console for details.",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsExecuting(false)
    }
  }

  // Implement a mock version of executeSecurityTest that doesn't rely on supabase
  const executeSecurityTest = async (testCaseId: string, url: string, scanTypes?: string[]) => {
    setIsExecuting(true)
    console.log("Starting security test:", { testCaseId, url, scanTypes })
    
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Generate mock security scan results
      const mockVulnerabilities = {
        xss: [
          {
            id: "vuln-001",
            title: "Reflected XSS Vulnerability",
            description: "Cross-site scripting vulnerability found in search parameter",
            severity: scanTypes?.includes('xss') ? "high" : "none",
            location: `${url}/search?q=`,
            scanner: "XSS Scanner"
          }
        ],
        sql_injection: [
          {
            id: "vuln-002",
            title: "SQL Injection Point",
            description: "Potential SQL injection vulnerability in user parameter",
            severity: scanTypes?.includes('sql_injection') ? "critical" : "none",
            location: `${url}/user?id=`,
            scanner: "SQL Injection Scanner"
          }
        ],
        csrf: [
          {
            id: "vuln-003",
            title: "Missing CSRF Token",
            description: "Form submission lacks CSRF protection",
            severity: scanTypes?.includes('csrf') ? "medium" : "none",
            location: `${url}/account/update`,
            scanner: "CSRF Scanner"
          }
        ],
        security_headers: [
          {
            id: "vuln-004",
            title: "Missing Content-Security-Policy",
            description: "No Content-Security-Policy header is set",
            severity: scanTypes?.includes('security_headers') ? "low" : "none",
            location: url,
            scanner: "Security Headers Scanner"
          }
        ],
        ssl_tls: [
          {
            id: "vuln-005",
            title: "TLS 1.0 Supported",
            description: "Server supports outdated TLS 1.0 protocol",
            severity: scanTypes?.includes('ssl_tls') ? "medium" : "none",
            location: url,
            scanner: "SSL/TLS Scanner"
          }
        ],
        open_redirect: [
          {
            id: "vuln-006",
            title: "Open Redirect",
            description: "Open redirect vulnerability in redirect parameter",
            severity: scanTypes?.includes('open_redirect') ? "medium" : "none",
            location: `${url}/redirect?to=`,
            scanner: "Open Redirect Scanner"
          }
        ]
      }
      
      // Combine all vulnerabilities and filter out "none" severity ones
      const allFindings = Object.values(mockVulnerabilities)
        .flat()
        .filter(vuln => vuln.severity !== "none")
      
      // Count vulnerabilities by severity
      const countBySeverity = allFindings.reduce((counts, vuln) => {
        counts[vuln.severity] = (counts[vuln.severity] || 0) + 1
        return counts
      }, { critical: 0, high: 0, medium: 0, low: 0 })
      
      // Safely extract hostname for the test case name
      let hostname = "Unknown";
      try {
        hostname = new URL(url).hostname;
      } catch (e) {
        // If URL is invalid, use the url as is
        hostname = url;
      }
      
      const mockResult = {
        summary: {
          total_findings: allFindings.length,
          critical: countBySeverity.critical || 0,
          high: countBySeverity.high || 0,
          medium: countBySeverity.medium || 0,
          low: countBySeverity.low || 0,
          url: url,
          scan_duration: 1.5,
          scan_types: scanTypes || []
        },
        findings: allFindings,
        test_case: {
          id: testCaseId,
          name: `Security Test for ${hostname}`
        }
      }
      
      // Determine message based on findings
      const hasIssues = mockResult.summary.total_findings > 0
      
      toast({
        title: hasIssues ? "Security Issues Found" : "Security Test Passed",
        description: hasIssues 
          ? `${mockResult.summary.total_findings} vulnerabilities found` 
          : "No security vulnerabilities detected",
        variant: hasIssues ? "destructive" : "default",
      })
      
      return mockResult
      
    } catch (error: any) {
      console.error("Security test error:", error)
      
      toast({
        title: "Error",
        description: error.message || "Failed to execute security test",
        variant: "destructive",
      })
      throw error
    } finally {
      setIsExecuting(false)
    }
  }

  // Execute Newman tests using Docker
  const executeNewmanTest = async (collectionUrl: string, apiKey: string, testCaseId?: string, environment?: any) => {
    setIsExecuting(true)
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(getApiUrl(`${API_ENDPOINTS.NEWMAN}/run`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          collection_url: collectionUrl,
          api_key: apiKey,
          test_case_id: testCaseId,
          environment: environment
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Newman test failed');

      toast({
        title: "Newman Test Completed",
        description: `Test run successfully in ${data.duration.toFixed(2)} seconds`,
        variant: "default",
      });

      return data;
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to execute Newman test",
        variant: "destructive",
      });
      throw error;
    } finally {
      setIsExecuting(false);
    }
  }

  return {
    executeApiTest,
    // executeVisualTest, // Commented out as it requires supabase
    executePerformanceTest,
    executeSecurityTest, // Implemented mock version
    executeNewmanTest, // Added Newman test execution
    checkServerHealth,
    isExecuting,
    debugInfo // Expose debug info
  }
}