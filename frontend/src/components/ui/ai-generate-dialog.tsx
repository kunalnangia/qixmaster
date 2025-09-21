import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Sparkles, Loader2, AlertCircle, CheckCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { getApiUrl, API_ENDPOINTS } from "@/config/api"

interface AIGenerateDialogProps {
  onGenerate?: (generatedTestCases: any[]) => void
  projectId?: string
  children?: React.ReactNode
}

export function AIGenerateDialog({ onGenerate, projectId, children }: AIGenerateDialogProps) {
  const [open, setOpen] = useState(false)
  const [url, setUrl] = useState("")
  const [testCount, setTestCount] = useState(5)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!url) {
      setError("Please enter a website URL")
      return
    }

    if (!projectId) {
      setError("Project ID is required")
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      setSuccess(null)

      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      // Use the proxy URL for AI test case generation
      const backendUrl = getApiUrl('/ai/generate-tests-from-url')
      
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          url: url,
          project_id: projectId,
          test_type: 'functional',
          priority: 'medium',
          count: testCount
        })
      })

      if (!response.ok) {
        let errorMessage = 'Failed to generate test cases'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      let data
      try {
        data = await response.json()
      } catch (jsonError) {
        throw new Error('Failed to parse response: Unexpected end of JSON input')
      }
      const testCasesCount = Array.isArray(data) ? data.length : (data.generated_test_cases?.length || testCount)
      setSuccess(`Successfully generated ${testCasesCount} test cases from ${url}!`)
      
      // Call the parent callback if provided - pass the test cases
      if (onGenerate) {
        const testCases = Array.isArray(data) ? data : (data.generated_test_cases || [])
        onGenerate(testCases)
      }

      // Close dialog after a brief success message
      setTimeout(() => {
        setOpen(false)
        setUrl("")
        setTestCount(5)
        setSuccess(null)
      }, 2000)

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate test cases'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const isValidUrl = (string: string) => {
    try {
      new URL(string)
      return true
    } catch (_) {
      return false
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="ai">
            <Sparkles className="h-4 w-4 mr-2" />
            AI Generate
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Generate Test Cases from Website
          </DialogTitle>
          <DialogDescription>
            Enter a website URL and our AI will analyze it to generate comprehensive test cases automatically.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="url">Website URL</Label>
            <Input
              id="url"
              type="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isLoading}
            />
            <p className="text-sm text-muted-foreground">
              Enter the URL of the website you want to generate test cases for
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="count">Number of Test Cases</Label>
            <Input
              id="count"
              type="number"
              min="1"
              max="10"
              value={testCount}
              onChange={(e) => setTestCount(parseInt(e.target.value) || 5)}
              disabled={isLoading}
            />
            <p className="text-sm text-muted-foreground">
              How many test cases to generate (1-10)
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
         ) }

          {success && (
            <Alert className="border-success bg-success/10">
              <CheckCircle className="h-4 w-4 text-success" />
              <AlertDescription className="text-success">{success}</AlertDescription>
            </Alert>
          )
          }
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)} disabled={isLoading}>
            Cancel
          </Button>
          <Button 
            onClick={handleGenerate} 
            disabled={isLoading || !url || !isValidUrl(url)}
            className="min-w-[120px]"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}