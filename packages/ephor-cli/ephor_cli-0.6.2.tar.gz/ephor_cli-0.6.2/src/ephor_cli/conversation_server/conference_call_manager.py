import asyncio
import uuid
import os
import requests
from typing import Dict

from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import messages_from_dict
from langchain_core.messages.base import messages_to_dict

from ephor_cli.utils.orchestrator_agent_config import generate_final_response
from ephor_cli.conversation_server.host_manager import ADKHostManager
from ephor_cli.services.agent import AgentService
from ephor_cli.services.message import MessageService
from ephor_cli.types.message import (
    ConferenceCallTaskRequest,
    ConferenceCallTaskResponse,
    SendMessageRequest,
    SendMessageParams,
    SendMessageResponse,
    MessageInfo,
)


class ConferenceCallManager:
    def __init__(self):
        self.agent_service = AgentService()
        self.message_service = MessageService()

        self.active_managers: Dict[str, ADKHostManager] = {}
        self.managers_lock = asyncio.Lock()

    async def _send_message_orchestrator_internal(
        self, request_data: SendMessageRequest
    ):
        print(f"Orchestrator: Received message: {request_data.params.message}")
        message = messages_from_dict([request_data.params.message])[0]
        print(f"Orchestrator: Message: {message}")
        message.id = str(uuid.uuid4())

        # Create and manage ADKHostManager instance locally for this orchestration
        orchestrator_manager = ADKHostManager(
            request_data.params.user_id,
            request_data.params.project_id,
            request_data.params.conversation_id,
            request_data.params.context,
            None,
        )

        async with self.managers_lock:
            print(f"Orchestrator: Active manager for message {message.id} set")
            self.active_managers[message.id] = orchestrator_manager

        message = orchestrator_manager.sanitize_message(message)
        self.message_service.add_message(
            request_data.params.user_id,
            request_data.params.project_id,
            request_data.params.conversation_id,
            message,
        )
        print(
            f"Orchestrator: Stored message: {self.message_service.get_message(request_data.params.user_id, request_data.params.project_id, request_data.params.conversation_id, message.id)}"
        )
        message_id = message.id

        try:
            await orchestrator_manager.process_message(message)
        finally:
            # Clean up the active manager when done
            async with self.managers_lock:
                if message_id in self.active_managers:
                    del self.active_managers[message_id]

        return SendMessageResponse(
            result=MessageInfo(
                message_id=message_id,
                conversation_id=request_data.params.conversation_id,
                project_id=request_data.params.project_id,
                user_id=request_data.params.user_id,
            )
        )

    async def handle_conference_call_task(
        self, request_data: ConferenceCallTaskRequest
    ):
        """Handle conference call"""

        try:
            params = request_data.params
            user_email = params.user_id
            conversation_id = params.conversation_id
            project_id = params.project_id
            primary_conversation_id = params.primary_conversation_id
            summary = params.summary
            transcript = params.transcript

            asyncio.create_task(
                self.run_conference_call_task(
                    user_email,
                    project_id,
                    conversation_id,
                    primary_conversation_id,
                    summary,
                    transcript,
                )
            )

            return ConferenceCallTaskResponse(
                user_id=user_email,
                project_id=project_id,
                conversation_id=conversation_id,
                primary_conversation_id=primary_conversation_id,
                result="success",
            )
        except Exception as e:
            return ConferenceCallTaskResponse(
                user_id=user_email,
                project_id=project_id,
                conversation_id=conversation_id,
                primary_conversation_id=primary_conversation_id,
                result=f"Error: {e}",
            )

    async def run_conference_call_task(
        self,
        user_email,
        project_id,
        conversation_id,
        primary_conversation_id,
        summary,
        transcript,
    ):
        agents = self.agent_service.list_agents(
            user_email, project_id, primary_conversation_id
        )

        for agent in agents:
            self.agent_service.register_agent(
                user_email, project_id, conversation_id, agent.url
            )

        try:
            print(
                f"Starting background processing for conference call: {conversation_id}"
            )

            context = f"Transcript: {transcript}\\nCallSummary: {summary}"
            message_content = "Refer to the transcript and call summary given to you, understand the task assigned. You should get this task done without asking any follow up questions as you cannot interact with the user directly. Your job is to get the task done by delegating it to agents."
            message = HumanMessage(content=message_content)

            try:
                self.message_service.delete_messages(
                    user_email, project_id, conversation_id
                )
                print("Messages deleted for new conference call task.")
            except Exception as e:
                print(f"Error deleting messages: {e}")

            await self._send_message_orchestrator_internal(
                SendMessageRequest(
                    params=SendMessageParams(
                        user_id=user_email,
                        project_id=project_id,
                        conversation_id=conversation_id,
                        message=messages_to_dict([message])[0],
                        context=context,
                    )
                )
            )

            messages = self.message_service.list_messages(
                user_email, project_id, conversation_id
            )

            print("Conference call task processing completed.")

            final_response = generate_final_response(
                call_summary=summary,
                call_transcript=transcript,
                conversation_history=messages,
            )

            # Make HTTP call to the completion endpoint
            headers = {
                "Content-Type": "application/json",
                "x-api-key": os.environ.get("EPHOR_API_KEY", ""),
            }

            # Prepare the request payload
            payload = {
                "user_id": user_email,
                "project_id": project_id,
                "conversation_id": conversation_id,
                "primary_conversation_id": primary_conversation_id,
                "result": final_response,
            }

            # Get API server URL from environment
            API_SERVER_URL = os.environ.get("API_SERVER_URL", "")

            # Send the request to the completion endpoint
            response = requests.post(
                f"{API_SERVER_URL}/projects/{project_id}/conversations/{conversation_id}/on-background-task-complete",
                json=payload,
                headers=headers,
                timeout=30,  # 30 second timeout
            )

            # Handle the response
            if response.status_code == 200:
                print(
                    f"Successfully notified completion for conversation {conversation_id}"
                )
            else:
                print(
                    f"Failed to notify completion for conversation {conversation_id}. Status: {response.status_code}, Response: {response.text}"
                )

        except Exception as e:
            print(
                f"Error in background processing for conference call {conversation_id}: {e}"
            )
