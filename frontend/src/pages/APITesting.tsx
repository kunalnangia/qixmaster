import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Globe, Loader2, Play, CheckCircle, XCircle } from 'lucide-react'
import { useTesting } from '@/hooks/useTesting'
import TestCaseSelector from '@/components/shared/TestCaseSelector'
import { useToast } from '@/hooks/use-toast'

const APITesting = () => {
  const [selectedTestCase, setSelectedTestCase] = useState('')
  const [apiConfig, setApiConfig] = useState({
    endpoint: '',
    method: 'GET',
    headers: {},
    body: null,
    expected_status: 200,
    expected_response: null
  })
  const [newmanConfig, setNewmanConfig] = useState({
    collectionUrl: '',
    apiKey: '',
    environment: ''
  })
  const [testResult, setTestResult] = useState<any>(null)
  const [headerInput, setHeaderInput] = useState('')
  const [bodyInput, setBodyInput] = useState('')
  const [activeTab, setActiveTab] = useState('configure')

  const { executeApiTest, executeNewmanTest, isExecuting } = useTesting()
  const { toast } = useToast()

  const handleExecuteTest = async () => {
    if (!selectedTestCase || !apiConfig.endpoint) {
      toast({
        title: "Missing Information",
        description: "Please select a test case and enter an API endpoint",
        variant: "destructive",
      })
      return
    }

    // Parse headers
    let headers = {}
    if (headerInput.trim()) {
      try {
        headers = JSON.parse(headerInput)
      } catch {
        // Try parsing as key:value pairs
        headerInput.split('\n').forEach(line => {
          const [key, value] = line.split(':').map(s => s.trim())
          if (key && value) {
            headers[key] = value
          }
        })
      }
    }

    // Parse body
    let body = null
    if (bodyInput.trim() && apiConfig.method !== 'GET') {
      try {
        body = JSON.parse(bodyInput)
      } catch {
        body = bodyInput
      }
    }

    const config = {
      ...apiConfig,
      headers,
      body,
      expected_response: apiConfig.expected_response ? JSON.parse(apiConfig.expected_response) : null
    }

    try {
      const result = await executeApiTest(selectedTestCase, config)
      setTestResult(result)
      setActiveTab('results')
    } catch (error) {
      console.error('Error executing API test:', error)
    }
  }

  const handleExecuteNewmanTest = async () => {
    if (!newmanConfig.collectionUrl || !newmanConfig.apiKey) {
      toast({
        title: "Missing Information",
        description: "Please enter both Collection URL and API Key",
        variant: "destructive",
      })
      return
    }

    try {
      const result = await executeNewmanTest(
        newmanConfig.collectionUrl,
        newmanConfig.apiKey,
        selectedTestCase,
        newmanConfig.environment ? JSON.parse(newmanConfig.environment) : null
      )
      setTestResult(result)
      setActiveTab('results')
    } catch (error) {
      console.error('Error executing Newman test:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">API Testing</h1>
        <p className="text-muted-foreground">Test REST APIs with comprehensive validation</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="configure">Configure Test</TabsTrigger>
          <TabsTrigger value="newman">Newman Test</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="configure" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                API Test Configuration
              </CardTitle>
              <CardDescription>
                Configure your API test parameters and validation criteria
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Test Case</label>
                <TestCaseSelector
                  value={selectedTestCase}
                  onValueChange={setSelectedTestCase}
                  testType="api"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">HTTP Method</label>
                  <Select value={apiConfig.method} onValueChange={(value) => setApiConfig({...apiConfig, method: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GET">GET</SelectItem>
                      <SelectItem value="POST">POST</SelectItem>
                      <SelectItem value="PUT">PUT</SelectItem>
                      <SelectItem value="PATCH">PATCH</SelectItem>
                      <SelectItem value="DELETE">DELETE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Expected Status Code</label>
                  <Input
                    type="number"
                    value={apiConfig.expected_status}
                    onChange={(e) => setApiConfig({...apiConfig, expected_status: parseInt(e.target.value)})}
                    placeholder="200"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">API Endpoint</label>
                <Input
                  value={apiConfig.endpoint}
                  onChange={(e) => setApiConfig({...apiConfig, endpoint: e.target.value})}
                  placeholder="https://api.example.com/users"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Headers (JSON or key:value per line)</label>
                <Textarea
                  value={headerInput}
                  onChange={(e) => setHeaderInput(e.target.value)}
                  placeholder={'Authorization: Bearer token\nContent-Type: application/json'}
                  rows={3}
                />
              </div>

              {apiConfig.method !== 'GET' && (
                <div>
                  <label className="text-sm font-medium">Request Body (JSON)</label>
                  <Textarea
                    value={bodyInput}
                    onChange={(e) => setBodyInput(e.target.value)}
                    placeholder='{"name": "John Doe", "email": "john@example.com"}'
                    rows={4}
                  />
                </div>
              )}

              <Button 
                onClick={handleExecuteTest} 
                disabled={isExecuting || !selectedTestCase || !apiConfig.endpoint}
                className="w-full"
              >
                {isExecuting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running API Test...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Execute API Test
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="newman" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Newman Test Configuration
              </CardTitle>
              <CardDescription>
                Run Postman collections using Newman via Docker
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Test Case</label>
                <TestCaseSelector
                  value={selectedTestCase}
                  onValueChange={setSelectedTestCase}
                  testType="api"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Collection URL</label>
                <Input
                  value={newmanConfig.collectionUrl}
                  onChange={(e) => setNewmanConfig({...newmanConfig, collectionUrl: e.target.value})}
                  placeholder="47463989-8d6cec84-fb64-48dc-8d71-7c2e6ba45c28"
                />
              </div>

              <div>
                <label className="text-sm font-medium">API Key</label>
                <Input
                  value={newmanConfig.apiKey}
                  onChange={(e) => setNewmanConfig({...newmanConfig, apiKey: e.target.value})}
                  placeholder="PMAK-68bc06cf8e88740001889312-b50afdd3066958a44f1a7d8ed5e48cf10d"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Environment Variables (JSON)</label>
                <Textarea
                  value={newmanConfig.environment}
                  onChange={(e) => setNewmanConfig({...newmanConfig, environment: e.target.value})}
                  placeholder='{ "base_url": "https://postman-echo.com", "api_key": "your-api-key" }'
                  rows={4}
                />
              </div>

              <Button 
                onClick={handleExecuteNewmanTest} 
                disabled={isExecuting || !newmanConfig.collectionUrl || !newmanConfig.apiKey}
                className="w-full"
              >
                {isExecuting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Newman Test...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Execute Newman Test
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results">
          {testResult ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {testResult.success ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  Test Results
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Status Code</label>
                    <div className="flex items-center gap-2">
                      <Badge variant={testResult.validation?.status_match ? "default" : "destructive"}>
                        {testResult.status}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        Expected: {testResult.expected_status}
                      </span>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Response Time</label>
                    <p className="text-sm">{testResult.duration}ms</p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Response Body</label>
                  <pre className="bg-muted p-3 rounded text-xs overflow-auto max-h-48">
                    {JSON.stringify(testResult.response, null, 2)}
                  </pre>
                </div>

                {testResult.validation && (
                  <div>
                    <label className="text-sm font-medium">Validation Results</label>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge variant={testResult.validation.status_match ? "default" : "destructive"}>
                          Status {testResult.validation.status_match ? "✓" : "✗"}
                        </Badge>
                        <Badge variant={testResult.validation.response_match ? "default" : "destructive"}>
                          Response {testResult.validation.response_match ? "✓" : "✗"}
                        </Badge>
                      </div>
                    </div>
                  </div>
                )}

                {testResult.error && (
                  <div>
                    <label className="text-sm font-medium text-red-500">Error</label>
                    <p className="text-sm text-red-500">{testResult.error}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground">No test results yet. Run a test to see results here.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default APITesting