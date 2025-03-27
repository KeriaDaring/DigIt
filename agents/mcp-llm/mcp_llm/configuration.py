import json
import os
from typing import Any, Optional

import dotenv


class Configuration:
    """Manages configuration and environment variables for the MCP client."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.load_env()
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model_name = os.getenv("LLM_MODEL_NAME")

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file."""
        dotenv.load_dotenv()

    @staticmethod
    def load_config(file_path: str) -> dict[str, Any]:
        """Load server configuration from JSON file.

        Args:
            file_path: Path to the JSON configuration file.

        Returns:
            Dict containing server configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            JSONDecodeError: If configuration file is invalid JSON.
        """
        with open(file_path, "r") as f:
            return json.load(f)

    @property
    def llm_api_key(self) -> str:
        """Get the LLM API key.

        Returns:
            The API key as a string.

        Raises:
            ValueError: If the API key is not found in environment variables.
        """
        if not self.api_key:
            raise ValueError("LLM_API_KEY not found in environment variables")
        return self.api_key

    @property
    def llm_base_url(self) -> Optional[str]:
        """Get the LLM base URL.

        Returns:
            The base URL as a string.
        """
        return self.base_url

    @property
    def llm_model_name(self) -> str:
        """Get the LLM model name.

        Returns:
            The model name as a string.

        Raises:
            ValueError: If the model name is not found in environment variables.
        """
        if not self.model_name:
            raise ValueError("LLM_MODEL_NAME not found in environment variables")
        return self.model_name
