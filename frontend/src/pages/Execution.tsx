import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useTestExecutions, TestExecution } from "@/hooks/useTestExecutions"
import { Loader2, AlertTriangle, CheckCircle, XCircle, ClockIcon, RefreshCw, FileText, Clock } from "lucide-react"

const Execution = () => {
  const [activeTab, setActiveTab] = useState<string>("all")
  const { executions, loading, error, fetchExecutions, clearExecutionHistory } = useTestExecutions()
  
  const filterExecutions = (status?: string): TestExecution[] => {
    if (!status || status === "all") {
      return executions
    }
    return executions.filter(execution => execution.result === status)
  }

  const getStatusIcon = (execution: TestExecution) => {
    if (execution.status === "running") {
      return <Loader2 className="h-4 w-4 animate-spin text-primary" />
    }
    
    switch (execution.result) {
      case "pass":
        return <CheckCircle className="h-4 w-4 text-success" />
      case "fail":
        return <XCircle className="h-4 w-4 text-destructive" />
      case "error":
        return <AlertTriangle className="h-4 w-4 text-destructive" />
      case "skipped":
        return <ClockIcon className="h-4 w-4 text-muted-foreground" />
      default:
        return <FileText className="h-4 w-4 text-primary" />
    }
  }

  const getStatusColor = (execution: TestExecution) => {
    if (execution.status === "running") {
      return "bg-primary text-primary-foreground"
    }
    
    switch (execution.result) {
      case "pass":
        return "bg-success text-success-foreground"
      case "fail":
      case "error":
        return "bg-destructive text-destructive-foreground"
      case "skipped":
        return "bg-muted text-muted-foreground"
      default:
        return "bg-primary text-primary-foreground"
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const handleRefresh = () => {
    fetchExecutions(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Test Execution</h1>
          <p className="text-muted-foreground">
            Real-time test execution monitoring and results
            <span className="text-xs ml-2">(Showing up to 10 most recent executions)</span>
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button 
            variant="destructive" 
            onClick={clearExecutionHistory}
            disabled={executions.length === 0}
          >
            Clear History ({executions.length})
          </Button>
        </div>
      </div>

      <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All Executions</TabsTrigger>
          <TabsTrigger value="pass">Passed</TabsTrigger>
          <TabsTrigger value="fail">Failed</TabsTrigger>
          <TabsTrigger value="running">Running</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="space-y-4 mt-4">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <span className="ml-2 text-muted-foreground">Loading executions...</span>
            </div>
          ) : error ? (
            <div className="text-center p-8">
              <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-2" />
              <p className="text-destructive">{error}</p>
              <Button onClick={handleRefresh} variant="outline" className="mt-2">
                Try Again
              </Button>
            </div>
          ) : filterExecutions(activeTab === "running" ? "running" : activeTab).length === 0 ? (
            <div className="text-center p-8">
              <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">
                No {activeTab === "all" ? "" : activeTab + " "} test executions found.
              </p>
            </div>
          ) : (
            filterExecutions(activeTab === "running" ? "running" : activeTab).map((execution) => (
              <Card key={execution.id} className="overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">
                        {execution.test_case.title}
                      </CardTitle>
                      <CardDescription>{execution.test_case.description}</CardDescription>
                    </div>
                    
                    <Badge className={getStatusColor(execution)}>
                      {execution.status === "running" ? "Running" : (execution.result || "Unknown")}
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Start Time:</span>
                      <span className="ml-2">{formatDate(execution.start_time)}</span>
                    </div>
                    
                    {execution.end_time && (
                      <div>
                        <span className="text-muted-foreground">End Time:</span>
                        <span className="ml-2">{formatDate(execution.end_time)}</span>
                      </div>
                    )}
                    
                    {execution.execution_time !== undefined && (
                      <div>
                        <span className="text-muted-foreground">Duration:</span>
                        <span className="ml-2">{execution.execution_time} seconds</span>
                      </div>
                    )}
                    
                    <div>
                      <span className="text-muted-foreground">Test Type:</span>
                      <span className="ml-2">{execution.test_case.test_type}</span>
                    </div>
                  </div>
                  
                  {execution.error_message && (
                    <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm">
                      <div className="font-medium text-destructive mb-1">Error:</div>
                      <div className="text-muted-foreground">{execution.error_message}</div>
                    </div>
                  )}
                  
                  {execution.logs && execution.logs.length > 0 && (
                    <div className="mt-4">
                      <div className="font-medium mb-2">Execution Logs:</div>
                      <div className="bg-muted p-3 rounded-md text-xs font-mono h-40 overflow-y-auto">
                        {execution.logs.map((log, index) => (
                          <div key={index} className="py-1 border-b border-border/20 last:border-0">
                            {log}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mt-4">
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Clock className="h-4 w-4 mr-1" />
                      <span>
                        {execution.status === "running" 
                          ? "Execution in progress..." 
                          : `Executed ${new Date(execution.start_time).toLocaleDateString()}`
                        }
                      </span>
                    </div>
                    
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Execution