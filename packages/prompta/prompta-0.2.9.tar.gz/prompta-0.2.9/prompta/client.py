"""HTTP client for communicating with the Prompta API."""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlencode

import httpx

from . import __version__
from .config import Config
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    PromptaAPIError,
    ValidationError,
)


class PromptaClient:
    """HTTP client for the Prompta API."""

    def __init__(self, api_key: str, config: Optional[Config] = None):
        """Initialize the Prompta API client.

        Args:
            api_key: API key for authentication
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.api_key = api_key
        self.base_url = self.config.api_url.rstrip("/")
        self.timeout = self.config.api_timeout

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"prompta-cli/{__version__}",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        skip_auth: bool = False,
    ) -> Any:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            skip_auth: Skip authentication headers (for login)

        Returns:
            Response data

        Raises:
            AuthenticationError: For 401 errors
            NotFoundError: For 404 errors
            ValidationError: For 422 errors
            PromptaAPIError: For other API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if skip_auth:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"prompta-cli/{__version__}",
            }
        else:
            headers = self._get_headers()

        try:
            with httpx.Client(
                timeout=self.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=True,
            ) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                )

                # Handle different status codes
                if response.status_code == 401:
                    error_detail = self._extract_error_detail(response)
                    raise AuthenticationError(error_detail, response.status_code)
                elif response.status_code == 404:
                    error_detail = self._extract_error_detail(response)
                    raise NotFoundError(error_detail, response.status_code)
                elif response.status_code == 422:
                    error_detail = self._extract_error_detail(response)
                    raise ValidationError(error_detail, response.status_code)
                elif response.status_code >= 400:
                    error_detail = self._extract_error_detail(response)
                    raise PromptaAPIError(error_detail, response.status_code)

                # For successful DELETE requests, return None
                if response.status_code == 204:
                    return None

                # Parse JSON response
                return response.json()

        except httpx.RequestError as e:
            raise PromptaAPIError(f"Request failed: {str(e)}")

    def _extract_error_detail(self, response: httpx.Response) -> str:
        """Extract error detail from response."""
        try:
            error_data = response.json()
            if isinstance(error_data.get("detail"), list):
                # Validation errors
                errors = []
                for error in error_data["detail"]:
                    field = ".".join(str(loc) for loc in error.get("loc", []))
                    message = error.get("msg", "Unknown error")
                    errors.append(f"{field}: {message}")
                return "; ".join(errors)
            elif isinstance(error_data.get("detail"), str):
                return error_data["detail"]
            else:
                return f"HTTP {response.status_code} error"
        except (json.JSONDecodeError, KeyError):
            return f"HTTP {response.status_code} error"

    def get_prompts(
        self,
        tags: Optional[List[str]] = None,
        location: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get list of prompts.

        Args:
            tags: Filter by tags
            location: Filter by location
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of prompt data
        """
        params = {}
        if tags:
            params["tags"] = ",".join(tags)
        if location:
            params["location"] = location
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        response = self._make_request("GET", "/prompts", params=params)
        return response.get("prompts", [])

    def get_prompt_by_name(self, name: str) -> Dict[str, Any]:
        """Get a prompt by name.

        Args:
            name: Prompt name

        Returns:
            Prompt data
        """
        # Get all prompts and filter by name
        prompts = self.get_prompts()

        # Find the prompt with the matching name
        for prompt in prompts:
            if prompt["name"] == name:
                return prompt

        raise NotFoundError(f"Prompt '{name}' not found")

    def create_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prompt.

        Args:
            prompt_data: Prompt data

        Returns:
            Created prompt data
        """
        return self._make_request("POST", "/prompts", data=prompt_data)

    def update_prompt(
        self, prompt_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a prompt.

        Args:
            prompt_id: Prompt ID
            update_data: Data to update

        Returns:
            Updated prompt data
        """
        return self._make_request("PUT", f"/prompts/{prompt_id}", data=update_data)

    def delete_prompt(self, prompt_id: str) -> None:
        """Delete a prompt.

        Args:
            prompt_id: Prompt ID
        """
        self._make_request("DELETE", f"/prompts/{prompt_id}")

    def create_version(
        self, prompt_id: str, version_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new version for a prompt.

        Args:
            prompt_id: Prompt ID
            version_data: Version data

        Returns:
            Created version data
        """
        return self._make_request(
            "POST", f"/prompts/{prompt_id}/versions", data=version_data
        )

    def get_versions(self, prompt_id: str) -> List[Dict[str, Any]]:
        """Get all versions for a prompt.

        Args:
            prompt_id: Prompt ID

        Returns:
            List of version data
        """
        response = self._make_request("GET", f"/prompts/{prompt_id}/versions")
        return response.get("versions", [])

    def get_version(self, prompt_id: str, version_number: int) -> Dict[str, Any]:
        """Get a specific version of a prompt.

        Args:
            prompt_id: Prompt ID
            version_number: Version number

        Returns:
            Version data
        """
        return self._make_request(
            "GET", f"/prompts/{prompt_id}/versions/{version_number}"
        )

    def search_prompts(self, query: str) -> List[Dict[str, Any]]:
        """Search prompts by content.

        Args:
            query: Search query

        Returns:
            List of matching prompts
        """
        params = {"q": query}
        response = self._make_request("GET", "/prompts/search", params=params)
        return response.get("prompts", [])

    def restore_version(self, prompt_id: str, version_number: int) -> Dict[str, Any]:
        """Restore a prompt to a specific version.

        Args:
            prompt_id: Prompt ID
            version_number: Version number to restore to

        Returns:
            Updated prompt data
        """
        return self._make_request(
            "POST", f"/prompts/{prompt_id}/restore/{version_number}"
        )

    def get_diff(self, prompt_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """Get diff between two versions.

        Args:
            prompt_id: Prompt ID
            version1: First version number
            version2: Second version number

        Returns:
            Diff data
        """
        return self._make_request(
            "GET", f"/prompts/{prompt_id}/diff/{version1}/{version2}"
        )

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login with username and password and create an API key.

        Args:
            username: Username
            password: Password

        Returns:
            Login response with API key
        """
        # Step 1: Login to get JWT token
        login_data = {"username": username, "password": password}
        token_response = self._make_request(
            "POST", "/auth/login", data=login_data, skip_auth=True
        )

        # Step 2: Use JWT token to create an API key
        jwt_token = token_response["access_token"]

        # Create a temporary client with JWT token for API key creation
        jwt_headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "User-Agent": f"prompta-cli/{__version__}",
        }

        # Create API key
        api_key_name = f"prompta-cli-{username}"
        api_key_data = {"name": api_key_name, "expires_at": None}  # No expiration

        url = f"{self.base_url}/auth/api-keys"

        try:
            with httpx.Client(
                timeout=self.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=True,
            ) as client:
                response = client.request(
                    method="POST",
                    url=url,
                    headers=jwt_headers,
                    json=api_key_data,
                )

                # If we get a 400 error with "already exists", try to delete the old key and create a new one
                if response.status_code == 400 and "already exists" in response.text:
                    # Get existing API keys
                    keys_url = f"{self.base_url}/auth/api-keys"
                    keys_response = client.request(
                        method="GET", url=keys_url, headers=jwt_headers
                    )

                    if keys_response.status_code == 200:
                        keys_data = keys_response.json()
                        for key in keys_data.get("api_keys", []):
                            if key.get("name") == api_key_name and key.get("is_active"):
                                # Delete the existing key
                                delete_url = (
                                    f"{self.base_url}/auth/api-keys/{key['id']}"
                                )
                                client.request(
                                    method="DELETE", url=delete_url, headers=jwt_headers
                                )
                                break

                        # Try creating the key again
                        response = client.request(
                            method="POST",
                            url=url,
                            headers=jwt_headers,
                            json=api_key_data,
                        )

                if response.status_code >= 400:
                    error_detail = self._extract_error_detail(response)
                    raise PromptaAPIError(error_detail, response.status_code)

                api_key_response = response.json()

                # Return the API key in the expected format
                return {
                    "api_key": api_key_response["key"],
                    "name": api_key_response["name"],
                    "id": api_key_response["id"],
                }

        except httpx.RequestError as e:
            raise PromptaAPIError(f"Request failed: {str(e)}")

    def download_prompts(
        self,
        project_name: Optional[str] = None,
        directory: Optional[str] = None,
        tags: Optional[List[str]] = None,
        include_content: bool = True,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Download prompts with filtering options.

        Args:
            project_name: Filter by project name
            directory: Filter by directory pattern
            tags: Filter by tags
            include_content: Include prompt content in response
            format: Response format (json or zip)

        Returns:
            Download response data
        """
        params = {}
        if project_name:
            params["project_name"] = project_name
        if directory:
            params["directory"] = directory
        if tags:
            params["tags"] = tags
        if include_content is not None:
            params["include_content"] = include_content
        if format:
            params["format"] = format

        return self._make_request("GET", "/prompts/download", params=params)

    def download_prompts_zip(
        self,
        project_name: Optional[str] = None,
        directory: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bytes:
        """Download prompts as a ZIP file.

        Args:
            project_name: Filter by project name
            directory: Filter by directory pattern
            tags: Filter by tags

        Returns:
            ZIP file content as bytes
        """
        params = {}
        if project_name:
            params["project_name"] = project_name
        if directory:
            params["directory"] = directory
        if tags:
            params["tags"] = tags

        url = f"{self.base_url}/prompts/download/zip"
        headers = self._get_headers()

        try:
            with httpx.Client(
                timeout=self.timeout,
                verify=self.config.verify_ssl,
                follow_redirects=True,
            ) as client:
                response = client.request(
                    method="GET",
                    url=url,
                    headers=headers,
                    params=params,
                )

                # Handle different status codes
                if response.status_code == 401:
                    error_detail = self._extract_error_detail(response)
                    raise AuthenticationError(error_detail, response.status_code)
                elif response.status_code == 404:
                    error_detail = self._extract_error_detail(response)
                    raise NotFoundError(error_detail, response.status_code)
                elif response.status_code >= 400:
                    error_detail = self._extract_error_detail(response)
                    raise PromptaAPIError(error_detail, response.status_code)

                return response.content

        except httpx.RequestError as e:
            raise PromptaAPIError(f"Request failed: {str(e)}")

    def download_prompts_by_project(
        self, project_name: str, include_content: bool = True
    ) -> Dict[str, Any]:
        """Download all prompts from a specific project.

        Args:
            project_name: Project name
            include_content: Include prompt content in response

        Returns:
            Download response data
        """
        params = {"include_content": include_content}
        return self._make_request(
            "GET", f"/prompts/download/by-project/{quote(project_name)}", params=params
        )

    def download_prompts_by_directory(
        self, directory: str, include_content: bool = True
    ) -> Dict[str, Any]:
        """Download all prompts from a specific directory pattern.

        Args:
            directory: Directory pattern
            include_content: Include prompt content in response

        Returns:
            Download response data
        """
        params = {"directory": directory, "include_content": include_content}
        return self._make_request(
            "GET", "/prompts/download/by-directory", params=params
        )

    def download_prompts_by_tags(
        self, tags: List[str], include_content: bool = True
    ) -> Dict[str, Any]:
        """Download all prompts matching specific tags.

        Args:
            tags: Tags to filter by
            include_content: Include prompt content in response

        Returns:
            Download response data
        """
        params = {"tags": tags, "include_content": include_content}
        return self._make_request("GET", "/prompts/download/by-tags", params=params)
