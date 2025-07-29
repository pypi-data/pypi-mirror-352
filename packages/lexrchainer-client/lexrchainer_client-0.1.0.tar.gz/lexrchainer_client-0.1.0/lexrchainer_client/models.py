"""
Client-side data models for LexrChainer.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union, TypeAlias
from enum import Enum
from typing_extensions import Required, TypedDict

class MessageType(str, Enum):
    """Type of message content."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"

class MessageRole(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageContent(BaseModel):
    """Content of a message."""
    type: MessageType
    text: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Message(BaseModel):
    """A message in a conversation."""
    role: MessageRole
    content: str
    entity_id: str
    conversation_id: Optional[str] = None

class ModelParams(BaseModel):
    """Parameters for model configuration."""
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None

class ModelConfig(BaseModel):
    """Configuration for a model."""
    name: str
    credentials: Dict[str, Any] = Field(default_factory=dict)
    params: ModelParams

class ToolConfig(BaseModel):
    """Configuration for a tool."""
    name: str
    credentials: Dict[str, Any] = Field(default_factory=dict)

class ChainStepType(str, Enum):
    """Type of chain step."""
    USER_MESSAGE_ADDENDUM = "USER_MESSAGE_ADDENDUM"
    ASSISTANT_MESSAGE_ADDENDUM = "ASSISTANT_MESSAGE_ADDENDUM"
    HIDDEN_TURN_USER = "HIDDEN_TURN_USER"
    HIDDEN_TURN_ASSISTANT = "HIDDEN_TURN_ASSISTANT"
    DIRECT_TOOL_USE = "DIRECT_TOOL_USE"
    EXECUTE_CODE = "EXECUTE_CODE"
    SET_RESULT = "SET_RESULT"
    # Used when a calculated / processed data needs to be sent to user. Example: Message extracted from XML tags.
    SEND_TO_USER = "SEND_TO_USER"

class ChainStepFlowDirection(str, Enum):
    """Direction of flow in a chain step."""
    TO_USER = "TO_USER"
    TO_ASSISTANT = "TO_ASSISTANT"

class ChainStepFlowType(str, Enum):
    """Type of flow in a chain step."""
    AT_ONCE = "AT_ONCE"
    STREAMING = "STREAMING"

class ChainStepFlowState(str, Enum):
    """State of flow in a chain step."""
    CONTINUE = "CONTINUE"
    END = "END"

class ChainStepResponseTreatment(str, Enum):
    """How to treat the response in a chain step."""
    APPEND = "APPEND"
    REPLACE = "REPLACE"
    IGNORE = "IGNORE"

class ChainStepConfig(BaseModel):
    """Configuration for a chain step."""
    name: str
    id: str
    description: str
    version: str
    prompt: str
    type: ChainStepType
    flow: ChainStepFlowDirection
    flow_type: ChainStepFlowType = ChainStepFlowType.AT_ONCE
    flow_state: ChainStepFlowState = ChainStepFlowState.CONTINUE
    response_treatment: ChainStepResponseTreatment = ChainStepResponseTreatment.APPEND
    tool_use: bool = False
    model_params: ModelParams

class ChainMeta(BaseModel):
    """Metadata for a chain."""
    id: str
    name: str
    description: str
    version: str
    default_system_prompt: str
    static_meta: Dict[str, Any] = Field(default_factory=dict)
    tools: List[ToolConfig] = Field(default_factory=list)
    models: List[ModelConfig] = Field(default_factory=list)
    default_model_params: ModelParams

class ChainCreate(BaseModel):
    json_content: Dict[str, Any]
    class Config:
        extra = 'allow'

class ChainConfig(BaseModel):
    """Configuration for a chain."""
    chain: ChainMeta
    steps: List[ChainStepConfig]

class UserType(str, Enum):
    """Type of user."""
    HUMAN = "human"
    AGENT = "agent"

class ConversationMedium(str, Enum):
    """Medium of conversation."""
    WHATSAPP = "WHATSAPP"
    WEB = "WEB"
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"

class ConversationTurnType(str, Enum):
    """Type of conversation turn."""
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"

class ConversationIterationEndCriteria(str, Enum):
    """Criteria for ending conversation iteration."""
    ALL_TURNS_DONE = "ALL_TURNS_DONE"
    PERPETUAL = "PERPETUAL"
    MAX_ITERATIONS = "MAX_ITERATIONS"

class ConversationMemberRole(str, Enum):
    """Role of a conversation member."""
    ACTIVE_PARTICIPATION = "ACTIVE_PARTICIPATION"
    OBSERVER = "OBSERVER"

class ConversationMember(BaseModel):
    """A member in a conversation."""
    id: Optional[str] = None
    role: ConversationMemberRole = ConversationMemberRole.ACTIVE_PARTICIPATION

class UserCreate(BaseModel):
    """Request to create a user."""
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_type: UserType
    chain_id: Optional[str] = None
    chain_config: Optional[ChainCreate] = None

class CreateConversationRequest(BaseModel):
    """Request to create a conversation."""
    medium: ConversationMedium
    members: List[ConversationMember]
    turn_type: ConversationTurnType
    iteration_end_criteria: ConversationIterationEndCriteria
    iteration_limit: Optional[int] = None
    persist: bool = True

class ClientConversationMessageRequest(BaseModel):
    """Request to send a message to a conversation."""
    sender_id: str
    messages: List[Message]
    streaming: Optional[bool] = False

class ModelInfo(BaseModel):
    """Information about an available model."""
    name: str
    version: str
    description: str
    default_model_params: ModelParams

class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass 

FunctionParameters: TypeAlias = Dict[str, object]

class FunctionDefinition(TypedDict, total=False):
    name: Required[str]
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    description: str
    """
    A description of what the function does, used by the model to choose when and
    how to call the function.
    """

    parameters: FunctionParameters
    """The parameters the functions accepts, described as a JSON Schema object.

    See the [guide](https://platform.openai.com/docs/guides/function-calling) for
    examples, and the
    [JSON Schema reference](https://json-schema.org/understanding-json-schema/) for
    documentation about the format.

    Omitting `parameters` defines a function with an empty parameter list.
    """

    strict: Optional[bool]
    """Whether to enable strict schema adherence when generating the function call.

    If set to true, the model will follow the exact schema defined in the
    `parameters` field. Only a subset of JSON Schema is supported when `strict` is
    `true`. Learn more about Structured Outputs in the
    [function calling guide](docs/guides/function-calling).
    """