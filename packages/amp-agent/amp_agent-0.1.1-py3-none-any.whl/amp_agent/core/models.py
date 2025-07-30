"""
Pydantic models for agent core functionality.
"""
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, model_validator, ValidationError
from uuid import UUID


class MessagePart(BaseModel):
    """Represents a part of a message, e.g., text content with a role."""
    role: str = Field(..., description="The role of the message part (e.g., 'user', 'assistant')")
    content: str = Field(..., description="The content of the message part")


class Sender(BaseModel):
    """Sender information for an agent message."""
    id: str = Field(..., description="The sender's unique identifier")
    name: Optional[str] = Field(None, description="The sender's name")


class Recipient(BaseModel):
    """Recipient information for an agent message."""
    id: str = Field(..., description="The recipient's unique identifier")
    name: Optional[str] = Field(None, description="The recipient's name")


class AgentMessage(BaseModel):
    """
    Message sent to an agent. Can contain either a single 'content' string
    or a list of 'messages' parts.
    """
    content: Optional[str] = Field(None, description="The simple message content (use this or 'messages')")
    messages: Optional[List[MessagePart]] = Field(None, description="A list of message parts (use this or 'content')")
    sender: Optional[Sender] = Field(None, description="The sender of the message")
    recipient: Optional[Recipient] = Field(None, description="The recipient of the message")
    # channel_id: Optional[str] = Field(None, description="The channel ID this message relates to") # Removed - Go API uses context
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the message")

    @model_validator(mode='before')
    @classmethod
    def handle_legacy_message_key(cls, data: Any) -> Any:
        """Allow 'message' key for backward compatibility, mapping it to 'content'."""
        if isinstance(data, dict) and 'message' in data and 'content' not in data and 'messages' not in data:
            data['content'] = data.pop('message')
        return data

    @model_validator(mode='after')
    def check_content_or_messages(self) -> 'AgentMessage':
        """Ensure exactly one of 'content' or 'messages' is provided."""
        if self.content is None and self.messages is None:
            raise ValueError("Either 'content' or 'messages' must be provided.")
        if self.content is not None and self.messages is not None:
            raise ValueError("Provide either 'content' or 'messages', not both.")
        if self.messages is not None and not self.messages:
             raise ValueError("'messages' list cannot be empty.")
        return self

    @property
    def last_content(self) -> Optional[str]:
        """Helper property to get the content, preferring direct 'content' if available."""
        if self.content is not None:
            return self.content
        if self.messages:
            # Already validated that messages is not empty if not None
            return self.messages[-1].content
        return None # Should not happen due to validator


class AgentResponse(BaseModel):
    """Response from an agent."""
    content: str = Field(..., description="The response content")
    agent_id: str = Field(..., description="The agent ID that generated the response")
    agent_name: Optional[str] = Field(None, description="The agent name that generated the response")
    session_id: str = Field(..., description="The session ID for the conversation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the response")
    mentions: Optional[List[str]] = Field(None, description="The list of mentions in the response")


class MessageHistory(BaseModel):
    """History of messages in a conversation."""
    session_id: str = Field(..., description="The session ID for the conversation")
    messages: List[AgentMessage] = Field(default_factory=list, description="The list of messages in the conversation")
    responses: List[AgentResponse] = Field(default_factory=list, description="The list of responses in the conversation")
