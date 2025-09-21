import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Wand2, Loader2, Plus, Globe, Download, FileText, FileSpreadsheet, FileImage } from 'lucide-react'
import { useAI } from '@/hooks/useAI'
import { useProjects } from '@/hooks/useProjects'
import { useTestCases } from '@/hooks/useTestCases'
import { useToast } from '@/hooks/use-toast'

const AIGenerator = () => {
  const [prompt, setPrompt] = useState('')
  const [url, setUrl] = useState('')
  const [selectedProject, setSelectedProject] = useState('')
  const [generatedTests, setGeneratedTests] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState('prompt')
  const { generateTests, generateTestsFromUrl, isGenerating } = useAI()
  const { projects, loading: projectsLoading, error: projectsError } = useProjects()
  const { createTestCase } = useTestCases()
  const { toast } = useToast()

  // Debug information
  const debugInfo = {
    isGenerating,
    prompt: prompt.trim(),
    url: url.trim(),
    selectedProject,
    projectsCount: projects?.length || 0,
    projectsLoading,
    projectsError,
    activeTab,
    buttonShouldBeDisabled: isGenerating || (activeTab === 'prompt' ? !prompt.trim() : !url.trim()) || !selectedProject
  }

  console.log('AIGenerator Debug Info:', debugInfo)

  const handleGenerate = async () => {
    const currentInput = activeTab === 'prompt' ? prompt : url
    
    if (!currentInput.trim() || !selectedProject) {
      toast({
        title: "Missing Information",
        description: "Please enter a prompt/URL and select a project",
        variant: "destructive",
      })
      return
    }
    
    // Validate URL format if using website URL generation
    if (activeTab === 'url' && !url.trim().startsWith('http')) {
      toast({
        title: "Invalid URL Format",
        description: "URL must start with http:// or https://",
        variant: "destructive",
      })
      return
    }

    try {
      let result
      if (activeTab === 'prompt') {
        result = await generateTests(prompt, selectedProject)
      } else {
        // Call URL-based generation endpoint
        result = await generateTestsFromUrl(url, selectedProject)
      }
      setGeneratedTests(result.tests?.testCases || [])
    } catch (error) {
      console.error('Error generating tests:', error)
      // Error toast already displayed by the useAI hook
    }
  }

  const handleAddTestCase = async (test: any) => {
    try {
      await createTestCase({
        title: test.title,
        description: test.description,
        expected_result: test.expected_result,
        steps: test.steps || test.test_steps?.map((step: any) => ({
          step_number: step.step_number,
          description: step.description,
          expected_result: step.expected_result
        })) || [],
        priority: test.priority,
        test_type: test.test_type,
        tags: test.tags || [],
        project_id: selectedProject,
        ai_generated: true,
        status: 'draft',
        self_healing_enabled: true
      })

      toast({
        title: "Success",
        description: "Test case added successfully",
      })
    } catch (error) {
      console.error('Error adding test case:', error)
    }
  }

  const handleExport = async (format: 'csv' | 'excel' | 'pdf') => {
    if (!selectedProject || generatedTests.length === 0) {
      toast({
        title: "No Data to Export",
        description: "Please generate test cases first and select a project",
        variant: "destructive",
      })
      return
    }

    try {
      const apiUrl = `http://localhost:8001/api/test-cases/export/${format}?project_id=${selectedProject}`
      
      // Create a temporary link to trigger download
      const link = document.createElement('a')
      link.href = apiUrl
      link.download = `test-cases-${selectedProject}-${Date.now()}.${format === 'excel' ? 'xlsx' : format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: "Export Started",
        description: `Downloading test cases as ${format.toUpperCase()}`,
      })
    } catch (error) {
      console.error('Error exporting test cases:', error)
      toast({
        title: "Export Failed",
        description: "Failed to export test cases. Please try again.",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Test Generator</h1>
        <p className="text-muted-foreground">Generate comprehensive test cases using AI</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="h-5 w-5" />
            Generate Test Cases
          </CardTitle>
          <CardDescription>
            Generate comprehensive test cases using AI from text prompts or website URLs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Project</label>
            <Select value={selectedProject} onValueChange={setSelectedProject}>
              <SelectTrigger>
                <SelectValue placeholder={
                  projectsLoading ? "Loading projects..." : 
                  projectsError ? `Error: ${projectsError}` : 
                  projects?.length === 0 ? "No projects found" :
                  "Select a project"
                } />
              </SelectTrigger>
              <SelectContent>
                {projects?.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {/* Debug information */}
            <div className="text-xs mt-2 space-y-1">
              {projectsError && (
                <p className="text-red-500">
                  Error: {projectsError}
                </p>
              )}
              {!projectsLoading && !projectsError && (
                <p className="text-green-600">
                  Found {projects?.length || 0} project(s)
                </p>
              )}
              {projectsLoading && (
                <p className="text-blue-500">
                  Loading projects...
                </p>
              )}
              <p className="text-gray-500">
                Debug: Loading={projectsLoading.toString()}, Error={projectsError || 'none'}, Count={projects?.length || 0}
              </p>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="prompt">Text Prompt</TabsTrigger>
              <TabsTrigger value="url">Website URL</TabsTrigger>
            </TabsList>
            
            <TabsContent value="prompt" className="space-y-4">
              <div>
                <label className="text-sm font-medium">Describe what you want to test</label>
                <Textarea
                  placeholder="Example: Login functionality with email and password, including forgot password flow and validation errors..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={4}
                />
              </div>
            </TabsContent>
            
            <TabsContent value="url" className="space-y-4">
              <div>
                <label className="text-sm font-medium">Website URL to analyze</label>
                <Input
                  type="url"
                  placeholder="https://example.com/login"
                  value={url}
                  onChange={(e) => {
                    let inputUrl = e.target.value
                    // Add https:// prefix if user didn't include protocol
                    if (inputUrl && !inputUrl.startsWith('http://') && !inputUrl.startsWith('https://')) {
                      if (!url) { // Only auto-add for the first character
                        inputUrl = 'https://' + inputUrl
                      }
                    }
                    setUrl(inputUrl)
                  }}
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Enter a website URL to analyze and generate test cases automatically (must start with http:// or https://)
                </p>
              </div>
            </TabsContent>
          </Tabs>

          <Button 
            onClick={handleGenerate} 
            disabled={isGenerating || (activeTab === 'prompt' ? !prompt.trim() : !url.trim()) || !selectedProject}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing {activeTab === 'url' ? 'Website' : 'Prompt'}...
              </>
            ) : (
              <>
                {activeTab === 'url' ? (
                  <Globe className="mr-2 h-4 w-4" />
                ) : (
                  <Wand2 className="mr-2 h-4 w-4" />
                )}
                Generate Test Cases
              </>
            )}
          </Button>
          
          {/* Status message to help users understand what's needed */}
          {!isGenerating && (
            <div className="text-sm text-center">
              {!selectedProject && (
                <p className="text-orange-600">⚠️ Please select a project first</p>
              )}
              {selectedProject && activeTab === 'prompt' && !prompt.trim() && (
                <p className="text-orange-600">⚠️ Please enter a text prompt</p>
              )}
              {selectedProject && activeTab === 'url' && !url.trim() && (
                <p className="text-orange-600">⚠️ Please enter a website URL</p>
              )}
              {selectedProject && ((activeTab === 'prompt' && prompt.trim()) || (activeTab === 'url' && url.trim())) && (
                <p className="text-green-600">✅ Ready to generate test cases!</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {generatedTests.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Generated Test Cases</h2>
            <div className="flex gap-2">
              <Button
                onClick={() => handleExport('csv')}
                size="sm"
                variant="outline"
                className="gap-2"
              >
                <FileText className="h-4 w-4" />
                Export CSV
              </Button>
              <Button
                onClick={() => handleExport('excel')}
                size="sm"
                variant="outline"
                className="gap-2"
              >
                <FileSpreadsheet className="h-4 w-4" />
                Export Excel
              </Button>
              <Button
                onClick={() => handleExport('pdf')}
                size="sm"
                variant="outline"
                className="gap-2"
              >
                <FileImage className="h-4 w-4" />
                Export PDF
              </Button>
            </div>
          </div>
          <div className="grid gap-4">
            {generatedTests.map((test, index) => (
              <Card key={test.id || index}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{test.title}</CardTitle>
                      <CardDescription>{test.description}</CardDescription>
                    </div>
                    <Button
                      onClick={() => handleAddTestCase(test)}
                      size="sm"
                      className="shrink-0"
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Add to Project
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant={test.priority === 'high' ? 'destructive' : test.priority === 'medium' ? 'default' : 'secondary'}>
                      {test.priority}
                    </Badge>
                    <Badge variant="outline">{test.test_type}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Test Steps:</h4>
                      <ol className="list-decimal list-inside space-y-1">
                        {(test.steps || test.test_steps || []).map((step: any, stepIndex: number) => (
                          <li key={step.id || stepIndex} className="text-sm">
                            <strong>{step.description || step.action}</strong> - Expected: {step.expected_result || step.expected}
                          </li>
                        ))}
                      </ol>
                    </div>
                    <div>
                      <h4 className="font-medium mb-1">Expected Result:</h4>
                      <p className="text-sm text-muted-foreground">{test.expected_result}</p>
                    </div>
                    {test.tags && (
                      <div className="flex gap-1 flex-wrap">
                        {test.tags.map((tag: string, tagIndex: number) => (
                          <Badge key={tagIndex} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AIGenerator