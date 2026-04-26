import os
import json
import asyncio
from typing import Dict, Any, List
import httpx
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GroqClient:
    """Groq API client for LLM interactions"""
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.base_url = "https://api.groq.com/openai/v1"
        
        # Don't validate API key here - validate when making requests
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Groq API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            Parsed response from Groq API
        """
        # Validate API key
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set")
        
        try:
            # Prepare messages with system prompt
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Only add JSON format if the request seems to need JSON response
            if any("json" in msg.get("content", "").lower() for msg in messages):
                payload["response_format"] = {"type": "json_object"}
            
            # Make request
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse as JSON
                    try:
                        parsed_content = json.loads(content)
                        return parsed_content
                    except json.JSONDecodeError:
                        # Fallback: return raw content in expected structure
                        return {
                            "reply_text": content,
                            "corrections": [],
                            "vocab_suggestions": []
                        }
                else:
                    logger.error("No choices in Groq response")
                    return {
                        "reply_text": "Sorry, I couldn't process that. Could you try again?",
                        "corrections": [],
                        "vocab_suggestions": []
                    }
                    
        except httpx.TimeoutException:
            logger.error("Groq API timeout")
            return {
                "reply_text": "Sorry, the service is taking too long to respond. Please try again.",
                "corrections": [],
                "vocab_suggestions": []
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "reply_text": "Sorry, there's an issue with the AI service. Please try again later.",
                "corrections": [],
                "vocab_suggestions": []
            }
        except Exception as e:
            logger.error(f"Error in Groq chat completion: {str(e)}")
            return {
                "reply_text": "Sorry, something went wrong. Please try again.",
                "corrections": [],
                "vocab_suggestions": []
            }
    
    async def get_tutor_response(
        self,
        user_message: str,
        session_history: List[Dict[str, str]] = None,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Get response from English tutor
        
        Args:
            user_message: Current user message
            session_history: Previous messages in the session
            system_prompt: System prompt for the tutor
            
        Returns:
            Structured response with reply_text, corrections, vocab_suggestions
        """
        # Prepare messages
        messages = []
        
        # Add session history (last 10 messages)
        if session_history:
            # Take last 10 messages (5 user + 5 assistant)
            recent_history = session_history[-10:]
            messages.extend(recent_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Load system prompt if not provided
        if not system_prompt:
            try:
                with open(os.path.join(settings.BASE_DIR, 'prompts', 'tutor_system.txt'), 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            except Exception as e:
                logger.error(f"Error loading system prompt: {str(e)}")
                system_prompt = "You are an English tutor. Respond naturally and help the student improve."
        
        # Get response from Groq
        return await self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=800,
            timeout=25.0
        )


# Singleton instance
groq_client = GroqClient()
