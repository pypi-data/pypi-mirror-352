"""
Client interface for interacting with the LexrChainer API.
"""

import os
import requests
from enum import Enum
from typing import List, Dict, Any, Optional
from lexrchainer_client.models import ModelInfo, FunctionDefinition, ValidationError, ConversationMedium, UserCreate, ClientConversationMessageRequest

class ClientMode(Enum):
    """Enum for client mode configuration."""
    SERVER = "server"  # Direct method calls
    CLIENT = "client"  # API calls

class ClientConfig:
    """Configuration for the client interface."""
    
    def __init__(self):
        self.mode = os.getenv("LEXRCHAINER_MODE", ClientMode.CLIENT.value)
        self.api_key = os.getenv("LEXRCHAINER_API_KEY")
        self.jwt_token = os.getenv("LEXRCHAINER_JWT_TOKEN")
        self.base_url = os.getenv("LEXRCHAINER_API_URL")
        
    @property
    def headers(self) -> Dict[str, str]:
        """Get the headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        elif self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers

class ClientInterface:
    """Interface for making API calls to the LexrChainer API."""
    
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self._available_tools = None
        self._available_models = None
    
    def _get_available_tools(self) -> List[FunctionDefinition]:
        """Get available tools from the server."""
        if self._available_tools is None:
            response = requests.get(
                f"{self.config.base_url}/agent/tools",
                headers=self.config.headers
            )
            response.raise_for_status()
            self._available_tools = response.json()
        return self._available_tools
    
    def _get_available_models(self) -> List[ModelInfo]:
        """Get available models from the server."""
        if self._available_models is None:
            response = requests.get(
                f"{self.config.base_url}/agent/models",
                headers=self.config.headers
            )
            response.raise_for_status()
            self._available_models = response.json()
        return self._available_models
    
    def validate_model(self, model_name: str) -> None:
        """Validate that the model exists in the model repository.
        
        Args:
            model_name: The name of the model to validate
            
        Raises:
            ValidationError: If the model is not found in the repository
        """
        available_models = self._get_available_models()
        if not any(model["name"] == model_name for model in available_models):
            raise ValidationError(f"Model '{model_name}' not found in model repository")
    
    def validate_tool(self, tool_name: str) -> None:
        """Validate that the tool exists in the tool repository.
        
        Args:
            tool_name: The name of the tool to validate
            
        Raises:
            ValidationError: If the tool is not found in the repository
        """
        available_tools = self._get_available_tools()
        if not any(tool["name"] == tool_name for tool in available_tools):
            raise ValidationError(f"Tool '{tool_name}' not found in tool repository")
    
    def send_message(self, conversation_id: str, messages: List[Any], streaming: bool = False) -> Any:
        """Send a message to a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            messages: The messages to send
            streaming: Whether to stream the response. If True, returns a response object
                     that can be iterated over for SSE events. If False, returns JSON response.
            
        Returns:
            If streaming=False: The JSON response from the conversation
            If streaming=True: The raw response object that can be iterated over for SSE events
        """
        client_conversation_message_request = ClientConversationMessageRequest(
            sender_id="",
            messages=messages,
            streaming=streaming
        )
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/send_message",
            headers=self.config.headers,
            json=client_conversation_message_request.model_dump(),
            stream=streaming  # Enable streaming for SSE
        )
        response.raise_for_status()
        
        if not streaming:
            return response.json()
        return response  # Return raw response for SSE streaming
    
    def create_conversation(self, request: Any) -> Dict[str, Any]:
        """Create a new conversation.
        
        Args:
            request: The conversation creation request
            
        Returns:
            The created conversation details
        """
        response = requests.post(
            f"{self.config.base_url}/conversation/",
            headers=self.config.headers,
            json=request.dict()
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, request: UserCreate) -> Any:
        """Create a new user.
        
        Args:
            request: The user creation request
            
        Returns:
            The created user details
        """
        #print(f"create_user: {request.model_dump()}")
        response = requests.post(
            f"{self.config.base_url}/user/",
            headers=self.config.headers,
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()

    # User API endpoints
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a user by ID."""
        response = requests.get(
            f"{self.config.base_url}/user/id/{user_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user."""
        response = requests.put(
            f"{self.config.base_url}/user/id/{user_id}",
            headers=self.config.headers,
            json=user_data
        )
        response.raise_for_status()
        return response.json()

    def delete_user(self, user_id: str) -> None:
        """Delete a user."""
        response = requests.delete(
            f"{self.config.base_url}/user/id/{user_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List users."""
        response = requests.get(
            f"{self.config.base_url}/user?skip={skip}&limit={limit}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def get_current_user(self) -> Dict[str, Any]:
        """Get the current user."""
        response = requests.get(
            f"{self.config.base_url}/user/self",
            headers=self.config.headers
        )
        print(response.headers)
        print(response.text)
        response.raise_for_status()
        return response.json()

    # Organization API endpoints
    def create_organization(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization."""
        response = requests.post(
            f"{self.config.base_url}/organization",
            headers=self.config.headers,
            json=org_data
        )
        response.raise_for_status()
        return response.json()

    def update_organization(self, org_id: str, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an organization."""
        response = requests.put(
            f"{self.config.base_url}/organization/{org_id}",
            headers=self.config.headers,
            json=org_data
        )
        response.raise_for_status()
        return response.json()

    # Workspace API endpoints
    def create_workspace(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workspace."""
        response = requests.post(
            f"{self.config.base_url}/workspace",
            headers=self.config.headers,
            json=workspace_data
        )
        response.raise_for_status()
        return response.json()

    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Get a workspace by ID."""
        response = requests.get(
            f"{self.config.base_url}/workspace/{workspace_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_workspace(self, workspace_id: str, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a workspace."""
        response = requests.put(
            f"{self.config.base_url}/workspace/{workspace_id}",
            headers=self.config.headers,
            json=workspace_data
        )
        response.raise_for_status()
        return response.json()

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete a workspace."""
        response = requests.delete(
            f"{self.config.base_url}/workspace/{workspace_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def list_workspaces(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List workspaces."""
        response = requests.get(
            f"{self.config.base_url}/workspace?skip={skip}&limit={limit}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def list_workspace_members(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List members of a workspace."""
        response = requests.get(
            f"{self.config.base_url}/workspace/{workspace_id}/members",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def add_workspace_member(self, workspace_id: str, member_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a member to a workspace."""
        response = requests.post(
            f"{self.config.base_url}/workspace/{workspace_id}/members",
            headers=self.config.headers,
            json=member_data
        )
        response.raise_for_status()
        return response.json()

    def remove_workspace_member(self, workspace_id: str, user_id: str) -> None:
        """Remove a member from a workspace."""
        response = requests.delete(
            f"{self.config.base_url}/workspace/{workspace_id}/members/{user_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    # Chain API endpoints
    def create_chain(self, chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chain."""
        response = requests.post(
            f"{self.config.base_url}/chain",
            headers=self.config.headers,
            json=chain_data
        )
        response.raise_for_status()
        return response.json()

    def get_chain(self, chain_id: str) -> Dict[str, Any]:
        """Get a chain by ID."""
        response = requests.get(
            f"{self.config.base_url}/chain/{chain_id}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_chain(self, chain_id: str, chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a chain."""
        response = requests.put(
            f"{self.config.base_url}/chain/{chain_id}",
            headers=self.config.headers,
            json=chain_data
        )
        response.raise_for_status()
        return response.json()

    def delete_chain(self, chain_id: str) -> None:
        """Delete a chain."""
        response = requests.delete(
            f"{self.config.base_url}/chain/{chain_id}",
            headers=self.config.headers
        )
        response.raise_for_status()

    def list_chains(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List chains."""
        response = requests.get(
            f"{self.config.base_url}/chain?skip={skip}&limit={limit}",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def trigger_chain(self, chain_id: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a chain execution."""
        response = requests.post(
            f"{self.config.base_url}/chain/{chain_id}/trigger",
            headers=self.config.headers,
            json=trigger_data
        )
        response.raise_for_status()
        return response.json()

    def schedule_chain(self, chain_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a chain execution."""
        response = requests.post(
            f"{self.config.base_url}/chain/{chain_id}/schedule",
            headers=self.config.headers,
            json=schedule_data
        )
        response.raise_for_status()
        return response.json()

    # Conversation API endpoints
    def add_conversation_member(self, conversation_id: str, user_id: str, role: str) -> Dict[str, Any]:
        """Add a member to a conversation."""
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/add_member",
            headers=self.config.headers,
            json={"user_id": user_id, "role": role}
        )
        response.raise_for_status()
        return response.json()

    def remove_conversation_member(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """Remove a member from a conversation."""
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/remove_member",
            headers=self.config.headers,
            json={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages from a conversation."""
        response = requests.post(
            f"{self.config.base_url}/conversation/{conversation_id}/get_messages",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def send_message_to_agent(self, agent_name: str, message_data: Dict[str, Any], streaming: bool = False) -> Any:
        """Send a message to a specific agent.
        
        Args:
            agent_name: The name of the agent to send the message to
            message_data: The message data to send
            streaming: Whether to stream the response. If True, returns a response object
                     that can be iterated over for SSE events. If False, returns JSON response.
            
        Returns:
            If streaming=False: The JSON response from the agent
            If streaming=True: The raw response object that can be iterated over for SSE events
        """
        response = requests.post(
            f"{self.config.base_url}/conversation/{agent_name}/message",
            headers=self.config.headers,
            json=message_data,
            stream=streaming  # Enable streaming for SSE
        )
        response.raise_for_status()
        
        if not streaming:
            return response.json()
        return response  # Return raw response for SSE streaming

    def send_public_agent_message(self, agent_name: str, message_data: Dict[str, Any], streaming: bool = False) -> Any:
        """Send a message to a public agent.
        
        Args:
            agent_name: The name of the public agent to send the message to
            message_data: The message data to send
            streaming: Whether to stream the response. If True, returns a response object
                     that can be iterated over for SSE events. If False, returns JSON response.
            
        Returns:
            If streaming=False: The JSON response from the public agent
            If streaming=True: The raw response object that can be iterated over for SSE events
        """
        response = requests.post(
            f"{self.config.base_url}/conversation/public/{agent_name}/message",
            headers=self.config.headers,
            json=message_data,
            stream=streaming  # Enable streaming for SSE
        )
        response.raise_for_status()
        
        if not streaming:
            return response.json()
        return response  # Return raw response for SSE streaming

    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all available agents.
        
        Returns:
            List of agent information dictionaries
        """
        response = requests.get(
            f"{self.config.base_url}/agent",
            headers=self.config.headers
        )
        response.raise_for_status()
        return response.json()

    def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent.
        
        Args:
            agent_id: The ID of the agent to update
            agent_data: The updated agent data
            
        Returns:
            Updated agent information
        """
        response = requests.patch(
            f"{self.config.base_url}/agent/{agent_id}",
            headers=self.config.headers,
            json=agent_data
        )
        response.raise_for_status()
        return response.json()

    def get_agent_conversations(self, agent_id: str, medium: ConversationMedium) -> List[str]:
        """Get all conversations for an agent with a specific medium.
        
        Args:
            agent_id: The ID of the agent
            medium: The conversation medium to filter by
            
        Returns:
            List of conversation IDs
        """
        response = requests.post(
            f"{self.config.base_url}/{agent_id}/conversations",
            headers=self.config.headers,
            params={"medium": medium.value}
        )
        response.raise_for_status()
        return response.json() 