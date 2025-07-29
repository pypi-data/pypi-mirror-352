from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from google_a2a.common.types import Message, Part


def a2a_message_to_langchain_message(message: Message) -> BaseMessage:
    if message.role == "user":
        return a2a_user_message_to_langchain_message(message)
    else:
        raise ValueError(f"Unknown message role: {message.role}")


def a2a_user_message_to_langchain_message(message: Message) -> HumanMessage:
    content = []  
    for part in message.parts:
        part_type = getattr(part, "type", "text")
        if part_type == "image":
            content.append({
                "type": "image",
                "source_type": getattr(part, "source_type", "base64"),
                "data": getattr(part, "data", ""),
                "mime_type": getattr(part, "mime_type", ""),
                "filename": getattr(part, "filename", "")
            })
        elif part_type == "file" or getattr(part, "mime_type", "") == "application/pdf":
            content.append({
                "type": "file",
                "source_type": getattr(part, "source_type", "base64"),
                "data": getattr(part, "data", ""),
                "mime_type": getattr(part, "mime_type", "application/pdf"),
                "filename": getattr(part, "filename", "")
            })
        elif part_type == "text":
            content.append({"type": "text", "text": part.text})
        else:
            content.append(part)
    return HumanMessage(content=content)


def langchain_message_to_a2a_message(message: BaseMessage) -> Message:
    if isinstance(message, AIMessage):
        return langchain_ai_message_to_a2a_message(message)
    else:
        raise ValueError(f"Unknown message type: {type(message)}")


def langchain_ai_message_to_a2a_message(message: AIMessage) -> Message:
    return Message(role="agent", parts=[{"type": "text", "text": message.content}])


def langchain_content_to_a2a_content(content: str | list[str | dict]) -> list[Part]:
    parts = []
    if isinstance(content, list):
        for item in content:
            parts.extend(langchain_content_to_a2a_content(item))
    elif isinstance(content, dict) and content["type"] == "text":
        parts.append(content)
    elif isinstance(content, str):
        parts.append({"type": "text", "text": content})
    return parts
