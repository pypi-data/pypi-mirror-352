import requests
from functools import wraps
from typing import Any, Dict, List, Callable, Optional
import functools
import asyncio
import jsonpickle
from contextvars import ContextVar
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

# Create context variable for agent_log_id
agent_log_id: ContextVar[Optional[str]] = ContextVar('agent_log_id', default=None)

class HanditTracker:
    def __init__(self):
        self.tracking_server_url = "https://handit-api-299768392189.us-central1.run.app/api/track"
        self.sso_tracking_server_url = "https://handit-api-oss-299768392189.us-central1.run.app/api/track"
        self.performance_server_url = "https://handit-api-299768392189.us-central1.run.app/api/performance"
        self.api_key = None
        self.urls_to_track = []

    def config(self, api_key, tracking_url=None):
        if not api_key:
            raise ValueError("API key is required for configuration.")
        self.api_key = api_key
        if tracking_url:
            self.tracking_server_url = tracking_url

    def update_tracked_urls(self):
        if not self.api_key:
            raise ValueError("API key not set. Call the config method with your API key.")
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(f"{self.tracking_server_url}/urls-to-track", headers=headers)
            response.raise_for_status()
            self.urls_to_track = response.json()
        except requests.RequestException as e:
            print(f"")

    def intercept_requests(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.update_tracked_urls()
            url = args[0]
            matching_url = next((u for u in self.urls_to_track if u["url"] in url), None)
            if matching_url:
                model_id = matching_url["id"]
                request_body = kwargs.get("json", kwargs.get("data"))
                
                try:
                    response = func(*args, **kwargs)
                    response_body = response.json()
                    self._send_tracked_data(model_id, request_body, response_body)
                    return response
                except Exception as e:
                    print(f"")
                    raise
            else:
                return func(*args, **kwargs)
        return wrapper

    def capture_model(self, model_id, request_body, response_body):
        try:
            self._send_tracked_data(model_id, request_body, response_body)
        except Exception as e:
            print(f"")

    def _sanitize_and_serialize(self, obj: Any) -> Any:
        """Sanitize sensitive data and serialize objects"""
        try:
            # Handle None case explicitly
            if obj is None:
                return None
                
            # Special handling for Pinecone results
            if hasattr(obj, 'matches') and hasattr(obj, 'namespace'):
                return {
                    'matches': [
                        {
                            'id': match.id,
                            'score': match.score,
                            'metadata': match.metadata
                        } for match in obj.matches
                    ],
                    'namespace': obj.namespace,
                }
            
            # Handle common Python types that need special treatment
            if isinstance(obj, (str, int, float, bool)):
                return obj
            
            # Convert to JSON-compatible format
            serialized = jsonpickle.encode(obj, unpicklable=False)
            # Then sanitize any sensitive data
            sanitized = jsonpickle.decode(serialized)
            return sanitized
        except Exception as e:
            logger.warning(f"Error serializing object: {str(e)}")
            # Return a safe representation of the object
            if hasattr(obj, '__dict__'):
                return f"<{obj.__class__.__name__} object>"
            return str('')

    async def _end_agent_tracing(self, error: Optional[Exception] = None):
        """End agent tracing and optionally report error"""
        try:
            current_agent_log_id = agent_log_id.get(None)
            if not current_agent_log_id:
                return

            payload = {"agentLogId": current_agent_log_id}
            
            if error:
                payload.update({
                    "error": str(error),
                    "stack": getattr(error, '__traceback__', 'No stack trace available')
                })

            headers = {"Authorization": f"Bearer {self.api_key}"}
            await self._async_post(f"{self.tracking_server_url}/end", payload, headers)
        except Exception as e:
            logger.warning(f"Error ending agent tracing: {e}")

    async def _async_post(self, url: str, data: Dict, headers: Dict):
        """Async HTTP POST helper"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    return await response.json()
        except Exception as e:
            logger.warning(f"Error in async POST: {e}")
            return None

    def start_agent_tracing(self):
        """
        Decorator to trace full agent execution.
        Supports both async and sync functions.
        """
        def decorator(func: Callable):
            # For async functions
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                token = agent_log_id.set(None)
                try:
                    result = await func(*args, **kwargs)
                    await self._end_agent_tracing()
                    return result
                except Exception as e:
                    await self._end_agent_tracing(error=e)
                    raise
                finally:
                    agent_log_id.reset(token)

            # For sync functions
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                token = agent_log_id.set(None)
                try:
                    result = func(*args, **kwargs)
                    # Use synchronous version for sync functions
                    self._end_agent_tracing_sync()
                    return result
                except Exception as e:
                    self._end_agent_tracing_sync(error=e)
                    raise
                finally:
                    agent_log_id.reset(token)

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator

    def trace_agent_node(self, agent_node_id: str):
        """
        Decorator to trace individual agent node execution.
        Supports both async and sync functions.
        """
        def decorator(func: Callable):
            # For async functions
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    try:
                        await self._send_tracked_data(
                            model_id=agent_node_id,
                            request_body=self._sanitize_and_serialize(
                                args[0] if len(args) == 1 else args
                            ),
                            response_body=self._sanitize_and_serialize(result)
                        )
                    except Exception as e:
                        logger.warning(f"Error tracking agent node: {e}")
                    return result
                except Exception as original_error:
                    try:
                        await self._send_tracked_data(
                            model_id=agent_node_id,
                            request_body=self._sanitize_and_serialize(
                                args[0] if len(args) == 1 else args
                            ),
                            response_body={
                                "error": str(original_error),
                                "stack": getattr(original_error, '__traceback__', 'No stack trace available')
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Error tracking agent node error: {e}")
                    raise original_error

            # For sync functions
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    try:
                        self._send_tracked_data_sync(
                            model_id=agent_node_id,
                            request_body=self._sanitize_and_serialize(
                                args[0] if len(args) == 1 else args
                            ),
                            response_body=self._sanitize_and_serialize(result)
                        )
                    except Exception as e:
                        logger.warning(f"Error tracking agent node: {e}")
                    return result
                except Exception as original_error:
                    try:
                        self._send_tracked_data_sync(
                            model_id=agent_node_id,
                            request_body=self._sanitize_and_serialize(
                                args[0] if len(args) == 1 else args
                            ),
                            response_body={
                                "error": str(original_error),
                                "stack": getattr(original_error, '__traceback__', 'No stack trace available')
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Error tracking agent node error: {e}")
                    raise original_error

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator

    def clean_payload(self, payload):
        cleaned = {}
        for k, v in payload.items():
            try:
                json.dumps(v)  # Test if serializable
                cleaned[k] = v
            except (TypeError, OverflowError):
                cleaned[k] = str(v)  # Fallback to string conversion
        return cleaned

    def start_tracing(self, agent_name: str):
        """
        Start tracing an agent.
        """
        return self._sso_start_tracing(agent_name)
    
    def end_tracing(self, execution_id: str, agent_name = None):
        """
        End tracing an agent.
        """
        return self._sso_end_tracing(execution_id, agent_name)
    
    def track_node(self, input, output, node_name, agent_name, node_type, execution_id):
        """
        Send tracked data to the SSO tracking server.
        """
        if node_type == "llm":
            node_type = "model"
        return self._sso_send_tracked_data(input, output, node_name, agent_name, node_type, execution_id)

    def _sso_start_tracing(self, agent_name: str):
        """
        Start tracing an agent.
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "agentName": agent_name
            }
            response = requests.post(
                self.sso_tracking_server_url + "/start",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error starting agent tracing: {e}")
            return None

    def _sso_end_tracing(self, execution_id: str, agent_name = None):
        """
        End tracing an agent.
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "agentName": agent_name,
                "executionId": execution_id
            }
            response = requests.post(
                self.sso_tracking_server_url + "/end",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
        except Exception as e:
            logger.warning(f"Error ending agent tracing: {e}")
            return None

    def _sso_send_tracked_data(self, input, output, node_name, agent_name, node_type, execution_id):
        """
        Send tracked data to the SSO tracking server.
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "input": input,
                "output": output,
                "nodeName": node_name,
                "agentName": agent_name,
                "nodeType": node_type,
                "executionId": execution_id
            }
            response = requests.post(
                self.sso_tracking_server_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error sending tracked data: {e}")
            return None

    def _send_tracked_data_sync(self, model_id, request_body, response_body):
        """Synchronous version of _send_tracked_data"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}

            payload = {
                "input": request_body,
                "output": response_body,
                "modelId": model_id,
                "parameters": {},
                "agentLogId": agent_log_id.get(None)
            }
            payload = self.clean_payload(payload)
            
            response = requests.post(
                self.tracking_server_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Update agent_log_id if provided in response
            if response_data and 'agentLogId' in response_data:
                agent_log_id.set(response_data['agentLogId'])
                
            return response_data
        except Exception as e:
            logger.warning(f"Error sending tracked data: {e}")
            return None

    def _end_agent_tracing_sync(self, error: Optional[Exception] = None):
        """Synchronous version of _end_agent_tracing"""
        try:
            current_agent_log_id = agent_log_id.get(None)
            if not current_agent_log_id:
                return

            payload = {"agentLogId": current_agent_log_id}
            
            if error:
                payload.update({
                    "error": str(error),
                    "stack": getattr(error, '__traceback__', 'No stack trace available')
                })

            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(
                f"{self.tracking_server_url}/end",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
        except Exception as e:
            logger.warning(f"Error ending agent tracing: {e}")

    async def _send_tracked_data(self, model_id, request_body, response_body):
        """Modified to include agent_log_id in tracking data"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "input": request_body,
                "output": response_body,
                "modelId": model_id,
                "parameters": {},
                "agentLogId": agent_log_id.get(None)
            }
            
            response = await self._async_post(self.tracking_server_url, payload, headers)
            
            # Update agent_log_id if provided in response
            if response and 'agentLogId' in response:
                agent_log_id.set(response['agentLogId'])
                
            return response
        except Exception as e:
            logger.warning(f"Error sending tracked data: {e}")
            return None

    def fetch_optimized_prompt(self, model_id):
        """
        Fetches the most optimized prompt for a given model ID.
        
        Args:
            model_id (str): The ID of the model to fetch the optimized prompt for.
            
        Returns:
            dict: The optimized prompt data
            
        Raises:
            ValueError: If API key is not configured
            requests.RequestException: If the API request fails
        """
        if not self.api_key:
            raise ValueError("API key not set. Call the config method with your API key.")
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.performance_server_url}/model/{model_id}/optimized-prompt"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"")
            raise

    def track_model(self, model, model_id):
        """
        Creates a tracked version of an AI model (LLM, embedding model, etc.)
        
        Args:
            model: The model to track (ChatOpenAI, OpenAIEmbeddings, etc.)
            model_id (str): The ID of the model to track
            
        Returns:
            Modified model with tracking capabilities
        """
        original_call = model.__call__
        
        async def tracked_call(*args, **kwargs):
            try:
                # Track model input
                self._send_tracked_data(
                    model_id=model_id,
                    request_body={
                        "type": "model_call",
                        "model_type": model.__class__.__name__,
                        "messages": kwargs.get("messages", []),
                        "prompt": kwargs.get("prompt", ""),
                        "parameters": {
                            k: v for k, v in kwargs.items()
                            if k not in ["messages", "prompt"]
                        }
                    },
                    response_body=None
                )
                
                # Execute model
                result = await original_call(*args, **kwargs)
                
                # Track model output
                self._send_tracked_data(
                    model_id=model_id,
                    request_body={
                        "type": "model_response",
                        "model_type": model.__class__.__name__
                    },
                    response_body={
                        "response": str(result)
                    }
                )
                
                return result
            except Exception as e:
                print(f"")
                raise
        
        model.__call__ = tracked_call
        return model

    def track_tool(self, tool, tool_id):
        """
        Creates a tracked version of a tool (RAG, API call, function, etc.)
        
        Args:
            tool: The tool to track
            tool_id (str): The ID of the tool to track
            
        Returns:
            Modified tool with tracking capabilities
        """
        original_call = tool.__call__ if hasattr(tool, '__call__') else tool
        
        async def tracked_call(*args, **kwargs):
            try:
                # Track tool input
                self._send_tracked_data(
                    model_id=tool_id,  # using model_id field for tool_id
                    request_body={
                        "type": "tool_call",
                        "tool_type": tool.__class__.__name__,
                        "inputs": {
                            "args": args,
                            "kwargs": kwargs
                        }
                    },
                    response_body=None
                )
                
                # Execute tool
                result = await original_call(*args, **kwargs)
                
                # Track tool output
                self._send_tracked_data(
                    model_id=tool_id,
                    request_body={
                        "type": "tool_response",
                        "tool_type": tool.__class__.__name__
                    },
                    response_body={
                        "result": result
                    }
                )
                
                return result
            except Exception as e:
                print(f"")
                raise
        
        if hasattr(tool, '__call__'):
            tool.__call__ = tracked_call
            return tool
        else:
            return tracked_call

    async def trace_agent_node_func(self, func: Callable, *args, key: str = None, **kwargs):
        """
        Async function to trace any function call, supporting both sync and async functions.
        
        Args:
            func (Callable): The function to trace
            *args: Positional arguments for the function
            key (str, optional): The tracking key. If not provided, uses function name
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
        """
        tracking_key = key or func.__name__
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Track successful execution
            try:
                data = {}
                try:
                    data = {
                        "args":self._sanitize_and_serialize(
                            args[0] if len(args) == 1 else args
                        ),
                        "kwargs": self._sanitize_and_serialize(kwargs)
                    }
                except Exception as e:
                    data = {"error": "Error serializing arguments"}

                await self._send_tracked_data(
                    model_id=tracking_key,
                    request_body=data,
                    response_body=self._sanitize_and_serialize(result)
                )
            except Exception as e:
                logger.warning(f"Error tracking function: {e}")

            return result
        except Exception as original_error:
            # Track error case
            try:
                data = {}
                try:
                    data = {
                        "args":self._sanitize_and_serialize(
                            args[0] if len(args) == 1 else args
                        ),
                        "kwargs": self._sanitize_and_serialize(kwargs)
                    }
                except Exception as e:
                    data = {"error": "Error serializing arguments"}

                await self._send_tracked_data(
                    model_id=tracking_key,
                    request_body=data,
                    response_body={
                        "error": str(original_error),
                        "stack": getattr(original_error, '__traceback__', 'No stack trace available')
                    }
                )
            except Exception as e:
                logger.warning(f"Error tracking function error: {e}")
            raise original_error

    def trace_agent_node_func_sync(self, func: Callable, *args, key: str = None, **kwargs):
        """
        Sync version of trace_agent_node_func
        """
        tracking_key = key or func.__name__
        
        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Track successful execution
            try:
                data = {}
                try:
                    data = {
                        "args":self._sanitize_and_serialize(
                            args[0] if len(args) == 1 else args
                        ),
                        "kwargs": self._sanitize_and_serialize(kwargs)
                    }
                except Exception as e:
                    data = {"error": "Error serializing arguments"}
                self._send_tracked_data_sync(
                    model_id=tracking_key,
                    request_body=data,
                    response_body=self._sanitize_and_serialize(result)
                )
            except Exception as e:
                logger.warning(f"Error tracking function: {e}")

            return result
        except Exception as original_error:
            # Track error case
            try:
                data = {}
                try:
                    data = {
                        "args":self._sanitize_and_serialize(
                            args[0] if len(args) == 1 else args
                        ),
                        "kwargs": self._sanitize_and_serialize(kwargs)
                    }
                except Exception as e:
                    data = {"error": "Error serializing arguments"}
                self._send_tracked_data_sync(
                    model_id=tracking_key,
                    request_body=data,
                    response_body={
                        "error": str(original_error),
                        "stack": getattr(original_error, '__traceback__', 'No stack trace available')
                    }
                )
            except Exception as e:
                logger.warning(f"Error tracking function error: {e}")
            raise original_error

    # Async versions of the SSO tracking functions
    async def start_tracing_async(self, agent_name: str):
        """
        Async version: Start tracing an agent.
        """
        return await self._sso_start_tracing_async(agent_name)
    
    async def end_tracing_async(self, execution_id: str, agent_name = None):
        """
        Async version: End tracing an agent.
        """
        return await self._sso_end_tracing_async(execution_id, agent_name)
    
    async def track_node_async(self, input, output, node_name, agent_name, node_type, execution_id):
        """
        Async version: Send tracked data to the SSO tracking server.
        """
        if node_type == "llm":
            node_type = "model"
        return await self._sso_send_tracked_data_async(input, output, node_name, agent_name, node_type, execution_id)

    async def _sso_start_tracing_async(self, agent_name: str):
        """
        Async version: Start tracing an agent.
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "agentName": agent_name
            }
            response = await self._async_post(
                self.sso_tracking_server_url + "/start",
                payload,
                headers
            )
            return response
        except Exception as e:
            logger.warning(f"Error starting agent tracing: {e}")
            return None

    async def _sso_end_tracing_async(self, execution_id: str, agent_name = None):
        """
        Async version: End tracing an agent.
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "agentName": agent_name,
                "executionId": execution_id
            }
            await self._async_post(
                self.sso_tracking_server_url + "/end",
                payload,
                headers
            )
            return True
        except Exception as e:
            logger.warning(f"Error ending agent tracing: {e}")
            return None

    async def _sso_send_tracked_data_async(self, input, output, node_name, agent_name, node_type, execution_id):
        """
        Async version: Send tracked data to the SSO tracking server.
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "input": input,
                "output": output,
                "nodeName": node_name,
                "agentName": agent_name,
                "nodeType": node_type,
                "executionId": execution_id
            }
            response = await self._async_post(
                self.sso_tracking_server_url,
                payload,
                headers
            )
            return response
        except Exception as e:
            logger.warning(f"Error sending tracked data: {e}")
            return None
