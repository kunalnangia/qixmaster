import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RefreshCw, Loader2 } from 'lucide-react'
import { useTestCases } from '@/hooks/useTestCases'
import { useToast } from '@/hooks/use-toast'

interface TestCaseSelectorProps {
  value: string
  onValueChange: (value: string) => void
  testType?: string
  placeholder?: string
  showRefreshButton?: boolean
}

const TestCaseSelector = ({
  value,
  onValueChange,
  testType,
  placeholder = "Select a test case",
  showRefreshButton = true
}: TestCaseSelectorProps) => {
  const { testCases, loading, refetch } = useTestCases()
  const { toast } = useToast()
  const [refreshing, setRefreshing] = useState(false)

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      await refetch()
      toast({
        title: "Refreshed",
        description: "Test cases have been refreshed",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to refresh test cases",
        variant: "destructive",
      })
    } finally {
      setRefreshing(false)
    }
  }

  // Filter test cases by type if specified
  const filteredTestCases = testType
    ? testCases?.filter(tc => tc.test_type === testType)
    : testCases

  return (
    <div className="flex gap-2">
      <Select value={value} onValueChange={onValueChange} disabled={loading}>
        <SelectTrigger>
          <SelectValue placeholder={loading ? "Loading test cases..." : placeholder} />
        </SelectTrigger>
        <SelectContent>
          {loading ? (
            <SelectItem value="loading" disabled>
              Loading test cases...
            </SelectItem>
          ) : filteredTestCases && filteredTestCases.length > 0 ? (
            filteredTestCases.map((testCase) => (
              <SelectItem key={testCase.id} value={testCase.id}>
                {testCase.title}
              </SelectItem>
            ))
          ) : (
            <SelectItem value="none" disabled>
              No test cases available
            </SelectItem>
          )}
        </SelectContent>
      </Select>
      
      {showRefreshButton && (
        <Button 
          variant="outline" 
          size="icon"
          onClick={handleRefresh}
          disabled={refreshing || loading}
          className="shrink-0"
        >
          {refreshing || loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
        </Button>
      )}
    </div>
  )
}

export default TestCaseSelector