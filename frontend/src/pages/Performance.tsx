import { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import { useTesting } from "@/hooks/useTesting"
import { 
  Card, 
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  LineChart,
  BarChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { BarChart3 } from "lucide-react"
import * as XLSX from 'xlsx'

const Performance = () => {
  const [selectedTestCase, setSelectedTestCase] = useState("")
  const [url, setUrl] = useState("https://hostbooks.com")
  const [testType, setTestType] = useState("load")
  const [loadPattern, setLoadPattern] = useState("ramp_up")
  const [concurrentUsers, setConcurrentUsers] = useState(10)
  const [duration, setDuration] = useState(30) // Reduced default duration
  const [rampUpTime, setRampUpTime] = useState(2) // Reduced default ramp-up time
  const [thresholds, setThresholds] = useState({
    response_time: 1000,
    max_95th_percentile: 1500,
    error_rate: 1,
    throughput: 10
  })
  const [testResult, setTestResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState("") 
  const [testHistory, setTestHistory] = useState([])
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [selectedRunId, setSelectedRunId] = useState(null)
  const [localDebugInfo, setLocalDebugInfo] = useState(null)
  const { executePerformanceTest, isExecuting, debugInfo, checkServerHealth } = useTesting()
  const { toast } = useToast()

  const handleExecuteTest = async () => {
    if (!selectedTestCase || !url) {
      toast({
        title: "Missing Information",
        description: "Please select a test case and enter a URL",
        variant: "destructive",
      })
      return
    }

    try {
      // Clear any previous error messages
      setErrorMessage("");
      
      // Pass advanced configuration to the performance test
      const config = {
        test_type: testType,
        load_pattern: loadPattern,
        concurrent_users: concurrentUsers,
        duration: duration,
        ramp_up_time: rampUpTime,
        thresholds: thresholds
      }
      
      console.log("Starting performance test with config:", config)
      
      const result = await executePerformanceTest(selectedTestCase, url, config)
      console.log("Performance test result:", result)
      
      // Add detailed structure logging for debugging
      console.log("Result structure:", {
        hasResult: !!result,
        hasTestDetails: result && !!result.test_details,
        hasTimeSeries: result && result.test_details && !!result.test_details.time_series,
        hasTimestamps: result && result.test_details && result.test_details.time_series && !!result.test_details.time_series.timestamps,
        dataStructure: JSON.stringify(result, null, 2)
      });
      
      // Save raw result to debug info
      const updatedDebugInfo = {
        rawResponse: result,
        structureCheck: {
          hasResult: !!result,
          hasTestDetails: result && !!result.test_details,
          hasTimeSeries: result && result.test_details && !!result.test_details.time_series,
          hasTimestamps: result && result.test_details && result.test_details.time_series && !!result.test_details.time_series.timestamps
        }
      };
      
      // Update the result with defaults if certain structures are missing
      let processedResult = result;
      if (result) {
        if (!result.test_details) {
          processedResult = {
            ...result,
            test_details: {}
          };
        }
        
        if (!result.test_details?.time_series) {
          processedResult = {
            ...processedResult,
            test_details: {
              ...processedResult.test_details,
              time_series: {}
            }
          };
        }
        
        if (!result.test_details?.time_series?.timestamps) {
          processedResult = {
            ...processedResult,
            test_details: {
              ...processedResult.test_details,
              time_series: {
                ...processedResult.test_details.time_series,
                timestamps: [],
                response_times: [],
                error_rate_series: [],
                throughput_series: []
              }
            }
          };
        }
      }
      
      // Still show error message but don't prevent rendering with defaults
      if (!result || !result.test_details || !result.test_details.time_series) {
        setErrorMessage("The test completed, but returned data in an unexpected format. Default placeholders have been added. Check the Debug tab for the actual data structure.");
        toast({
          title: "Data Structure Warning",
          description: "Displaying results with default placeholders for missing data",
          variant: "destructive",
        });
      }
      
      setTestResult(processedResult)
    } catch (error) {
      console.error('Error executing performance test:', error)
      setErrorMessage(`Error executing test: ${error.message || 'Unknown error'}`)
      // Error is handled by the useTesting hook toast
    }
  }

  const exportToExcel = () => {
    // Check for time_series data in either format
    const timeSeries = testResult?.test_details?.time_series || testResult?.test_details?.time_series_data;
    
    if (!testResult || !testResult.test_details || !timeSeries || !timeSeries.timestamps) {
      toast({
        title: "Export Failed",
        description: "No time series data available to export",
        variant: "destructive",
      })
      return
    }

    // Prepare data for export
    const data = timeSeries.timestamps.map((ts: string, i: number) => ({
      Timestamp: new Date(ts).toLocaleString(),
      'Response Time (ms)': timeSeries.response_times[i],
      'Error Rate (%)': timeSeries.error_rate_series[i],
      'Throughput (req/min)': timeSeries.throughput_series[i]
    }))

    // Create worksheet
    const ws = XLSX.utils.json_to_sheet(data)
    
    // Create workbook
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Performance Data')
    
    // Export file
    XLSX.writeFile(wb, `performance_test_${selectedTestCase}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`)
    
    toast({
      title: "Export Successful",
      description: "Performance data exported to Excel",
    })
  }

  const getPerformanceScore = (value: number, thresholds: { good: number, needs_improvement: number }) => {
    if (value <= thresholds.good) return { score: 'good', color: 'bg-green-500' }
    if (value <= thresholds.needs_improvement) return { score: 'needs improvement', color: 'bg-yellow-500' }
    return { score: 'poor', color: 'bg-red-500' }
  }

  const formatBytes = (bytes: number) => {
    return `${bytes} MB`
  }

  // Function to load test history
  const fetchHistory = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8002/performance-history');
      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.status}`);
      }
      const data = await response.json();
      setTestHistory(data);
    } catch (error) {
      console.error('Error fetching test history:', error);
      toast({
        title: "Error",
        description: "Failed to load test history",
        variant: "destructive",
      });
    }
  };

  // Function to load AI analysis for a specific run
  const fetchAiAnalysis = async (runId: string) => {
    if (!runId) return;
    
    try {
      setAiAnalysis(null); // Clear previous analysis
      const response = await fetch(`http://127.0.0.1:8002/ai-analysis/${runId}`);
      if (!response.ok) {
        if (response.status === 404) {
          setAiAnalysis({ error: "AI analysis not found for this test run" });
          return;
        }
        throw new Error(`Failed to fetch AI analysis: ${response.status}`);
      }
      const data = await response.json();
      setAiAnalysis(data);
      setSelectedRunId(runId);
    } catch (error: any) {
      console.error('Error fetching AI analysis:', error);
      setAiAnalysis({ error: error.message || "Failed to load AI analysis" });
    }
  };
  
  // Sync debugInfo from the hook to localDebugInfo
  useEffect(() => {
    if (debugInfo) {
      setLocalDebugInfo(prevInfo => ({
        ...prevInfo,
        ...debugInfo
      }))
    }
  }, [debugInfo])
  
  // Load test history on component mount
  useEffect(() => {
    fetchHistory();
  }, []);
  
  // Refresh history when a test completes
  useEffect(() => {
    if (testResult && !isExecuting) {
      fetchHistory();
      // Also fetch AI analysis for the current test
      if (testResult.run_id) {
        // Wait a bit to allow the backend to process the AI analysis
        const timer = setTimeout(() => {
          fetchAiAnalysis(testResult.run_id);
        }, 3000);
        return () => clearTimeout(timer);
      }
    }
  }, [testResult, isExecuting]);

  return (
    <div className="container py-6 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Performance Testing</h1>
          {testResult?.test_details?.enhanced_workflow && (
            <div className="flex items-center mt-1">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                <div className="w-2 h-2 rounded-full bg-blue-500 mr-1"></div>
                Enhanced AI Workflow Active
              </span>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-sm flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${localDebugInfo?.healthCheck?.java_installed ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>Java: {localDebugInfo?.healthCheck?.java_installed ? 'OK' : 'Not Found'}</span>
          </div>
          <div className="text-sm flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${localDebugInfo?.healthCheck?.jmeter_server_running || localDebugInfo?.healthCheck?.jmeter_port_active ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span>JMeter: {localDebugInfo?.healthCheck?.jmeter_server_running || localDebugInfo?.healthCheck?.jmeter_port_active ? 'Running' : 'Not Found'}</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={checkServerHealth}
          >
            Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="configuration">
        <TabsList>
          <TabsTrigger value="configuration">Configuration</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="ai-analysis">AI Analysis</TabsTrigger>
          <TabsTrigger value="debug">Debug Info</TabsTrigger>
        </TabsList>
        
        <TabsContent value="configuration" className="space-y-4">
          {/* Enhanced Workflow Info Banner */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <div className="w-5 h-5 text-blue-500">ⓘ</div>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Enhanced AI Performance Testing</h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    This system uses an enhanced AI workflow powered by LangGraph for more intelligent test orchestration and analysis.
                    When available, you'll see additional insights and recommendations in the results.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Test Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Test Case</label>
                  <Input 
                    value={selectedTestCase} 
                    onChange={(e) => setSelectedTestCase(e.target.value)} 
                    placeholder="Enter test case ID or name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">URL</label>
                  <Input 
                    value={url} 
                    onChange={(e) => setUrl(e.target.value)} 
                    placeholder="https://example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Test Type</label>
                  <Select value={testType} onValueChange={setTestType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select test type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="load">Load Test</SelectItem>
                      <SelectItem value="stress">Stress Test</SelectItem>
                      <SelectItem value="spike">Spike Test</SelectItem>
                      <SelectItem value="endurance">Endurance Test</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Load Pattern</label>
                  <Select value={loadPattern} onValueChange={setLoadPattern}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select load pattern" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ramp_up">Ramp Up</SelectItem>
                      <SelectItem value="steady">Steady State</SelectItem>
                      <SelectItem value="spike">Spike</SelectItem>
                      <SelectItem value="endurance">Endurance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Advanced Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Concurrent Users</label>
                  <Input 
                    type="number" 
                    value={concurrentUsers} 
                    onChange={(e) => setConcurrentUsers(parseInt(e.target.value))} 
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Duration (seconds)</label>
                  <Input 
                    type="number" 
                    value={duration} 
                    onChange={(e) => setDuration(parseInt(e.target.value))} 
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Ramp-up Time (seconds)</label>
                  <Input 
                    type="number" 
                    value={rampUpTime} 
                    onChange={(e) => setRampUpTime(parseInt(e.target.value))} 
                  />
                </div>
              </CardContent>
            </Card>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Response Time Threshold (ms)</CardTitle>
            </CardHeader>
            <CardContent>
              <Input 
                type="number" 
                value={thresholds.response_time} 
                onChange={(e) => setThresholds({...thresholds, response_time: parseInt(e.target.value)})} 
              />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>95th Percentile Threshold (ms)</CardTitle>
            </CardHeader>
            <CardContent>
              <Input 
                type="number" 
                value={thresholds.max_95th_percentile} 
                onChange={(e) => setThresholds({...thresholds, max_95th_percentile: parseInt(e.target.value)})} 
              />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Error Rate Threshold (%)</CardTitle>
            </CardHeader>
            <CardContent>
              <Input 
                type="number" 
                value={thresholds.error_rate} 
                onChange={(e) => setThresholds({...thresholds, error_rate: parseInt(e.target.value)})} 
              />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Throughput Threshold (req/sec)</CardTitle>
            </CardHeader>
            <CardContent>
              <Input 
                type="number" 
                value={thresholds.throughput} 
                onChange={(e) => setThresholds({...thresholds, throughput: parseInt(e.target.value)})} 
              />
            </CardContent>
          </Card>
          
          <Button 
            onClick={handleExecuteTest} 
            disabled={isExecuting}
            className="w-full"
          >
            {isExecuting ? (
              <>
                <span className="mr-2">
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                Running Performance Analysis...
              </>
            ) : (
              "Run Performance Test"
            )}
          </Button>
        </TabsContent>
        
        <TabsContent value="results">
          {isExecuting ? (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p>Running performance test...</p>
                {/* Show enhanced workflow indicator during execution */}
                {debugInfo?.rawResponse?.enhanced_workflow && (
                  <div className="mt-4 p-3 bg-blue-100 rounded-lg">
                    <div className="flex items-center justify-center">
                      <div className="w-3 h-3 rounded-full bg-blue-500 mr-2 animate-pulse"></div>
                      <span className="font-medium text-blue-800">Enhanced AI Workflow Active</span>
                    </div>
                    <p className="text-sm text-blue-600 mt-1">Powered by LangGraph orchestration</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : errorMessage ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-red-500">Error</CardTitle>
              </CardHeader>
              <CardContent className="p-8">
                <p>{errorMessage}</p>
                <p className="mt-4 text-sm text-muted-foreground">Please check the Debug tab for technical details.</p>
              </CardContent>
            </Card>
          ) : testResult ? (
            <div className="space-y-6">
              {/* Enhanced Workflow Indicator */}
              {testResult?.test_details?.enhanced_workflow && (
                <Card className="border-blue-200 bg-blue-50">
                  <CardContent className="p-4">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-blue-500 mr-3"></div>
                      <div>
                        <span className="font-medium text-blue-800">Enhanced AI Workflow</span>
                        <span className="text-sm text-blue-600 ml-2">(Powered by LangGraph)</span>
                      </div>
                    </div>
                    {testResult.test_details.workflow_status && (
                      <div className="text-sm text-blue-600 mt-1">
                        Status: {testResult.test_details.workflow_status}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{testResult.metrics?.page_load_time || 0}ms</div>
                    <p className="text-xs text-muted-foreground">Avg Response Time</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{testResult.metrics?.largest_contentful_paint || 0}ms</div>
                    <p className="text-xs text-muted-foreground">95th Percentile</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{(testResult.metrics?.cumulative_layout_shift || 0) * 100}%</div>
                    <p className="text-xs text-muted-foreground">Error Rate</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{testResult.metrics?.network_requests || 0}</div>
                    <p className="text-xs text-muted-foreground">Throughput (req/min)</p>
                  </CardContent>
                </Card>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{testResult.test_details?.cpu_usage || 0}%</div>
                    <p className="text-xs text-muted-foreground">CPU Usage</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{formatBytes(testResult.test_details?.memory_usage || 0)}</div>
                    <p className="text-xs text-muted-foreground">Memory Usage</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{testResult.test_details?.total_requests || 0}</div>
                    <p className="text-xs text-muted-foreground">Total Requests</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{testResult.test_details?.failed_requests || 0}</div>
                    <p className="text-xs text-muted-foreground">Failed Requests</p>
                  </CardContent>
                </Card>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Response Time Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart
                        data={(testResult.test_details?.time_series?.timestamps || testResult.test_details?.time_series_data?.timestamps) ? 
                          (testResult.test_details?.time_series?.timestamps || testResult.test_details?.time_series_data?.timestamps).map((ts: string, i: number) => ({
                            time: new Date(ts).toLocaleTimeString(),
                            response_time: (testResult.test_details?.time_series?.response_times || testResult.test_details?.time_series_data?.response_times)[i]
                          })) : []}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="response_time" stroke="#8884d8" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Error Rate Over Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart
                        data={(testResult.test_details?.time_series?.timestamps || testResult.test_details?.time_series_data?.timestamps) ? 
                          (testResult.test_details?.time_series?.timestamps || testResult.test_details?.time_series_data?.timestamps).map((ts: string, i: number) => ({
                            time: new Date(ts).toLocaleTimeString(),
                            error_rate: (testResult.test_details?.time_series?.error_rate_series || testResult.test_details?.time_series_data?.error_rate_series)[i]
                          })) : []}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="error_rate" stroke="#82ca9d" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Throughput Over Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={(testResult.test_details?.time_series?.timestamps || testResult.test_details?.time_series_data?.timestamps) ? 
                          (testResult.test_details?.time_series?.timestamps || testResult.test_details?.time_series_data?.timestamps).map((ts: string, i: number) => ({
                            time: new Date(ts).toLocaleTimeString(),
                            throughput: (testResult.test_details?.time_series?.throughput_series || testResult.test_details?.time_series_data?.throughput_series)[i]
                          })) : []}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="throughput" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Resource Usage</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-2xl font-bold">{formatBytes(testResult.metrics?.total_bytes || 0)}</div>
                        <p className="text-xs text-muted-foreground">Total Bytes</p>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{testResult.metrics?.dom_elements || 0}</div>
                        <p className="text-xs text-muted-foreground">DOM Elements</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* JMeter Report Link */}
              {testResult.test_details && testResult.test_details.detailed_reports && (
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Reports</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6 flex flex-wrap justify-between items-center gap-4">
                    <a 
                      href={`http://127.0.0.1:8002${testResult.test_details.detailed_reports.executive_html}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-blue-500 hover:underline"
                    >
                      <BarChart3 className="h-4 w-4" />
                      View Full JMeter Report
                    </a>
                    <a 
                      href={`http://127.0.0.1:8002${testResult.test_details.detailed_reports?.dashboard_html || testResult.test_details.detailed_reports.executive_html}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-blue-500 hover:underline"
                    >
                      <BarChart3 className="h-4 w-4" />
                      View Dashboard Report
                    </a>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={exportToExcel}
                      className="ml-auto"
                    >
                      Export to Excel
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground">No test results yet. Run a test to see results here.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        {/* History Tab */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Test History</CardTitle>
              <CardDescription>Previous performance test runs</CardDescription>
            </CardHeader>
            <CardContent>
              {testHistory.length > 0 ? (
                <div className="overflow-auto max-h-[600px]">
                  <table className="w-full border-collapse">
                    <thead className="bg-slate-100">
                      <tr>
                        <th className="p-2 text-left">Test Name</th>
                        <th className="p-2 text-left">Type</th>
                        <th className="p-2 text-right">Avg Response</th>
                        <th className="p-2 text-right">Error Rate</th>
                        <th className="p-2 text-right">Throughput</th>
                        <th className="p-2 text-right">Date</th>
                        <th className="p-2 text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {testHistory.map((run: any) => (
                        <tr key={run.run_id} className="border-b border-gray-200">
                          <td className="p-2">{run.test_name}</td>
                          <td className="p-2">{run.test_type}</td>
                          <td className="p-2 text-right">{run.avg_response_time || 0}ms</td>
                          <td className="p-2 text-right">{run.error_rate || 0}%</td>
                          <td className="p-2 text-right">{run.throughput || 0}/min</td>
                          <td className="p-2 text-right">{new Date(run.created_at).toLocaleString()}</td>
                          <td className="p-2 text-center">
                            <div className="flex justify-center space-x-2">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => fetchAiAnalysis(run.run_id)}
                              >
                                View AI Analysis
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-center text-muted-foreground">No test history available.</p>
              )}
              <div className="mt-4 flex justify-end">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={fetchHistory}
                >
                  Refresh History
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* AI Analysis Tab */}
        <TabsContent value="ai-analysis">
          <Card>
            <CardHeader>
              <CardTitle>AI Performance Analysis</CardTitle>
              <CardDescription>
                {selectedRunId ? `Analysis for test run: ${selectedRunId}` : "Select a test run to view AI analysis"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Enhanced Workflow AI Insights Indicator */}
              {testResult?.test_details?.enhanced_workflow && testResult?.test_details?.ai_insights && (
                <div className="mb-4 p-3 bg-purple-100 rounded-lg border border-purple-300">
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
                    <span className="font-medium text-purple-800">Enhanced AI Insights Available</span>
                  </div>
                  <p className="text-sm text-purple-600 mt-1">
                    Generated by LangGraph-powered workflow with advanced analysis capabilities
                  </p>
                </div>
              )}
              
              {!aiAnalysis ? (
                <div className="text-center p-4">
                  <p className="text-muted-foreground">
                    {selectedRunId ? "Loading analysis..." : "No analysis selected. View a test from the History tab."}
                  </p>
                </div>
              ) : aiAnalysis.error ? (
                <div className="p-4 border border-red-200 rounded bg-red-50">
                  <p className="text-red-500">{aiAnalysis.error}</p>
                  <p className="mt-2 text-sm text-muted-foreground">
                    AI analysis may take a few minutes to complete after a test run.
                    Try refreshing in a moment.
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Show enhanced workflow AI insights if available */}
                  {testResult?.test_details?.enhanced_workflow && testResult?.test_details?.ai_insights && (
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-lg font-medium">AI Performance Score</h3>
                        <div className="text-3xl font-bold text-purple-600">
                          {testResult.test_details.ai_insights.performance_score || 'N/A'}/100
                        </div>
                      </div>
                      
                      {testResult.test_details.ai_insights.executive_summary && (
                        <div>
                          <h3 className="text-lg font-medium">Executive Summary</h3>
                          <div className="p-3 bg-gray-50 rounded">
                            <p className="text-gray-700">{testResult.test_details.ai_insights.executive_summary}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Bottlenecks</h3>
                    {aiAnalysis.bottlenecks && aiAnalysis.bottlenecks.length > 0 ? (
                      <ul className="list-disc pl-5 space-y-2">
                        {aiAnalysis.bottlenecks.map((item: string, index: number) => (
                          <li key={index} className="text-red-600">{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground">No bottlenecks identified.</p>
                    )}
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Recommendations</h3>
                    {aiAnalysis.recommendations && aiAnalysis.recommendations.length > 0 ? (
                      <ul className="list-disc pl-5 space-y-2">
                        {aiAnalysis.recommendations.map((item: string, index: number) => (
                          <li key={index} className="text-green-600">{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground">No recommendations available.</p>
                    )}
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Suggested Next Tests</h3>
                    {aiAnalysis.next_tests && aiAnalysis.next_tests.length > 0 ? (
                      <ul className="list-disc pl-5 space-y-2">
                        {aiAnalysis.next_tests.map((item: string, index: number) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground">No suggested tests available.</p>
                    )}
                  </div>
                  
                  {aiAnalysis.full_report && (
                    <div className="pt-4 border-t border-gray-200">
                      <details>
                        <summary className="cursor-pointer text-lg font-medium mb-2">Full Analysis Report</summary>
                        <div className="p-4 bg-slate-50 rounded text-sm whitespace-pre-wrap">
                          {aiAnalysis.full_report}
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Debug Tab */}
        <TabsContent value="debug">
          <Card>
            <CardHeader>
              <CardTitle>Debug Information</CardTitle>
              <CardDescription>Technical details for troubleshooting</CardDescription>
            </CardHeader>
            <CardContent>
              {isExecuting ? (
                <div className="text-center p-4">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p>Executing performance test...</p>
                </div>
              ) : debugInfo || localDebugInfo ? (
                <div className="space-y-4">
                  {/* Enhanced Workflow Debug Information */}
                  {debugInfo?.rawResponse?.enhanced_workflow && (
                    <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h3 className="text-md font-medium mb-2 text-blue-800">Enhanced AI Workflow (LangGraph)</h3>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="bg-blue-100 p-2 rounded">
                          <div className="font-medium">Workflow Status</div>
                          <div className="text-sm text-blue-700">
                            {debugInfo.rawResponse.workflow_status || 'Active'}
                          </div>
                        </div>
                        <div className="bg-blue-100 p-2 rounded">
                          <div className="font-medium">AI Insights</div>
                          <div className="text-sm text-blue-700">
                            {debugInfo.rawResponse.ai_insights ? 'Available' : 'Processing...'}
                          </div>
                        </div>
                      </div>
                      {debugInfo.rawResponse.next_actions && (
                        <div className="mt-2">
                          <div className="font-medium text-sm">Next Recommended Actions:</div>
                          <ul className="list-disc pl-5 text-sm text-blue-700">
                            {debugInfo.rawResponse.next_actions.slice(0, 3).map((action: string, index: number) => (
                              <li key={index}>{action}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div>
                    <h3 className="text-md font-medium mb-2">Structure Check</h3>
                    {debugInfo?.structureCheck && (
                      <div className="grid grid-cols-2 gap-2 mb-4">
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">Has Result</div>
                          <div className={`text-sm ${debugInfo.structureCheck.hasResult ? 'text-green-500' : 'text-red-500'}`}>
                            {debugInfo.structureCheck.hasResult ? 'Yes' : 'No'}
                          </div>
                        </div>
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">Has Test Details</div>
                          <div className={`text-sm ${debugInfo.structureCheck.hasTestDetails ? 'text-green-500' : 'text-red-500'}`}>
                            {debugInfo.structureCheck.hasTestDetails ? 'Yes' : 'No'}
                          </div>
                        </div>
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">Has Time Series</div>
                          <div className={`text-sm ${debugInfo.structureCheck.hasTimeSeries ? 'text-green-500' : 'text-red-500'}`}>
                            {debugInfo.structureCheck.hasTimeSeries ? 'Yes' : 'No'}
                          </div>
                        </div>
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">Has Timestamps</div>
                          <div className={`text-sm ${debugInfo.structureCheck.hasTimestamps ? 'text-green-500' : 'text-red-500'}`}>
                            {debugInfo.structureCheck.hasTimestamps ? 'Yes' : 'No'}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {localDebugInfo?.healthCheck && (
                    <div className="mb-4">
                      <h3 className="text-md font-medium mb-2">Health Check</h3>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">Java</div>
                          <div className={`text-sm ${localDebugInfo.healthCheck.java_installed ? 'text-green-500' : 'text-red-500'}`}>
                            {localDebugInfo.healthCheck.java_installed ? 'Installed' : 'Not Installed'}
                          </div>
                        </div>
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">JMeter</div>
                          <div className={`text-sm ${localDebugInfo.healthCheck.jmeter_in_path || localDebugInfo.healthCheck.custom_jmeter_exists ? 'text-green-500' : 'text-red-500'}`}>
                            {localDebugInfo.healthCheck.jmeter_in_path || localDebugInfo.healthCheck.custom_jmeter_exists ? 'Installed' : 'Not Installed'}
                          </div>
                        </div>
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">JMeter Server Status</div>
                          <div className={`text-sm ${localDebugInfo.healthCheck.jmeter_server_running || localDebugInfo.healthCheck.jmeter_port_active ? 'text-green-500' : 'text-red-500'}`}>
                            {localDebugInfo.healthCheck.jmeter_server_running || localDebugInfo.healthCheck.jmeter_port_active ? 'Running' : 'Not Running'}
                          </div>
                        </div>
                        <div className="bg-slate-100 p-2 rounded">
                          <div className="font-medium">JMeter Port (50000)</div>
                          <div className={`text-sm ${localDebugInfo.healthCheck.jmeter_port_active ? 'text-green-500' : 'text-red-500'}`}>
                            {localDebugInfo.healthCheck.jmeter_port_active ? 'Active' : 'Inactive'}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <h3 className="text-md font-medium mb-2">Raw Response</h3>
                  <pre className="bg-slate-100 p-4 rounded overflow-auto max-h-[600px] text-xs">
                    {JSON.stringify({
                      ...debugInfo?.rawResponse,
                      ...localDebugInfo,
                    }, null, 2)}
                  </pre>
                </div>
              ) : (
                <p className="text-muted-foreground">No debug information available. Run a test to see details.</p>
              )}
              
              <div className="mt-6 space-y-4">
                <h3 className="text-lg font-medium">Backend Connection</h3>
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-slate-100 p-2 rounded">
                    <div className="font-medium">API URL</div>
                    <div className="text-sm">http://127.0.0.1:8002/run-performance-test</div>
                  </div>
                    <div className="bg-slate-100 p-2 rounded">
                      <div className="font-medium">JMeter Server Status</div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={async () => {
                          const healthData = await checkServerHealth()
                          if (healthData) {
                            setLocalDebugInfo(prevInfo => ({
                              ...prevInfo,
                              healthCheck: healthData
                            }))
                            
                            toast({
                              title: "Server Status",
                              description: `Server is ${healthData.status || 'unknown'}. Java: ${healthData.java_installed ? 'OK' : 'Not Found'}. JMeter: ${healthData.jmeter_server_running ? 'Running' : 'Not Running'}`,
                            })
                          } else {
                            toast({
                              title: "Server Unreachable",
                              description: "Cannot connect to the backend server",
                              variant: "destructive",
                            })
                          }
                        }}
                      >
                        Check Server
                      </Button>
                    </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      {/* Server Status Dialog */}
      {localDebugInfo?.healthCheck?.jmeter_server_running === false && localDebugInfo?.healthCheck?.jmeter_port_active === false && (
        <div className="fixed bottom-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded shadow-lg z-50">
          <div className="flex items-center">
            <div className="py-1"><svg className="fill-current h-6 w-6 text-yellow-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM9 11V9h2v6H9v-4zm0-6h2v2H9V5z"/></svg></div>
            <div>
              <p className="font-bold">JMeter Server Not Running</p>
              <p className="text-sm">Performance tests require JMeter server to be running. Run the start-jmeter.bat script.</p>
              <div className="mt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    await checkServerHealth()
                    toast({
                      title: "Server Status Checked",
                      description: "Server status has been refreshed."
                    })
                  }}
                >
                  Refresh Status
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Performance