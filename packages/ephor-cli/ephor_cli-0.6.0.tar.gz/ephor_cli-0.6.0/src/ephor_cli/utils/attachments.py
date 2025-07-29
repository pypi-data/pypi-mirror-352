import base64
import logging

def process_attachments(message, s3_service):
    attachments = message.additional_kwargs.get("attachments", [])
    if not attachments:
        return message

    user_question = message.content if isinstance(message.content, str) else ""
    content = [{"type": "text", "text": user_question}]

    for att in attachments:
        s3_key = att.get("s3_key")
        file_type = att.get("type", "")
        name = att.get("name", "")
        if not s3_key:
            continue
        try:
            file_content = s3_service.get_file_content(s3_key)
            if not file_content:
                continue

            if file_type.startswith("image/"):
                b64_data = base64.b64encode(file_content).decode("utf-8")
                content.append({
                    "type": "image",
                    "source_type": "base64",
                    "data": b64_data,
                    "mime_type": file_type,
                    "filename": name
                })
            elif file_type == "application/pdf":
                b64_data = base64.b64encode(file_content).decode("utf-8")
                content.append({
                    "type": "file",
                    "source_type": "base64",
                    "data": b64_data,
                    "mime_type": "application/pdf",
                    "filename": name
                })
            elif file_type == "text/plain":
                try:
                    text_content = file_content.decode("utf-8")
                    content.append({
                        "type": "text",
                        "text": f"Content of {name}:\n{text_content}"
                    })
                except UnicodeDecodeError:
                    content.append({
                        "type": "text",
                        "text": f"[File {name} contains binary data and cannot be displayed as text]"
                    })
            else:
                content.append({
                    "type": "text",
                    "text": f"[File {name} attached, but type {file_type} is not supported for LLM input]"
                })
        except Exception as e:
            content.append({
                "type": "text",
                "text": f"[Could not load {name}: {e}]"
            })
    message.content = content
    logging.debug("[attachments.py] Message content after attachment processing: %s", message.content)
    return message 