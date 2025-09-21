import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { AIGenerateDialog } from "@/components/ui/ai-generate-dialog"
import { useTestCases, TestCase } from "@/hooks/useTestCases"
import { useTestExecutions } from "@/hooks/useTestExecutions"
import { useNavigate } from "react-router-dom"
// import { useProjects } from "@/hooks/useProjects"
import { 
  Search,
  Plus,
  FileText,
  Play,
  Edit,
  MessageSquare,
  Brain,
  Sparkles,
  Filter,
  MoreHorizontal,
  CheckCircle,
  Clock,
  AlertTriangle,
  Loader2,
  Check,
  X,
  Upload,
  Link,
  Download,
  ExternalLink,
  Import
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from "@/components/ui/popover"
import { Checkbox } from "@/components/ui/checkbox"
import TestCaseForm from "@/components/test-cases/TestCaseForm"

// Type for filter options
interface FilterOptions {
  testType: string[];
  priority: string[];
  status: string[];
  tags: string[];
}

// Type for comment
interface Comment {
  id: number;
  user: string;
  message: string;
  time: string;
  type: string;
}

const TestCases = () => {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedTest, setSelectedTest] = useState<string | null>(null)
  const [showComments, setShowComments] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [isNewTestOpen, setIsNewTestOpen] = useState(false)
  const [isEditTestOpen, setIsEditTestOpen] = useState(false)
  const [isImportTestOpen, setIsImportTestOpen] = useState(false)
  const [currentTestToEdit, setCurrentTestToEdit] = useState<TestCase | null>(null)
  const [newComment, setNewComment] = useState("")
  const [allComments, setAllComments] = useState<Comment[]>([])
  const [showFilterPopover, setShowFilterPopover] = useState(false)
  const [filters, setFilters] = useState<FilterOptions>({
    testType: [],
    priority: [],
    status: [],
    tags: []
  })
  
  // Import test case data
  const [importData, setImportData] = useState({
    importType: "url", // url, file, mcp, jira, trello
    url: "",
    filePath: "Downloads\\performance_test_1_2025-08-30T09-07-37.xlsx",
    connection: "rebe.app",
    username: "",
    password: "",
    project: "",
    generateEdgeCases: false,
    droppedFileName: "" // Store the name of dropped file for display
  })
  
  // Drag and drop state
  const [isDragging, setIsDragging] = useState(false)
  
  const { toast } = useToast()
  
  // For now, use a hardcoded project ID - in production this should come from routing or user context
  const currentProjectId = "default-project-id"
  
  const { testCases, loading, error, refetch, createTestCase, updateTestCase } = useTestCases(currentProjectId)
  const { executeTest } = useTestExecutions(currentProjectId)
  // Commenting out projects for now to simplify
  // const { projects } = useProjects()
  
  // Use the hardcoded project ID for AI generation
  const projectId = currentProjectId
  
  // Initial comments data
  const initialComments = [
    {
      id: 1,
      user: "Sarah Johnson",
      message: "The payment timeout scenario needs more edge cases",
      time: "10 minutes ago",
      type: "feedback"
    },
    {
      id: 2,
      user: "AI Assistant",
      message: "Auto-healing detected element selector change. Test updated automatically.",
      time: "25 minutes ago",
      type: "system"
    },
    {
      id: 3,
      user: "Mike Chen",
      message: "Should we add tests for different currencies?",
      time: "1 hour ago",
      type: "question"
    }
  ];
  
  useEffect(() => {
    // Set initial comments from the sample data
    setAllComments(initialComments)
  }, [])
  
  // Apply filters to test cases
  const applyFilters = (test) => {
    if (filters.testType.length > 0 && !filters.testType.includes(test.test_type)) return false
    if (filters.priority.length > 0 && !filters.priority.includes(test.priority)) return false
    if (filters.status.length > 0 && !filters.status.includes(test.status)) return false
    if (filters.tags.length > 0 && !filters.tags.some(tag => test.tags?.includes(tag))) return false
    return true
  }
  
  // Filter test cases based on search term and filters
  const filteredTestCases = testCases.filter(testCase => 
    (testCase.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
     testCase.description?.toLowerCase().includes(searchTerm.toLowerCase())) &&
    applyFilters(testCase)
  )
  
  // Handle AI Generate callback
  const handleAIGenerate = async (generatedTestCases: any[]) => {
    // Refresh the test cases list to show newly generated ones
    await refetch()
    
    toast({
      title: "Test Cases Generated",
      description: `Successfully generated ${generatedTestCases.length} test cases`,
    })
  }
  
  // Handle test case execution
  const executeTestCase = async (testId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setIsExecuting(true)
    
    try {
      // Find the test case
      const testCase = testCases.find(test => test.id === testId)
      if (!testCase) {
        throw new Error('Test case not found')
      }
      
      toast({
        title: "Test Execution Started",
        description: "Test case is being executed. Results will be available shortly.",
      })
      
      // Add a system comment about the execution
      const newExecutionComment = {
        id: Date.now(),
        user: "System",
        message: "Test execution started. Waiting for results...",
        time: "Just now",
        type: "system"
      }
      
      setAllComments(prev => [newExecutionComment, ...prev])
      
      // Execute the test using our hook
      const execution = await executeTest(testCase)
      
      // Update comment with result
      const resultComment = {
        id: Date.now(),
        user: "System",
        message: execution.result === 'pass' 
          ? "Test execution completed successfully." 
          : `Test execution ${execution.result}: ${execution.error_message || 'No details available'}`,
        time: "Just now",
        type: "system"
      }
      
      setAllComments(prev => [resultComment, ...prev])
      
      // Select the test to show execution details
      setSelectedTest(testId)
      
      // Navigate to the execution page
      navigate('/execution')
    } catch (error) {
      toast({
        title: "Execution Failed",
        description: error instanceof Error ? error.message : "Failed to execute test case. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsExecuting(false)
    }
  }
  
  // Handle creating a new test case
  const handleCreateTestCase = async (testData: Partial<TestCase>) => {
    try {
      const result = await createTestCase({
        ...testData,
        project_id: currentProjectId
      } as any)
      
      if (result.error) {
        throw new Error(result.error)
      }
      
      toast({
        title: "Test Case Created",
        description: "New test case has been successfully created",
      })
      
      // Add system comment about test case creation
      const newCreationComment = {
        id: Date.now(),
        user: "System",
        message: `New test case "${testData.title}" created`,
        time: "Just now",
        type: "system"
      }
      
      setAllComments(prev => [newCreationComment, ...prev])
      
      setIsNewTestOpen(false)
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: error instanceof Error ? error.message : "Failed to create test case",
        variant: "destructive"
      })
    }
  }
  
  // Handle editing a test case
  const handleEditTestCase = async (testId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    
    // Find the test case to edit
    const testToEdit = testCases.find(test => test.id === testId)
    if (!testToEdit) return
    
    setCurrentTestToEdit(testToEdit)
    setIsEditTestOpen(true)
  }
  
  // Handle updating a test case
  const handleUpdateTestCase = async (testData: Partial<TestCase>) => {
    if (!currentTestToEdit) return
    
    try {
      const result = await updateTestCase(currentTestToEdit.id, testData)
      
      if (result.error) {
        throw new Error(result.error)
      }
      
      toast({
        title: "Test Case Updated",
        description: "Test case has been successfully updated",
      })
      
      // Add system comment about test case update
      const newUpdateComment = {
        id: Date.now(),
        user: "System",
        message: `Test case "${testData.title}" was updated`,
        time: "Just now",
        type: "system"
      }
      
      setAllComments(prev => [newUpdateComment, ...prev])
      
      setCurrentTestToEdit(null)
      setIsEditTestOpen(false)
    } catch (error) {
      toast({
        title: "Update Failed",
        description: error instanceof Error ? error.message : "Failed to update test case",
        variant: "destructive"
      })
    }
  }
  
  // Handle adding a new comment
  const handleAddComment = () => {
    if (!newComment.trim()) return
    
    const comment = {
      id: Date.now(),
      user: "Current User", // In a real app, this would be the logged-in user
      message: newComment,
      time: "Just now",
      type: "feedback"
    }
    
    setAllComments(prev => [comment, ...prev])
    setNewComment("")
    
    toast({
      title: "Comment Added",
      description: "Your comment has been added to the discussion",
    })
  }
  
  // Handle drag events
  const handleDragOver = (e: React.DragEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }
  
  const handleDragEnter = (e: React.DragEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }
  
  const handleDragLeave = (e: React.DragEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }
  
  const handleDrop = (e: React.DragEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    // Process the dropped files
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]
      
      // Check if it's an Excel file
      if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        // Update the import data
        setImportData(prev => ({
          ...prev,
          importType: 'file',
          filePath: file.name,
          droppedFileName: file.name
        }))
        
        // Open the import dialog
        setIsImportTestOpen(true)
        
        toast({
          title: "Excel File Detected",
          description: `Ready to import test cases from ${file.name}`,
        })
      } else {
        toast({
          title: "Invalid File Type",
          description: "Please drop an Excel file (.xlsx or .xls)",
          variant: "destructive"
        })
      }
    }
  }
  
  // Handle importing test cases
  const handleImportTestCases = async () => {
    try {
      // Show a loading toast
      toast({
        title: "Importing Test Cases",
        description: "Processing your import request...",
      })
      
      // Depending on the import type, handle differently
      switch (importData.importType) {
        case "url":
          if (!importData.url) {
            throw new Error("Please enter a valid URL");
          }
          // TODO: Implement URL import functionality
          toast({
            title: "URL Import",
            description: "URL import functionality will be implemented soon",
          })
          break;
          
        case "file":
          if (!importData.filePath) {
            throw new Error("Please select a file to import");
          }
          // TODO: Implement file import functionality
          toast({
            title: "File Import",
            description: "Excel file import functionality will be implemented soon",
          })
          break;
          
        case "mcp":
        case "jira":
        case "trello":
          if (!importData.connection || !importData.username || !importData.password || !importData.project) {
            throw new Error("Please fill in all connection details");
          }
          // TODO: Implement integration import functionality
          toast({
            title: "Integration Import",
            description: "Integration import functionality will be implemented soon",
          })
          break;
          
        default:
          throw new Error("Invalid import type selected");
      }
      
      // Close the import dialog
      setIsImportTestOpen(false);
      
      // Reset the import data
      setImportData({
        importType: "url",
        url: "",
        filePath: "Downloads\\performance_test_1_2025-08-30T09-07-37.xlsx",
        connection: "rebe.app",
        username: "",
        password: "",
        project: "",
        generateEdgeCases: false,
        droppedFileName: ""
      });
      
      // Refresh the test cases list
      await refetch();
      
    } catch (error) {
      toast({
        title: "Import Failed",
        description: error instanceof Error ? error.message : "Failed to import test cases",
        variant: "destructive"
      })
    }
  }
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-success text-success-foreground"
      case "failing": return "bg-destructive text-destructive-foreground"
      case "pending": return "bg-warning text-warning-foreground"
      default: return "bg-muted text-muted-foreground"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "border-l-destructive"
      case "medium": return "border-l-warning"
      case "low": return "border-l-muted"
      default: return "border-l-border"
    }
  }

  const getAutomationBadge = (automation: string) => {
    switch (automation) {
      case "ai-generated":
        return <Badge variant="default" className="bg-gradient-primary"><Sparkles className="h-3 w-3 mr-1" />AI Generated</Badge>
      case "self-healing":
        return <Badge variant="secondary" className="bg-gradient-success"><Brain className="h-3 w-3 mr-1" />Self-Healing</Badge>
      default:
        return <Badge variant="outline">Manual</Badge>
    }
  }

  // Set available filters based on current test cases
  const availableTestTypes = [...new Set(testCases.map(test => test.test_type))]
  const availablePriorities = [...new Set(testCases.map(test => test.priority))]
  const availableStatuses = [...new Set(testCases.map(test => test.status))]
  const availableTags = [...new Set(testCases.flatMap(test => test.tags || []))]
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Test Cases</h1>
          <p className="text-muted-foreground mt-1">
            Manage and execute your test cases with AI assistance
          </p>
        </div>
        
        <div className="flex gap-3">
          <AIGenerateDialog 
            onGenerate={handleAIGenerate}
            projectId={projectId}
          />
          <Dialog 
            open={isImportTestOpen} 
            onOpenChange={(open) => {
              setIsImportTestOpen(open);
              // Reset droppedFileName when dialog is closed
              if (!open) {
                setImportData(prev => ({ ...prev, droppedFileName: "" }));
              }
            }}
          >
            <Button 
              variant="outline" 
              onClick={() => setIsImportTestOpen(true)}
              onDragOver={handleDragOver}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`relative ${isDragging ? 'bg-primary/10 border-primary' : ''}`}
            >
              <Import className="h-4 w-4 mr-2" />
              {isDragging ? 'Drop Excel File Here' : 'Import'}
              {isDragging && (
                <div className="absolute inset-0 border-2 border-dashed border-primary rounded-md pointer-events-none" />
              )}
            </Button>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Import Test Cases</DialogTitle>
                <DialogDescription>
                  Import test cases from external sources
                </DialogDescription>
              </DialogHeader>
              
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="import-type">Import Type</Label>
                  <Select 
                    value={importData.importType}
                    onValueChange={(value) => setImportData({...importData, importType: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select import type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="url">
                        <div className="flex items-center">
                          <Link className="h-4 w-4 mr-2" />
                          URL Upload
                        </div>
                      </SelectItem>
                      <SelectItem value="file">
                        <div className="flex items-center">
                          <FileText className="h-4 w-4 mr-2" />
                          Excel File
                        </div>
                      </SelectItem>
                      <SelectItem value="mcp">
                        <div className="flex items-center">
                          <ExternalLink className="h-4 w-4 mr-2" />
                          MCP Server
                        </div>
                      </SelectItem>
                      <SelectItem value="jira">
                        <div className="flex items-center">
                          <Download className="h-4 w-4 mr-2" />
                          Jira Integration
                        </div>
                      </SelectItem>
                      <SelectItem value="trello">
                        <div className="flex items-center">
                          <Download className="h-4 w-4 mr-2" />
                          Trello Board
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {importData.importType === "url" && (
                  <div className="grid gap-2">
                    <Label htmlFor="url">Test Case URL</Label>
                    <Input 
                      id="url" 
                      value={importData.url}
                      onChange={(e) => setImportData({...importData, url: e.target.value})}
                      placeholder="https://example.com/testcases.json"
                    />
                    <p className="text-xs text-muted-foreground">Enter a URL containing test case definitions in JSON or XML format</p>
                  </div>
                )}
                
                {importData.importType === "file" && (
                  <div className="grid gap-2">
                    <Label htmlFor="file-path">Excel File Path</Label>
                    <Input 
                      id="file-path" 
                      value={importData.filePath}
                      onChange={(e) => setImportData({...importData, filePath: e.target.value})}
                      placeholder="Downloads\performance_test_1_2025-08-30T09-07-37.xlsx"
                    />
                    <div 
                      className={`border-2 border-dashed ${importData.droppedFileName ? 'border-success bg-success/5' : 'border-primary/40'} rounded-md p-6 flex flex-col items-center justify-center cursor-pointer hover:bg-primary/5 transition-colors`}
                      onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                      onDragEnter={(e) => { e.preventDefault(); e.stopPropagation(); }}
                      onDragLeave={(e) => { e.preventDefault(); e.stopPropagation(); }}
                      onDrop={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                          const file = e.dataTransfer.files[0];
                          if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                            setImportData(prev => ({
                              ...prev,
                              filePath: file.name,
                              droppedFileName: file.name
                            }));
                          } else {
                            toast({
                              title: "Invalid File Type",
                              description: "Please drop an Excel file (.xlsx or .xls)",
                              variant: "destructive"
                            });
                          }
                        }
                      }}
                    >
                      {importData.droppedFileName ? (
                        <>
                          <FileText className="h-12 w-12 text-success mb-2" />
                          <p className="text-center text-sm font-medium mb-1">{importData.droppedFileName}</p>
                          <p className="text-center text-xs text-muted-foreground">Excel file ready for import</p>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="mt-2"
                            onClick={() => setImportData(prev => ({ ...prev, droppedFileName: "" }))}
                          >
                            Change File
                          </Button>
                        </>
                      ) : (
                        <>
                          <FileText className="h-12 w-12 text-primary/60 mb-2" />
                          <p className="text-center text-sm text-muted-foreground mb-1">Drag and drop Excel file here</p>
                          <p className="text-center text-xs text-muted-foreground">or enter the path above</p>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">Enter the path to your Excel file containing test cases</p>
                  </div>
                )}
                
                {(importData.importType === "jira" || importData.importType === "trello" || importData.importType === "mcp") && (
                  <div className="space-y-4">
                    <div className="grid gap-2">
                      <Label htmlFor="connection">Connection</Label>
                      <Select 
                        value={importData.connection}
                        onValueChange={(value) => setImportData({...importData, connection: value})}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select connection" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="rebe.app">rebe.app</SelectItem>
                          <SelectItem value="direct">Direct Connection</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="grid gap-2">
                        <Label htmlFor="username">Username</Label>
                        <Input 
                          id="username" 
                          value={importData.username}
                          onChange={(e) => setImportData({...importData, username: e.target.value})}
                          placeholder="Your username"
                        />
                      </div>
                      
                      <div className="grid gap-2">
                        <Label htmlFor="password">API Key/Password</Label>
                        <Input 
                          id="password" 
                          type="password"
                          value={importData.password}
                          onChange={(e) => setImportData({...importData, password: e.target.value})}
                          placeholder="Your API key or password"
                        />
                      </div>
                    </div>
                    
                    <div className="grid gap-2">
                      <Label htmlFor="project">Project/Board</Label>
                      <Input 
                        id="project" 
                        value={importData.project}
                        onChange={(e) => setImportData({...importData, project: e.target.value})}
                        placeholder="Project key or board name"
                      />
                    </div>
                  </div>
                )}
                
                {/* Option to generate edge cases */}
                <div className="flex items-center space-x-2 mt-2">
                  <Checkbox 
                    id="generate-edge-cases" 
                    checked={importData.generateEdgeCases}
                    onCheckedChange={(checked) => setImportData({...importData, generateEdgeCases: !!checked})}
                  />
                  <label
                    htmlFor="generate-edge-cases"
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    Generate edge case scenarios from imported tests
                  </label>
                </div>
              </div>
              
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsImportTestOpen(false)}>Cancel</Button>
                <Button onClick={handleImportTestCases}>
                  <Import className="h-4 w-4 mr-2" />
                  Import Test Cases
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Dialog open={isNewTestOpen} onOpenChange={setIsNewTestOpen}>
            <Button variant="default" onClick={() => setIsNewTestOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              New Test Case
            </Button>
            <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Test Case</DialogTitle>
                <DialogDescription>
                  Fill in all the details to create a comprehensive test case
                </DialogDescription>
              </DialogHeader>
              
              <TestCaseForm
                onSubmit={handleCreateTestCase}
                onCancel={() => setIsNewTestOpen(false)}
              />
            </DialogContent>
          </Dialog>
          
          {/* Edit Test Case Dialog */}
          <Dialog open={isEditTestOpen} onOpenChange={setIsEditTestOpen}>
            <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Edit Test Case</DialogTitle>
                <DialogDescription>
                  Update the test case details
                </DialogDescription>
              </DialogHeader>
              
              {currentTestToEdit && (
                <TestCaseForm
                  testCase={currentTestToEdit}
                  onSubmit={handleUpdateTestCase}
                  onCancel={() => setIsEditTestOpen(false)}
                />
              )}
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters and Search */}
      <Card className="bg-card/50 backdrop-blur-sm">
        <CardContent className="p-4">
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search test cases..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Popover open={showFilterPopover} onOpenChange={setShowFilterPopover}>
              <PopoverTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                  {Object.values(filters).flat().length > 0 && (
                    <Badge variant="secondary" className="ml-2">
                      {Object.values(filters).flat().length}
                    </Badge>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-80 p-4">
                <div className="space-y-4">
                  <h4 className="font-medium">Filter Test Cases</h4>
                  
                  {/* Test Type Filter */}
                  <div className="space-y-2">
                    <h5 className="text-sm font-medium">Test Type</h5>
                    <div className="grid grid-cols-2 gap-2">
                      {availableTestTypes.map((type) => (
                        <div key={type} className="flex items-center space-x-2">
                          <Checkbox 
                            id={`type-${type}`} 
                            checked={filters.testType.includes(type)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setFilters({
                                  ...filters,
                                  testType: [...filters.testType, type]
                                })
                              } else {
                                setFilters({
                                  ...filters,
                                  testType: filters.testType.filter(t => t !== type)
                                })
                              }
                            }}
                          />
                          <label
                            htmlFor={`type-${type}`}
                            className="text-xs capitalize"
                          >
                            {type}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Priority Filter */}
                  <div className="space-y-2">
                    <h5 className="text-sm font-medium">Priority</h5>
                    <div className="grid grid-cols-2 gap-2">
                      {availablePriorities.map((priority) => (
                        <div key={priority} className="flex items-center space-x-2">
                          <Checkbox 
                            id={`priority-${priority}`} 
                            checked={filters.priority.includes(priority)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setFilters({
                                  ...filters,
                                  priority: [...filters.priority, priority]
                                })
                              } else {
                                setFilters({
                                  ...filters,
                                  priority: filters.priority.filter(p => p !== priority)
                                })
                              }
                            }}
                          />
                          <label
                            htmlFor={`priority-${priority}`}
                            className="text-xs capitalize"
                          >
                            {priority}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Status Filter */}
                  <div className="space-y-2">
                    <h5 className="text-sm font-medium">Status</h5>
                    <div className="grid grid-cols-2 gap-2">
                      {availableStatuses.map((status) => (
                        <div key={status} className="flex items-center space-x-2">
                          <Checkbox 
                            id={`status-${status}`} 
                            checked={filters.status.includes(status)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setFilters({
                                  ...filters,
                                  status: [...filters.status, status]
                                })
                              } else {
                                setFilters({
                                  ...filters,
                                  status: filters.status.filter(s => s !== status)
                                })
                              }
                            }}
                          />
                          <label
                            htmlFor={`status-${status}`}
                            className="text-xs capitalize"
                          >
                            {status}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Tags Filter */}
                  {availableTags.length > 0 && (
                    <div className="space-y-2">
                      <h5 className="text-sm font-medium">Tags</h5>
                      <div className="grid grid-cols-2 gap-2">
                        {availableTags.map((tag) => (
                          <div key={tag} className="flex items-center space-x-2">
                            <Checkbox 
                              id={`tag-${tag}`} 
                              checked={filters.tags.includes(tag)}
                              onCheckedChange={(checked) => {
                                if (checked) {
                                  setFilters({
                                    ...filters,
                                    tags: [...filters.tags, tag]
                                  })
                                } else {
                                  setFilters({
                                    ...filters,
                                    tags: filters.tags.filter(t => t !== tag)
                                  })
                                }
                              }}
                            />
                            <label
                              htmlFor={`tag-${tag}`}
                              className="text-xs"
                            >
                              {tag}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex justify-between pt-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        setFilters({
                          testType: [],
                          priority: [],
                          status: [],
                          tags: []
                        })
                      }}
                    >
                      Reset Filters
                    </Button>
                    <Button 
                      size="sm"
                      onClick={() => setShowFilterPopover(false)}
                    >
                      Apply Filters
                    </Button>
                  </div>
                </div>
              </PopoverContent>
            </Popover>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Test Cases List */}
        <div className="lg:col-span-2 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <span className="ml-2 text-muted-foreground">Loading test cases...</span>
            </div>
          ) : error ? (
            <div className="text-center p-8">
              <AlertTriangle className="h-8 w-8 text-destructive mx-auto mb-2" />
              <p className="text-destructive">{error}</p>
              <Button onClick={refetch} variant="outline" className="mt-2">
                Try Again
              </Button>
            </div>
          ) : filteredTestCases.length === 0 ? (
            <div className="text-center p-8">
              <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">
                {searchTerm ? 'No test cases found matching your search.' : 'No test cases found. Generate some with AI or create manually.'}
              </p>
            </div>
          ) : (
            filteredTestCases.map((test) => (
            <Card 
              key={test.id} 
              className={`cursor-pointer transition-all duration-200 hover:shadow-card border-l-4 ${getPriorityColor(test.priority)} ${
                selectedTest === test.id ? "bg-primary/5 border-primary/30" : "bg-card/50 backdrop-blur-sm"
              }`}
              onClick={() => setSelectedTest(test.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      {test.title}
                    </CardTitle>
                    <CardDescription>{test.description}</CardDescription>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(test.status)} variant="outline">
                      {test.status}
                    </Badge>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 mt-3">
                  {getAutomationBadge(test.ai_generated ? "ai-generated" : "manual")}
                  {test.tags?.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <CheckCircle className="h-4 w-4 text-success" />
                      <span>No runs yet</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>{new Date(test.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={(e) => handleEditTestCase(test.id, e)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        setShowComments(!showComments)
                      }}
                    >
                      <MessageSquare className="h-4 w-4" />
                      0
                    </Button>
                    <Button 
                      variant="default" 
                      size="sm"
                      onClick={(e) => executeTestCase(test.id, e)}
                      disabled={isExecuting}
                    >
                      {isExecuting && selectedTest === test.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
            ))
          )}
        </div>

        {/* Collaboration Panel */}
        <div className="space-y-4">
          <Card className="bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-primary" />
                Test Collaboration
              </CardTitle>
              <CardDescription>
                Real-time comments and discussions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {allComments.map((comment) => (
                <div key={comment.id} className="p-3 rounded-lg bg-background/50 border border-border/50">
                  <div className="flex items-start justify-between mb-2">
                    <span className="font-medium text-sm">{comment.user}</span>
                    <span className="text-xs text-muted-foreground">{comment.time}</span>
                  </div>
                  <p className="text-sm text-muted-foreground">{comment.message}</p>
                  {comment.type === "system" && (
                    <Badge variant="outline" className="mt-2 text-xs">
                      <Brain className="h-3 w-3 mr-1" />
                      Auto-Update
                    </Badge>
                  )}
                </div>
              ))}
              
              <div className="space-y-2">
                <Textarea 
                  placeholder="Add your comment..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="resize-none"
                />
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={handleAddComment}
                  disabled={!newComment.trim()}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Comment
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* AI Insights */}
          <Card className="bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                AI Test Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 rounded-lg bg-success/10 border border-success/20">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="h-4 w-4 text-success" />
                  <span className="text-sm font-medium">Coverage Optimal</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Login tests cover all critical scenarios
                </p>
              </div>
              
              <div className="p-3 rounded-lg bg-warning/10 border border-warning/20">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  <span className="text-sm font-medium">Suggest Enhancement</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Add negative test cases for payment flow
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default TestCases