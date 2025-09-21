import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  Plus, 
  X, 
  Upload, 
  Link as LinkIcon,
  MessageSquare,
  Paperclip
} from "lucide-react"
import { TestCase } from "@/hooks/useTestCases"

interface TestCaseFormProps {
  testCase?: Partial<TestCase>
  onSubmit: (data: Partial<TestCase>) => void
  onCancel: () => void
}

const TestCaseForm = ({ testCase, onSubmit, onCancel }: TestCaseFormProps) => {
  const [formData, setFormData] = useState<Partial<TestCase>>({
    title: "",
    description: "",
    requirement_reference: "",
    test_type: "functional",
    priority: "medium",
    status: "draft",
    module_feature: "",
    tags: [],
    version_build: "",
    preconditions: "",
    test_data: {},
    expected_result: "",
    actual_result: "",
    environment: "dev",
    automation_status: "manual",
    owner: "",
    assigned_to: "",
    linked_defects: [],
    attachments: [],
    ...testCase
  })

  const [newTag, setNewTag] = useState("")
  const [newDefect, setNewDefect] = useState("")

  const handleInputChange = (field: keyof TestCase, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      handleInputChange("tags", [...(formData.tags || []), newTag.trim()])
      setNewTag("")
    }
  }

  const handleRemoveTag = (tag: string) => {
    handleInputChange("tags", (formData.tags || []).filter(t => t !== tag))
  }

  const handleAddDefect = () => {
    if (newDefect.trim() && !formData.linked_defects?.includes(newDefect.trim())) {
      handleInputChange("linked_defects", [...(formData.linked_defects || []), newDefect.trim()])
      setNewDefect("")
    }
  }

  const handleRemoveDefect = (defect: string) => {
    handleInputChange("linked_defects", (formData.linked_defects || []).filter(d => d !== defect))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Information Section */}
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title / Summary *</Label>
              <Input
                id="title"
                value={formData.title || ""}
                onChange={(e) => handleInputChange("title", e.target.value)}
                placeholder="e.g., Login with valid credentials"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="requirement_reference">Requirement / User Story Reference</Label>
              <div className="flex gap-2">
                <Input
                  id="requirement_reference"
                  value={formData.requirement_reference || ""}
                  onChange={(e) => handleInputChange("requirement_reference", e.target.value)}
                  placeholder="e.g., JIRA-123"
                />
                <Button type="button" variant="outline" size="icon">
                  <LinkIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description || ""}
              onChange={(e) => handleInputChange("description", e.target.value)}
              placeholder="Business-friendly explanation of what is being tested"
              rows={3}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="test_type">Test Type</Label>
              <Select
                value={formData.test_type || "functional"}
                onValueChange={(value: any) => handleInputChange("test_type", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="functional">Functional</SelectItem>
                  <SelectItem value="regression">Regression</SelectItem>
                  <SelectItem value="smoke">Smoke</SelectItem>
                  <SelectItem value="uat">UAT</SelectItem>
                  <SelectItem value="performance">Performance</SelectItem>
                  <SelectItem value="security">Security</SelectItem>
                  <SelectItem value="api">API</SelectItem>
                  <SelectItem value="visual">Visual</SelectItem>
                  <SelectItem value="integration">Integration</SelectItem>
                  <SelectItem value="unit">Unit</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <Select
                value={formData.priority || "medium"}
                onValueChange={(value: any) => handleInputChange("priority", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={formData.status || "draft"}
                onValueChange={(value: any) => handleInputChange("status", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="ready">Ready</SelectItem>
                  <SelectItem value="pass">Pass</SelectItem>
                  <SelectItem value="fail">Fail</SelectItem>
                  <SelectItem value="blocked">Blocked</SelectItem>
                  <SelectItem value="not_run">Not Run</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="module_feature">Module / Feature</Label>
              <Input
                id="module_feature"
                value={formData.module_feature || ""}
                onChange={(e) => handleInputChange("module_feature", e.target.value)}
                placeholder="e.g., Payments, Navigation"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="version_build">Version / Build</Label>
              <Input
                id="version_build"
                value={formData.version_build || ""}
                onChange={(e) => handleInputChange("version_build", e.target.value)}
                placeholder="e.g., v1.2.3"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>Tags / Labels</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.tags?.map((tag) => (
                <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="rounded-full hover:bg-secondary-foreground/20"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag"
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTag())}
              />
              <Button type="button" variant="outline" size="icon" onClick={handleAddTag}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Execution-Focused Fields Section */}
      <Card>
        <CardHeader>
          <CardTitle>Execution Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="preconditions">Preconditions</Label>
            <Textarea
              id="preconditions"
              value={formData.preconditions || ""}
              onChange={(e) => handleInputChange("preconditions", e.target.value)}
              placeholder="Setup/data/environment required"
              rows={2}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="test_data">Test Data</Label>
              <Textarea
                id="test_data"
                value={JSON.stringify(formData.test_data || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const parsed = JSON.parse(e.target.value)
                    handleInputChange("test_data", parsed)
                  } catch {
                    // If invalid JSON, keep as string
                    handleInputChange("test_data", { raw: e.target.value })
                  }
                }}
                placeholder='{"username": "testuser", "password": "testpass"}'
                rows={3}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="environment">Environment</Label>
              <Select
                value={formData.environment || "dev"}
                onValueChange={(value: any) => handleInputChange("environment", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dev">Dev</SelectItem>
                  <SelectItem value="qa">QA</SelectItem>
                  <SelectItem value="staging">Staging</SelectItem>
                  <SelectItem value="prod">Prod</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="expected_result">Expected Result</Label>
              <Textarea
                id="expected_result"
                value={formData.expected_result || ""}
                onChange={(e) => handleInputChange("expected_result", e.target.value)}
                placeholder="What should happen"
                rows={2}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="actual_result">Actual Result</Label>
              <Textarea
                id="actual_result"
                value={formData.actual_result || ""}
                onChange={(e) => handleInputChange("actual_result", e.target.value)}
                placeholder="Captured during execution"
                rows={2}
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="automation_status">Automation Status</Label>
            <Select
              value={formData.automation_status || "manual"}
              onValueChange={(value: any) => handleInputChange("automation_status", value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="manual">Manual</SelectItem>
                <SelectItem value="automated">Automated</SelectItem>
                <SelectItem value="candidate">Candidate</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      {/* Collaboration & Reporting Fields Section */}
      <Card>
        <CardHeader>
          <CardTitle>Collaboration & Reporting</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="owner">Owner / Author</Label>
              <Input
                id="owner"
                value={formData.owner || ""}
                onChange={(e) => handleInputChange("owner", e.target.value)}
                placeholder="Who created/owns the test"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="assigned_to">Assigned To</Label>
              <Input
                id="assigned_to"
                value={formData.assigned_to || ""}
                onChange={(e) => handleInputChange("assigned_to", e.target.value)}
                placeholder="Who is responsible for execution"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>Linked Defects / Issues</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.linked_defects?.map((defect) => (
                <Badge key={defect} variant="destructive" className="flex items-center gap-1">
                  {defect}
                  <button
                    type="button"
                    onClick={() => handleRemoveDefect(defect)}
                    className="rounded-full hover:bg-destructive-foreground/20"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={newDefect}
                onChange={(e) => setNewDefect(e.target.value)}
                placeholder="e.g., BUG-456"
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddDefect())}
              />
              <Button type="button" variant="outline" size="icon" onClick={handleAddDefect}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>Attachments / References</Label>
            <div className="border-2 border-dashed rounded-lg p-4 text-center">
              <Paperclip className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground mb-2">
                Drag and drop files here or click to browse
              </p>
              <Button type="button" variant="outline" size="sm">
                <Upload className="h-4 w-4 mr-2" />
                Select Files
              </Button>
              <p className="text-xs text-muted-foreground mt-2">
                Supported formats: PNG, JPG, PDF, DOCX, XLSX
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Form Actions */}
      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {testCase?.id ? "Update Test Case" : "Create Test Case"}
        </Button>
      </div>
    </form>
  )
}

export default TestCaseForm