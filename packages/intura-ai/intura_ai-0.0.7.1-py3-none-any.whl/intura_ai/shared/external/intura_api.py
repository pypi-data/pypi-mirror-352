import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Union, List, TypedDict
from uuid import uuid4
from intura_ai import __version__
from intura_ai.shared.variables.api_host import INTURA_API_HOST
from intura_ai.shared.utils.logging import get_component_logger

# Get component-specific logger
logger = get_component_logger("intura_api")

class InturaAPIError(Exception):
    """Exception raised for Intura API errors."""
    pass

class ChatMessage(TypedDict):
    """Type definition for chat messages."""
    role: str
    content: str

class InturaFetch:
    """
    Client for interacting with the Intura API.
    
    This class provides methods to communicate with various Intura API endpoints
    for experiment management, model building, and logging.
    """
    
    # API endpoints
    ENDPOINTS = {
        # Authentication and validation
        "validate_api_key": "external/validate-api-key",
        "validate_experiment": "external/validate-experiment",
        
        # Inference and logging
        "insert_inference": "reward/insert/inference",
        
        # Experiment management
        "create_experiment": "experiment/create",
        "list_models": "experiment/models/list",
        "list_experiment": "experiment/list",
        "experiment_detail": "experiment/{experiment_id}/detail",
        "build_chat_model": "ai/build/chat",
        "invoke_chat_model": "experiment/inference/chat",
        
        # Tracking and rewards
        "track_reward": "ai/track"
    }
    
    def __init__(self, intura_api_key: Optional[str] = None, intura_api_host: Optional[str] = None, verbose: bool = False):
        """
        Initialize the Intura API client.
        
        Args:
            intura_api_key: API key for authentication (falls back to INTURA_API_KEY env var)
            verbose: Enable verbose logging for this component
        """
        self._api_host = intura_api_host or INTURA_API_HOST
        self._api_version = "v1"
        
        # Get API key from parameter or environment
        api_key = intura_api_key or os.environ.get("INTURA_API_KEY")
        if not api_key:
            logger.error("API key not found. Please provide an API key or set the INTURA_API_KEY environment variable.")
            raise ValueError("API key not found. Please provide an API key or set the INTURA_API_KEY environment variable.")
        
        # Configure component-specific logging if verbose is specified
        if verbose:
            from intura_ai.shared.utils.logging import set_component_level
            set_component_level("intura_api", "debug")
        
        # Initialize headers
        self._headers = self._create_headers(api_key)    
        logger.debug("Intura API client initialized successfully")
    
    def _create_headers(self, api_key: str) -> Dict[str, str]:
        """
        Create HTTP headers for API requests.
        
        Args:
            api_key: API key for authentication
            
        Returns:
            Dictionary of HTTP headers
        """
        return {
            'x-request-id': str(uuid4()),
            'x-timestamp': str(int(datetime.now().timestamp() * 1000)),
            'x-api-key': api_key,
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'source': f'Python;intura-ai;{__version__}'
        }
    
    def _get_endpoint_url(self, endpoint_key: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build the full URL for an API endpoint.
        
        Args:
            endpoint_key: Key of the endpoint in the ENDPOINTS dictionary
            
        Returns:
            Full URL for the endpoint
            
        Raises:
            ValueError: If the endpoint key is not found in ENDPOINTS
        """
        if endpoint_key not in self.ENDPOINTS:
            raise ValueError(f"Invalid endpoint: {endpoint_key}. Please check the available endpoints.")
        
        if endpoint_key in ["experiment_detail"]:
            return "/".join([self._api_host, self._api_version, self.ENDPOINTS[endpoint_key].format(experiment_id=params.get("experiment_id"))])
        else:
            return "/".join([self._api_host, self._api_version, self.ENDPOINTS[endpoint_key]])
    
    def _make_request(
        self, 
        method: str, 
        endpoint_key: str, 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Make an HTTP request to the Intura API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint_key: Key of the endpoint in the ENDPOINTS dictionary
            params: URL parameters
            data: Request data (for POST/PUT)
            json_data: JSON data (for POST/PUT)
            
        Returns:
            Response data on success, None on failure
            
        Raises:
            InturaAPIError: If the API request fails
        """
        url = self._get_endpoint_url(endpoint_key, params)
        
        # Update request ID and timestamp for each request
        self._headers.update({
            'x-request-id': str(uuid4()),
            'x-timestamp': str(int(datetime.now().timestamp() * 1000)),
        })
        
        try:
            logger.debug(f"Sending {method} request to {url}")
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=self._headers)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, data=data, json=json_data, headers=self._headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}. Please use GET or POST.")
            
            # Log response code
            logger.debug(f"Received response with status code: {response.status_code}")
            
            if response.status_code == 200:
                # For endpoints that return JSON
                if response.headers.get('Content-Type', '').startswith('application/json'):
                    return response.json()
                # For endpoints that return plain text or other formats
                return {"status": "success", "code": response.status_code}
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text[:100]}"
                logger.warning(error_msg)
                return None
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise InturaAPIError(error_msg)
    
    def _check_api_key(self) -> bool:
        """
        Validate the API key.
        
        Returns:
            True if valid, False otherwise
        """
        logger.debug("Validating API key")
        result = self._make_request("GET", "validate_api_key")
        return result is not None
    
    def get_list_experiment(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get a list of experiments.
        
        Returns:
            List of experiments or None if the request fails
        """
        logger.debug("Retrieving list of experiments")
        response = self._make_request("GET", "list_experiment")
        return response.get("data") if response else None
    
    def insert_experiment(self, payload: Union[Dict[str, Any], str]) -> Optional[str]:
        """
        Create a new experiment.
        
        Args:
            payload: Experiment data
            
        Returns:
            Experiment ID on success, None on failure
        """
        logger.debug("Creating new experiment")
        response = self._make_request("POST", "create_experiment", data=payload)
        if response and "data" in response and "experiment_id" in response["data"]:
            experiment_id = response["data"]["experiment_id"]
            logger.info(f"Successfully created experiment with ID: {experiment_id}")
            return experiment_id
        return None
    
    def get_list_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get a list of available models.
        
        Returns:
            List of models or None if the request fails
        """
        logger.debug("Retrieving list of available models")
        response = self._make_request("GET", "list_models")
        return response.get("data") if response else None
    
    def check_experiment_id(self, experiment_id: str) -> bool:
        """
        Check if an experiment ID is valid.
        
        Args:
            experiment_id: ID of the experiment to check
            
        Returns:
            True if valid, False otherwise
        """
        logger.debug(f"Validating experiment ID: {experiment_id}")
        params = {"experiment_id": experiment_id}
        response = self._make_request("GET", "validate_experiment", params=params)
        return response is not None
    
    def get_experiment_detail(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Experiment details or None if the request fails
        """
        logger.debug(f"Retrieving details for experiment: {experiment_id}")
        params = {"experiment_id": experiment_id}
        response = self._make_request("GET", "experiment_detail", params=params)
        return response.get("data") if response else None

    
    def build_chat_model(
        self, 
        experiment_id: str, 
        treatment_id: Optional[str] = None,
        request_id: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None,
        messages: Optional[List[ChatMessage]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Build a chat model based on an experiment configuration.
        
        Args:
            experiment_id: ID of the experiment
            treatment_id: ID of the treatment
            request_id: ID of the request
            features: Features to include in the model
            messages: Optional list of chat messages for model training
            
        Returns:
            Model configuration or None if the request fails
        """
        logger.debug(f"Building chat model for experiment: {experiment_id}")
        features = features or {}
        messages = messages or []
        
        json_data = {
            "experiment_id": experiment_id,
            "treatment_id": treatment_id,
            "request_id": request_id,
            "features": features,   
            "messages": messages,
        }
        
        
        return self._make_request(
            "POST", "build_chat_model", json_data=json_data
        )
        
    def inference_chat_model(
        self, 
        experiment_id: str, 
        treatment_id: Optional[str] = None,
        request_id: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None, 
        messages: Optional[List[ChatMessage]] = None,
        session_id: Optional[str] = None, 
        max_inferences: int = 1,
        latency_threshold: int = 30,
        max_timeout: int = 120
    ) -> Optional[Dict[str, Any]]:
        """
        Perform inference using a chat model.
        
        Args:
            experiment_id: ID of the experiment
            treatment_id: ID of the treatment
            request_id: ID of the request
            features: Features to include in the inference
            messages: List of chat messages for inference
            session_id: Optional session ID for tracking
            max_inferences: Maximum number of inferences to perform
            latency_threshold: Maximum allowed latency in seconds
            max_timeout: Maximum timeout in seconds
            
        Returns:
            Inference results or None if the request fails
        """
        logger.debug(f"Performing inference with chat model for experiment: {experiment_id}")
        features = features or {}
        json_data = {
            "features": features, 
            "experiment_id": experiment_id,
            "treatment_id": treatment_id,
            "request_id": request_id,
            "messages": messages, 
            "session_id": session_id,
            "max_inferences": max_inferences,
            "latency_threshold": latency_threshold,
            "max_timeout": max_timeout
        }
        
        return self._make_request(
            "POST", "invoke_chat_model", json_data=json_data
        )
    
    def insert_log_inference(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Log inference data.
        
        Args:
            payload: Inference data
            
        Returns:
            Response data or None if the request fails
        """
        try:
            session_id = payload.get("session_id", "unknown")
            logger.debug(f"Logging inference data for session: {session_id}")
            
            return self._make_request("POST", "insert_inference", json_data=payload)
        except Exception as e:
            logger.error(f"Failed to log inference data: {str(e)}")
            return None
    
    def _track_event(
        self, 
        event_name: str, 
        event_value: Any, 
        reward_category: str,
        prediction_id: Optional[str] = None
    ) -> bool:
        """
        Track an event in the Intura system.
        
        Args:
            event_name: Name of the event
            event_value: Value/data for the event
            reward_category: Category of the reward
            prediction_id: Optional prediction ID
            
        Returns:
            True on success, False on failure
        """
        prediction_id = prediction_id or str(uuid4())
        
        request_body = {
            "body": {
                "event_name": event_name,
                "event_value": event_value,
                "attributes": {},
                "prediction_id": prediction_id
            },
            "reward_type": "RESERVED_REWARD",
            "reward_category": reward_category
        }
        
        logger.debug(f"Tracking event '{event_name}' in category '{reward_category}'")
        response = self._make_request("POST", "track_reward", json_data=request_body)
        
        return response is not None
    
    def insert_chat_usage(self, values: Any) -> bool:
        """
        Log chat model usage.
        
        Args:
            values: Usage data
            
        Returns:
            True on success, False on failure
        """
        logger.debug("Logging chat model usage")
        return self._track_event(
            event_name="CHAT_MODEL_USAGE",
            event_value=values,
            reward_category="CHAT_USAGE"
        )
    
    def insert_chat_output(self, values: Any) -> bool:
        """
        Log chat model output.
        
        Args:
            values: Output data
            
        Returns:
            True on success, False on failure
        """
        return self._track_event(
            event_name="CHAT_MODEL_OUTPUT",
            event_value=values,
            reward_category="CHAT_LOG"
        )
    
    def insert_chat_input(self, values: Any) -> bool:
        """
        Log chat model input.
        
        Args:
            values: Input data
            
        Returns:
            True on success, False on failure
        """
        return self._track_event(
            event_name="CHAT_MODEL_INPUT",
            event_value=values,
            reward_category="CHAT_LOG"
        )