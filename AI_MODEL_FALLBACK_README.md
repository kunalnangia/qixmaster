# AI Model Fallback Mechanism

This document explains how the IntelliTest AI Automation Platform handles AI model quota errors and implements fallback mechanisms to alternative models.

## Overview

The platform now supports multiple AI providers with automatic fallback when quota limits are reached. When an AI model returns a quota error (429/insufficient_quota), the system automatically tries alternative models in the configured priority order.

## Supported AI Providers

1. **OpenAI** (Primary)
   - Models: gpt-4, gpt-4o, gpt-4-turbo, gpt-3.5-turbo
   - Environment Variable: `OPENAI_API_KEY`

2. **Google Gemini** (Fallback)
   - Models: gemini-pro, gemini-1.5-pro, gemini-1.5-flash
   - Environment Variable: `GOOGLE_API_KEY` or `GEMINI_API_KEY`

## Configuration

### Environment Variables

The following environment variables should be set in your `.env` file:

```env
# Primary AI Provider
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Fallback AI Provider
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-pro

# Model Priority Order (comma-separated)
AI_MODEL_PRIORITY=openai,google
```

### Model Priority

The `AI_MODEL_PRIORITY` variable determines the order in which AI providers are tried. The system will attempt to use providers in the specified order, falling back to the next provider when quota errors occur.

## How Fallback Works

1. **Initial Request**: The system attempts to use the first provider in the priority list (typically OpenAI)
2. **Quota Check**: If the request fails with a quota error (429/insufficient_quota), the system identifies it as a quota-related error
3. **Fallback**: The system automatically tries the next provider in the priority list
4. **Success**: The request is processed successfully with the fallback provider
5. **Error Handling**: If all providers fail, the system returns an appropriate error message

## Error Handling

### Quota Errors Detected

The system detects the following quota-related errors:
- HTTP 429 (Rate Limit Exceeded)
- "insufficient_quota" error codes
- "quota" in error messages
- "rate limit" in error messages

### Non-Quota Errors

Non-quota errors (invalid API keys, network issues, etc.) are not subject to fallback and will be raised immediately.

## Implementation Details

### Backend AI Service

The `LlmChat` class in `backend/app/llm_chat.py` has been enhanced to:
- Support multiple AI providers
- Automatically detect quota errors
- Implement fallback mechanisms
- Maintain conversation history across providers

### Performance Testing AI

The AI workflow in `ai-perf-tester/backend/ai_workflow.py` has been updated to:
- Initialize multiple providers based on environment configuration
- Use a priority-based selection system
- Implement fallback when quota errors occur
- Provide graceful degradation when all providers fail

## Testing Fallback

To test the fallback mechanism:

1. **Temporarily exhaust your OpenAI quota**
2. **Ensure Google API key is configured**
3. **Run a performance test that triggers AI analysis**
4. **Observe the system automatically switch to Google Gemini**

## Adding New Providers

To add support for additional AI providers:

1. Add the provider to the priority list in `.env`
2. Add the API key environment variable
3. Update the provider initialization code in `ai_workflow.py`
4. Add the required dependencies to `ai_requirements.txt`

## Troubleshooting

### Fallback Not Working

If fallback is not working as expected:

1. **Check environment variables** are properly set
2. **Verify API keys** are valid and have quota
3. **Ensure dependencies** are installed (`pip install -r ai_requirements.txt`)
4. **Check logs** for specific error messages

### All Providers Failing

If all providers are failing:

1. **Verify internet connectivity**
2. **Check API key permissions**
3. **Review quota limits** for all providers
4. **Examine error logs** for specific failure reasons

## Best Practices

1. **Configure multiple providers** to ensure maximum availability
2. **Monitor quota usage** to anticipate potential issues
3. **Set appropriate priority** based on cost and performance preferences
4. **Regularly update API keys** and check for expired credentials