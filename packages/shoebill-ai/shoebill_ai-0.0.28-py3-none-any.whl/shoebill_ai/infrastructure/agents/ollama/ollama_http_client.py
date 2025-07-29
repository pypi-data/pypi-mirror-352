import logging
import ollama
from typing import Dict, Any, Optional


class OllamaHttpClient:
    """
    Base HTTP client for the Ollama API using the ollama-python library.
    Handles authentication and common request functionality.
    """

    def __init__(self, api_url: str, api_token: str = None):
        """
        Initialize a new OllamaHttpClient.

        Args:
            api_url: The base URL of the Ollama API.
            api_token: Optional API token for authentication.
        """
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.logger = logging.getLogger(__name__)



        # Set up headers if API token is provided
        self.headers = {}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"

        # Configure the ollama client with the API URL
        self.client = ollama.Client(host=self.api_url, headers=self.headers)

    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for the request, including authentication if available.

        Returns:
            Dict[str, str]: The headers for the request.
        """
        return self.headers

    def post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a POST request to the Ollama API using the ollama-python library.

        Args:
            endpoint: The endpoint to send the request to (without the base URL).
            payload: The payload to send with the request.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if the request failed.
        """
        self.logger.info(f"OllamaHttpClient: Sending request to {endpoint} endpoint")
        self.logger.debug(f"OllamaHttpClient: Headers: {self.headers}")
        self.logger.debug(f"OllamaHttpClient: Payload: {payload}")

        try:

            # Route to the appropriate ollama-python method based on the endpoint
            if endpoint == "chat":
                # Extract required parameters for chat
                model = payload.get("model")
                messages = payload.get("messages", [])
                options = {
                    "temperature": payload.get("temperature"),
                    "seed": payload.get("seed"),
                    "stream": payload.get("stream", False)
                }
                # Remove None values from options
                options = {k: v for k, v in options.items() if v is not None}

                # Add images if present
                if "images" in payload:
                    options["images"] = payload.get("images", [])

                # Call the chat method
                response = self.client.chat(
                    model=model,
                    messages=messages,
                    options=options
                )

                # Format response to match the expected structure
                response_json = {
                    "message": {
                        "role": "assistant",
                        "content": response.get("message", {}).get("content", "")
                    }
                }

            elif endpoint == "generate":
                # Extract required parameters for generate
                model = payload.get("model")
                prompt = payload.get("prompt", "")
                system = payload.get("system")
                options = {
                    "temperature": payload.get("temperature"),
                    "seed": payload.get("seed"),
                    "num_ctx": payload.get("num_ctx"),
                    "stream": payload.get("stream", False)
                }
                # Remove None values from options
                options = {k: v for k, v in options.items() if v is not None}

                # Call the generate method
                response = self.client.generate(
                    model=model,
                    prompt=prompt,
                    system=system,
                    options=options
                )

                # Format response to match the expected structure
                response_json = {
                    "response": response.get("response", "")
                }

            elif endpoint == "embeddings":
                # Extract required parameters for embeddings
                model = payload.get("model")
                prompt = payload.get("prompt", "")

                # Call the embeddings method
                response = self.client.embeddings(
                    model=model,
                    prompt=prompt,
                )

                # Format response to match the expected structure
                response_json = {
                    "embedding": response.get("embedding", [])
                }

            else:
                self.logger.error(f"OllamaHttpClient: Unsupported endpoint: {endpoint}")
                return None

            self.logger.info(f"OllamaHttpClient: Received successful response from {endpoint} endpoint")

            # Log a truncated version of the response to avoid excessive logging
            if isinstance(response_json, dict):
                truncated_response = {k: str(v)[:100] + '...' if isinstance(v, str) and len(v) > 100 else v 
                                     for k, v in response_json.items()}
                self.logger.debug(f"OllamaHttpClient: Response body (truncated): {truncated_response}")

            return response_json

        except Exception as e:
            self.logger.error(f"OllamaHttpClient: Error during API call to {endpoint}: {e}")
            return None
