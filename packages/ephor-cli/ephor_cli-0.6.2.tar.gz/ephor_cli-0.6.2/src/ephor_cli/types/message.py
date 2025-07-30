from pydantic import BaseModel
from typing import Literal, Dict, Any, Optional

from google_a2a.common.types import (
    JSONRPCRequest,
    JSONRPCResponse,
)


class ConferenceCallTaskParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str
    summary: str
    transcript: str
    primary_conversation_id: str


class Attachment(BaseModel):
    s3_key: str
    type: str   
    name: str
    size: int | None = None


class SendMessageParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str
    message: dict
    context: str
    attachments: list[Attachment] | None = None


class SendMessageRequest(JSONRPCRequest):
    method: Literal["message/send"] = "message/send"
    params: SendMessageParams


class ConferenceCallTaskRequest(JSONRPCRequest):
    method: Literal["conference-call/task"] = "conference-call/task"
    params: ConferenceCallTaskParams


class ListMessageParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str


class ListMessageRequest(JSONRPCRequest):
    method: Literal["message/list"] = "message/list"
    params: ListMessageParams


class ListMessageResponse(JSONRPCResponse):
    result: list[dict] | None = None


class MessageInfo(BaseModel):
    message_id: str
    conversation_id: str
    project_id: str
    user_id: str


class SendMessageResponse(JSONRPCResponse):
    result: MessageInfo | None = None


class ConferenceCallTaskResponse(JSONRPCResponse):
    user_id: str
    project_id: str
    conversation_id: str
    primary_conversation_id: str
    result: str | None = None


class CancelMessageParams(BaseModel):
    """Parameters for cancelling a message."""

    user_id: str
    project_id: str
    conversation_id: str
    message_id: str


class CancelMessageRequest(JSONRPCRequest):
    """Request to cancel message processing."""

    method: Literal["message/cancel"] = "message/cancel"
    params: CancelMessageParams


class CancelMessageResponse(JSONRPCResponse):
    """Response from cancelling a message."""

    result: bool
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
