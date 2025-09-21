# AI Test Generation & Export Features - Quick Start Guide

## Overview

The IntelliTestAI platform now includes comprehensive AI-powered test case generation and export functionality. You can generate test cases from text prompts or website URLs, and export them in multiple formats.

## 🎯 Features Implemented

### 1. AI Test Case Generation
- **Text Prompt Generation**: Generate test cases from natural language descriptions
- **Website URL Analysis**: Analyze websites and generate relevant test cases
- **Multiple Test Types**: Support for functional, integration, API, performance, and other test types
- **Priority-based Generation**: Set test case priorities (low, medium, high, critical)

### 2. Export Functionality
- **CSV Export**: For data analysis and spreadsheet usage
- **Excel Export**: Professional formatting with detailed test steps
- **PDF Export**: Documentation-ready format with proper styling
- **Automatic Filename Generation**: Timestamped filenames for easy organization

### 3. User Interface
- **Integrated AI Generator Page**: Easy-to-use interface for test generation
- **Export Buttons**: One-click export in multiple formats
- **Project Selection**: Generate tests for specific projects
- **Real-time Feedback**: Toast notifications for status updates

## 🚀 Quick Start

### Prerequisites
1. Backend server running on port 8001
2. Frontend running on port 5175
3. Database properly set up with test users and projects
4. OpenAI API key configured (for AI generation)

### Setup Commands
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create test users and projects
python test_ai_generation_and_export.py

# 3. Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# 4. In a new terminal, start frontend
cd ../frontend
npm run dev
```

### Access the Application
1. Open: http://localhost:5175/
2. Login with: test@example.com / test1234
3. Navigate to "AI Generator" page

## 💡 How to Use

### Text Prompt Generation
1. Select a project from the dropdown
2. Choose "Text Prompt" tab
3. Enter your test description, for example:
   ```
   Login functionality with email and password validation,
   including forgot password flow and error handling
   ```
4. Click "Generate Test Cases"
5. Review generated test cases
6. Use export buttons to download results

### Website URL Generation
1. Select a project from the dropdown
2. Choose "Website URL" tab
3. Enter a website URL, for example:
   ```
   https://example.com/login
   https://shopify.com/checkout
   https://github.com/login
   ```
4. Click "Generate Test Cases"
5. Review generated test cases based on website analysis
6. Use export buttons to download results

### Export Options
- **CSV**: Click "Export CSV" for spreadsheet-compatible format
- **Excel**: Click "Export Excel" for formatted spreadsheet with detailed steps
- **PDF**: Click "Export PDF" for documentation-ready format

## 🔧 API Endpoints

### AI Generation
```
POST /api/v1/ai/generate-tests
POST /api/v1/ai/generate-tests-from-url
```

### Export Endpoints
```
GET /api/v1/test-cases/export/csv?project_id={id}
GET /api/v1/test-cases/export/excel?project_id={id}
GET /api/v1/test-cases/export/pdf?project_id={id}
```

## 📋 Example Test Case Generation

### Input Prompt:
```
Login functionality with email and password - with steps to login and expected, actual results
```

### Generated Output:
```
Test Case: User Login with Valid Credentials
Description: Verify successful login functionality with valid email and password

Steps:
1. Navigate to login page
   Expected: Login form is displayed with email and password fields
   
2. Enter valid email address
   Expected: Email field accepts input and shows no validation errors
   
3. Enter valid password
   Expected: Password field accepts input and masks characters
   
4. Click login button
   Expected: User is authenticated and redirected to dashboard

Tags: authentication, login, functional, smoke
Priority: High
```

## 🛠️ Technical Details

### Database Schema
- **TestStep Model**: Now includes `created_at` and `updated_at` fields
- **AI Generated Flag**: Test cases marked as AI-generated
- **Project Association**: Test cases linked to specific projects

### Export Formats
- **CSV**: Simple comma-separated format with all test case details
- **Excel**: Professionally formatted with headers, styling, and auto-sizing
- **PDF**: Multi-page document with proper formatting and test step details

### AI Integration
- **OpenAI GPT-4**: For natural language processing and test case generation
- **MCP Server**: For website analysis and structure identification
- **Smart Parsing**: Automatic identification of forms, buttons, and testable elements

## 🔍 Troubleshooting

### Common Issues
1. **"Generate Test Cases" button greyed out**
   - Ensure a project is selected
   - Check that prompt/URL is entered
   - Verify backend connection

2. **Export not working**
   - Ensure test cases are generated first
   - Check browser download permissions
   - Verify backend export endpoints are accessible

3. **AI generation failing**
   - Check OpenAI API key configuration
   - Verify internet connection for URL analysis
   - Check backend logs for detailed error messages

### Debug Commands
```bash
# Test backend connectivity
curl http://127.0.0.1:8001/api/health

# Test project listing
curl http://127.0.0.1:8001/api/projects-test

# Run comprehensive test
python test_ai_generation_and_export.py
```

## 🎉 Success Criteria

You'll know everything is working correctly when you can:
1. ✅ Login to the application
2. ✅ Select a project from dropdown
3. ✅ Generate test cases from text prompts
4. ✅ Generate test cases from website URLs
5. ✅ Export test cases in CSV format
6. ✅ Export test cases in Excel format with detailed steps
7. ✅ Export test cases in PDF format
8. ✅ See detailed test steps in exported files

## 📞 Support

If you encounter issues:
1. Check the browser console for frontend errors
2. Check backend logs for API errors
3. Run the test script: `python test_ai_generation_and_export.py`
4. Verify all dependencies are installed
5. Ensure OpenAI API key is properly configured

## 🎯 Next Steps

After successful setup, you can:
- Customize AI prompts for specific testing scenarios
- Add more test case templates
- Integrate with CI/CD pipelines
- Extend export formats
- Add more sophisticated website analysis rules