import openai
import anthropic
import asyncio
import json
import tiktoken
from typing import Dict, List, Optional, Any
from app.core.config import settings

class AIClient:
    def __init__(self):
        self.openai_client = None
        self.claude_client = None
        self.tokenizer = None
        
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        if settings.CLAUDE_API_KEY:
            self.claude_client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split()) * 1.3  # Rough estimate
    
    def compress_context(self, messages: List[Dict], max_tokens: int = 3000) -> List[Dict]:
        """Compress context to fit within token limits"""
        if not messages:
            return messages
        
        total_tokens = sum(self.count_tokens(str(msg)) for msg in messages)
        
        if total_tokens <= max_tokens:
            return messages
        
        # Keep system message and recent messages
        compressed = []
        if messages[0].get("role") == "system":
            compressed.append(messages[0])
            messages = messages[1:]
        
        # Add recent messages until we hit token limit
        current_tokens = sum(self.count_tokens(str(msg)) for msg in compressed)
        
        for msg in reversed(messages):
            msg_tokens = self.count_tokens(str(msg))
            if current_tokens + msg_tokens <= max_tokens:
                compressed.insert(-1 if compressed and compressed[0].get("role") == "system" else 0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        return compressed
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """Generate AI response with fallback between models"""
        
        model = model or settings.DEFAULT_MODEL
        temperature = temperature or settings.TEMPERATURE
        max_tokens = max_tokens or settings.MAX_TOKENS
        
        # Compress context if needed
        messages = self.compress_context(messages, settings.CONTEXT_WINDOW_SIZE)
        
        try:
            if model.startswith("gpt") and self.openai_client:
                return await self._openai_request(messages, model, temperature, max_tokens)
            elif model.startswith("claude") and self.claude_client:
                return await self._claude_request(messages, model, temperature, max_tokens)
            else:
                # Fallback to available model
                if self.openai_client:
                    return await self._openai_request(messages, "gpt-3.5-turbo", temperature, max_tokens)
                elif self.claude_client:
                    return await self._claude_request(messages, "claude-3-haiku-20240307", temperature, max_tokens)
                else:
                    raise Exception("No AI models available")
        
        except Exception as e:
            # Fallback response
            return {
                "content": "I apologize, but I'm having trouble processing your request right now. Could you please try again?",
                "tokens_used": 0,
                "model_used": "fallback",
                "error": str(e)
            }
    
    async def _openai_request(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Make OpenAI API request"""
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "model_used": model,
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _claude_request(self, messages: List[Dict], model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Make Claude API request"""
        # Convert messages format for Claude
        system_message = ""
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append(msg)
        
        response = await self.claude_client.messages.create(
            model=model,
            system=system_message,
            messages=claude_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.content[0].text,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "model_used": model,
            "finish_reason": response.stop_reason
        }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotion in text"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Analyze the sentiment and emotions in the given text. Return a JSON response with:
                    {
                        "sentiment": "positive/negative/neutral",
                        "confidence": 0.0-1.0,
                        "emotions": {
                            "joy": 0.0-1.0,
                            "sadness": 0.0-1.0,
                            "anger": 0.0-1.0,
                            "fear": 0.0-1.0,
                            "surprise": 0.0-1.0,
                            "disgust": 0.0-1.0
                        },
                        "tone": "formal/casual/friendly/professional/etc",
                        "urgency": 0.0-1.0
                    }"""
                },
                {"role": "user", "content": text}
            ]
            
            response = await self.generate_response(messages, temperature=0.1, max_tokens=200)
            
            try:
                return json.loads(response["content"])
            except json.JSONDecodeError:
                # Fallback analysis
                return {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "emotions": {"joy": 0.3, "sadness": 0.1, "anger": 0.1, "fear": 0.1, "surprise": 0.2, "disgust": 0.1},
                    "tone": "casual",
                    "urgency": 0.3
                }
        
        except Exception:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": {"joy": 0.3, "sadness": 0.1, "anger": 0.1, "fear": 0.1, "surprise": 0.2, "disgust": 0.1},
                "tone": "casual",
                "urgency": 0.3
            }
