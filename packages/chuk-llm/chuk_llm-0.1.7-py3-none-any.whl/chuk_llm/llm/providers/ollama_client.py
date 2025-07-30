# chuk_llm/llm/providers/ollama_client.py
"""
Ollama chat-completion adapter.
"""
import asyncio
import json
import logging
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional, Union

# provider
import ollama

# providers
from chuk_llm.llm.core.base import BaseLLMClient

log = logging.getLogger(__name__)

class OllamaLLMClient(BaseLLMClient):
    """Wrapper around `ollama` SDK supporting both sync and async interfaces."""

    def __init__(self, model: str = "qwen3", api_base: Optional[str] = None) -> None:
        """
        Initialize Ollama client.
        
        Args:
            model: Name of the model to use
            api_base: Optional API base URL (will be applied if ollama.set_host is available)
        """
        self.model = model
        self.api_base = api_base
        
        # Configure the API base if provided and if the library supports it
        if api_base and hasattr(ollama, 'set_host'):
            log.info(f"Setting Ollama host to: {api_base}")
            ollama.set_host(api_base)
        elif api_base:
            log.warning(f"Ollama client doesn't support set_host; api_base '{api_base}' will be ignored")
        
        # Verify that the installed ollama package supports chat
        if not hasattr(ollama, 'chat'):
            raise ValueError(
                "The installed ollama package does not expose 'chat'; "
                "check your ollama-python version."
            )
        
        # Create sync and async clients
        self.async_client = ollama.AsyncClient()
        self.sync_client = ollama.Client()

    def _create_sync(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous internal completion call.
        """
        # Prepare messages as expected by Ollama
        ollama_messages = []
        for m in messages:
            message = {"role": m.get("role"), "content": m.get("content")}
            
            # Handle images if present in the message content
            if isinstance(m.get("content"), list):
                for item in m.get("content", []):
                    if item.get("type") == "image" or item.get("type") == "image_url":
                        image_url = item.get("image_url", {}).get("url", "")
                        if image_url.startswith("data:image"):
                            # Extract base64 data and convert to proper format
                            import base64
                            _, encoded = image_url.split(",", 1)
                            message["images"] = [base64.b64decode(encoded)]
                        else:
                            message["images"] = [image_url]
            
            ollama_messages.append(message)
        
        # Convert tools to Ollama format if needed
        ollama_tools = []
        if tools:
            for tool in tools:
                # Ollama expects a specific format for tools
                if "function" in tool:
                    fn = tool["function"]
                    ollama_tools.append({
                        "type": "function",
                        "function": {
                            "name": fn.get("name"),
                            "description": fn.get("description", ""),
                            "parameters": fn.get("parameters", {})
                        }
                    })
                else:
                    # Pass through other tool formats
                    ollama_tools.append(tool)
        
        # Make the non-streaming sync call
        response = self.sync_client.chat(
            model=self.model,
            messages=ollama_messages,
            tools=ollama_tools or [],
            stream=False,
        )
        
        # Process response
        return self._parse_response(response)
    
    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """Parse Ollama response to standardized format."""
        main_text = ""
        tool_calls = []
        
        # Get message from response
        message = getattr(response, "message", None)
        if message:
            # Get content
            main_text = getattr(message, "content", "No response")
            
            # Process tool calls if any
            raw_tool_calls = getattr(message, "tool_calls", None)
            if raw_tool_calls:
                for tc in raw_tool_calls:
                    tc_id = getattr(tc, "id", None) or f"call_{uuid.uuid4().hex[:8]}"
                    
                    fn_name = getattr(tc.function, "name", "")
                    fn_args = getattr(tc.function, "arguments", {})
                    
                    # Ensure arguments are in string format
                    if isinstance(fn_args, dict):
                        fn_args_str = json.dumps(fn_args)
                    elif isinstance(fn_args, str):
                        fn_args_str = fn_args
                    else:
                        fn_args_str = str(fn_args)
                    
                    tool_calls.append({
                        "id": tc_id,
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "arguments": fn_args_str
                        }
                    })
        
        # If we have tool calls and no content, return null content
        if tool_calls and not main_text:
            return {"response": None, "tool_calls": tool_calls}
        
        return {"response": main_text, "tool_calls": tool_calls}
    
    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        *,
        stream: bool = False,
        **kwargs,
    ) -> Union[AsyncIterator[Dict[str, Any]], Any]:
        """
        Generate a chat completion with real streaming support.
        
        Args:
            messages: List of message dictionaries
            tools: Optional list of tools
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to the underlying API
            
        Returns:
            When stream=True: AsyncIterator that yields chunks in real-time
            When stream=False: Awaitable that resolves to completion dict
        """
        if stream:
            # Return async generator directly for real streaming
            return self._stream_completion_async(messages, tools, **kwargs)
        else:
            # Return awaitable for non-streaming
            return self._regular_completion(messages, tools, **kwargs)

    async def _stream_completion_async(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Real streaming using Ollama's AsyncClient without buffering.
        This provides true real-time streaming from Ollama's API.
        """
        try:
            # Prepare messages for Ollama
            ollama_messages = []
            for m in messages:
                message = {"role": m.get("role"), "content": m.get("content")}
                
                # Handle images if present
                if isinstance(m.get("content"), list):
                    for item in m.get("content", []):
                        if item.get("type") == "image" or item.get("type") == "image_url":
                            image_url = item.get("image_url", {}).get("url", "")
                            if image_url.startswith("data:image"):
                                # Extract base64 data
                                import base64
                                _, encoded = image_url.split(",", 1)
                                message["images"] = [base64.b64decode(encoded)]
                            else:
                                message["images"] = [image_url]
                
                ollama_messages.append(message)
            
            # Convert tools to Ollama format
            ollama_tools = []
            if tools:
                for tool in tools:
                    if "function" in tool:
                        fn = tool["function"]
                        ollama_tools.append({
                            "type": "function",
                            "function": {
                                "name": fn.get("name"),
                                "description": fn.get("description", ""),
                                "parameters": fn.get("parameters", {})
                            }
                        })
                    else:
                        ollama_tools.append(tool)
            
            log.debug("Starting Ollama streaming...")
            
            # Use async client for real streaming
            stream = await self.async_client.chat(
                model=self.model,
                messages=ollama_messages,
                tools=ollama_tools or [],
                stream=True,
                **kwargs
            )
            
            chunk_count = 0
            aggregated_tool_calls = []
            
            # Process each chunk in the stream immediately
            async for chunk in stream:
                chunk_count += 1
                
                # Get content from chunk
                content = ""
                if hasattr(chunk, 'message') and chunk.message:
                    content = getattr(chunk.message, "content", "")
                
                # Check for tool calls
                new_tool_calls = []
                if hasattr(chunk, 'message') and chunk.message:
                    chunk_tool_calls = getattr(chunk.message, "tool_calls", None)
                    if chunk_tool_calls:
                        for tc in chunk_tool_calls:
                            tc_id = getattr(tc, "id", None) or f"call_{uuid.uuid4().hex[:8]}"
                            
                            fn_name = getattr(tc.function, "name", "")
                            fn_args = getattr(tc.function, "arguments", {})
                            
                            # Process arguments
                            if isinstance(fn_args, dict):
                                fn_args_str = json.dumps(fn_args)
                            elif isinstance(fn_args, str):
                                fn_args_str = fn_args
                            else:
                                fn_args_str = str(fn_args)
                            
                            tool_call = {
                                "id": tc_id,
                                "type": "function",
                                "function": {
                                    "name": fn_name,
                                    "arguments": fn_args_str
                                }
                            }
                            new_tool_calls.append(tool_call)
                            aggregated_tool_calls.append(tool_call)
                
                # Yield chunk immediately if we have content or tool calls
                if content or new_tool_calls:
                    yield {
                        "response": content,
                        "tool_calls": new_tool_calls
                    }
                
                # Allow other async tasks to run periodically
                if chunk_count % 5 == 0:
                    await asyncio.sleep(0)
            
            log.debug(f"Ollama streaming completed with {chunk_count} chunks")
        
        except Exception as e:
            log.error(f"Error in Ollama streaming: {e}")
            yield {
                "response": f"Streaming error: {str(e)}",
                "tool_calls": [],
                "error": True
            }

    async def _regular_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Non-streaming completion using async execution."""
        try:
            return await asyncio.to_thread(self._create_sync, messages, tools)
        except Exception as e:
            log.error(f"Error in Ollama completion: {e}")
            return {
                "response": f"Error: {str(e)}",
                "tool_calls": [],
                "error": True
            }