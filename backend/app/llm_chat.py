import os
import json
from typing import Dict, List, Optional, Any

# Add imports for other AI providers
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import google.generativeai as genai
    from google.generativeai.types import generation_types
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    genai = None
    generation_types = None

class LlmChat:
    """
    A simple wrapper for multiple AI chat completion APIs with fallback support.
    """
    
    def __init__(self, session_id: str, system_message: str):
        """
        Initialize the chat session with support for multiple providers.
        
        Args:
            session_id: Unique identifier for the chat session
            system_message: Initial system message to set the behavior of the assistant
        """
        self.session_id = session_id
        self.messages = [{"role": "system", "content": system_message}]
        self.providers = []
        self.current_provider = None
        self.current_model = None
        
        # Initialize available providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers from environment variables."""
        # OpenAI
        if OPENAI_AVAILABLE and openai is not None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key:
                self.providers.append({
                    "name": "openai",
                    "api_key": openai_api_key,
                    "models": ["gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                    "default_model": os.environ.get("OPENAI_MODEL", "gpt-4")
                })
                # Configure OpenAI API key (only for legacy API)
                if hasattr(openai, 'api_key'):
                    openai.api_key = openai_api_key
        
        # Google Gemini
        if GOOGLE_AI_AVAILABLE and genai is not None:
            google_api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
            if google_api_key:
                # Configure Google Generative AI
                if hasattr(genai, 'configure'):
                    genai.configure(api_key=google_api_key)
                self.providers.append({
                    "name": "google",
                    "api_key": google_api_key,
                    "models": ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
                    "default_model": os.environ.get("GOOGLE_MODEL", "gemini-pro")
                })
        
        # Set initial provider and model
        if self.providers:
            self.current_provider = self.providers[0]
            self.current_model = self.current_provider["default_model"]
    
    def with_model(self, provider: str, model_name: str) -> 'LlmChat':
        """
        Set the model to use for completions.
        
        Args:
            provider: The provider of the model (e.g., 'openai', 'google')
            model_name: The name of the model to use
            
        Returns:
            Self for method chaining
        """
        for prov in self.providers:
            if prov["name"] == provider.lower():
                self.current_provider = prov
                self.current_model = model_name
                break
        return self
    
    def _is_quota_error(self, error: Exception) -> bool:
        """Check if the error is a quota-related error."""
        error_str = str(error).lower()
        return (
            "quota" in error_str or 
            "429" in error_str or 
            "insufficient_quota" in error_str or
            "rate limit" in error_str
        )
    
    def _get_next_provider(self) -> Optional[Dict]:
        """Get the next available provider for fallback."""
        if not self.providers or not self.current_provider:
            return None
            
        current_index = next((i for i, p in enumerate(self.providers) 
                             if p["name"] == self.current_provider["name"]), -1)
        
        # Try next provider in the list
        for i in range(current_index + 1, len(self.providers)):
            return self.providers[i]
            
        # If we're at the end, try from the beginning (except current)
        for i in range(0, current_index):
            return self.providers[i]
            
        return None
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Get a completion for the given prompt with fallback support.
        
        Args:
            prompt: The user's message
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The assistant's response as a string
        """
        # Add user message to the conversation history
        self.messages.append({"role": "user", "content": prompt})
        
        # Try each provider until one succeeds
        providers_to_try = [self.current_provider] if self.current_provider else []
        
        # Add fallback providers
        next_provider = self._get_next_provider()
        while next_provider and next_provider not in providers_to_try:
            providers_to_try.append(next_provider)
            # Get the next one for potential fallback chain
            temp_chat = LlmChat(self.session_id, "")
            temp_chat.current_provider = next_provider
            next_provider = temp_chat._get_next_provider()
        
        last_error = None
        
        for provider in providers_to_try:
            try:
                if provider["name"] == "openai" and OPENAI_AVAILABLE and openai is not None:
                    # Ensure we have a valid model name
                    model_name = self.current_model or provider["default_model"]
                    if not model_name:
                        raise ValueError("No model specified for OpenAI provider")
                    
                    # Call the OpenAI API (using the modern async API)
                    if hasattr(openai, 'ChatCompletion'):
                        # Legacy API (v0.x)
                        response = await openai.ChatCompletion.acreate(
                            model=model_name,
                            messages=self.messages,
                            **kwargs
                        )
                        # Extract the assistant's response
                        assistant_message = response.choices[0].message
                        assistant_content = assistant_message.content
                    else:
                        # Modern API (v1.x+)
                        from openai import AsyncOpenAI
                        client = AsyncOpenAI(api_key=provider["api_key"])
                        # Convert messages to the correct format for the modern API
                        formatted_messages = []
                        for msg in self.messages:
                            formatted_msg = {
                                "role": msg["role"],
                                "content": msg["content"]
                            }
                            formatted_messages.append(formatted_msg)
                        
                        response = await client.chat.completions.create(
                            model=model_name,
                            messages=formatted_messages,
                            **kwargs
                        )
                        assistant_content = response.choices[0].message.content
                    
                    # Add assistant's response to the conversation history
                    self.messages.append({"role": "assistant", "content": assistant_content})
                    
                    # Update current provider
                    self.current_provider = provider
                    return assistant_content
                    
                elif provider["name"] == "google" and GOOGLE_AI_AVAILABLE and genai is not None:
                    # Ensure we have a valid model name
                    model_name = self.current_model or provider["default_model"]
                    if not model_name:
                        raise ValueError("No model specified for Google provider")
                    
                    # Call the Google Gemini API
                    if hasattr(genai, 'GenerativeModel'):
                        model = genai.GenerativeModel(model_name)
                        
                        # Convert messages to Gemini format
                        gemini_messages = []
                        for msg in self.messages:
                            if msg["role"] == "system":
                                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
                                gemini_messages.append({"role": "model", "parts": ["Understood."]})
                            else:
                                gemini_messages.append({
                                    "role": "user" if msg["role"] == "user" else "model",
                                    "parts": [msg["content"]]
                                })
                        
                        # Add current prompt
                        gemini_messages.append({"role": "user", "parts": [prompt]})
                        
                        response = model.generate_content(gemini_messages)
                        assistant_content = response.text
                        
                        # Add assistant's response to the conversation history
                        self.messages.append({"role": "assistant", "content": assistant_content})
                        
                        # Update current provider
                        self.current_provider = provider
                        return assistant_content
                    
            except Exception as e:
                last_error = e
                # If this is a quota error, try the next provider
                if self._is_quota_error(e):
                    print(f"Quota error with {provider['name']}, trying next provider: {str(e)}")
                    continue
                else:
                    # For non-quota errors, re-raise immediately
                    print(f"Non-quota error with {provider['name']}: {str(e)}")
                    raise
        
        # If we get here, all providers failed
        if last_error:
            raise last_error
        else:
            raise Exception("No AI providers available")
    
    async def complete_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Get a JSON response from the model with fallback support.
        
        Args:
            prompt: The user's message
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The assistant's response parsed as JSON
        """
        # Add a system message to ensure JSON response
        json_system_message = {
            "role": "system",
            "content": "You are a helpful assistant that always responds with valid JSON."
        }
        
        # Create a new messages list with the JSON instruction
        json_messages = [json_system_message] + self.messages[1:] + [{"role": "user", "content": prompt}]
        
        # Create a temporary chat instance with the same providers
        temp_chat = LlmChat(self.session_id, "")
        temp_chat.providers = self.providers
        temp_chat.current_provider = self.current_provider
        temp_chat.current_model = self.current_model
        temp_chat.messages = json_messages
        
        assistant_content = ""  # Initialize the variable
        try:
            # Get response using the complete method with fallback support
            assistant_content = await temp_chat.complete(prompt, **kwargs)
            
            # Parse the JSON response
            try:
                return json.loads(assistant_content)
            except json.JSONDecodeError:
                # If the response isn't valid JSON, try to extract JSON from it
                import re
                json_match = re.search(r'```(?:json)?\n(.*?)\n```', assistant_content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    # Try to find any JSON-like structure in the response
                    json_match = re.search(r'\{.*\}', assistant_content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(0))
                    else:
                        raise ValueError(f"Could not parse JSON from response: {assistant_content}")
        except Exception as e:
            # If we can't parse JSON, return an error response
            return {
                "error": "Failed to parse JSON response",
                "message": str(e),
                "raw_response": assistant_content
            }
