import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { FileText, Upload } from "lucide-react"

const TestExcelImport = () => {
  const [filePath, setFilePath] = useState("Downloads\\performance_test_1_2025-08-30T09-07-37.xlsx")
  const { toast } = useToast()

  const handleImport = async () => {
    if (!filePath) {
      toast({
        title: "Error",
        description: "Please enter a valid file path",
        variant: "destructive"
      })
      return
    }

    try {
      // Simulate importing with a timeout
      toast({
        title: "Import Started",
        description: "Importing test cases from Excel file...",
      })

      await new Promise(resolve => setTimeout(resolve, 1500))

      toast({
        title: "Import Successful",
        description: "Test cases imported successfully from Excel file",
      })
    } catch (error) {
      toast({
        title: "Import Failed",
        description: error instanceof Error ? error.message : "Failed to import test cases",
        variant: "destructive"
      })
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Test Excel Import</CardTitle>
          <CardDescription>
            Test the Excel file import functionality
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="file-path">Excel File Path</Label>
            <Input 
              id="file-path" 
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="Downloads\performance_test_1_2025-08-30T09-07-37.xlsx"
            />
            <p className="text-xs text-muted-foreground">Enter the path to your Excel file containing test cases</p>
          </div>
          
          <Button onClick={handleImport}>
            <Upload className="h-4 w-4 mr-2" />
            Import Test Cases
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default TestExcelImport