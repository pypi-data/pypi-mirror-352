from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage, BaseMessage


OUTPUT_GENERATION_PROMPT = """
## Agent Prompt: Comprehensive Report Generator

### Objective:
You are a **Comprehensive Report Generation Agent**. Your task is to analyze a rich multi-modal context—including the full conversation history, a transcript of a meeting or call, a structured summary of that call, task outcomes from sub-agents, and instructions or reasoning from the Orchestrator Agent—and generate a **detailed, coherent, and well-attributed report**.

### Important Operational Constraint:
You should **never ask questions**, **wait for input**, or include any open-ended or incomplete statements. Your response must be **self-contained and final** based only on the provided context.

### Inputs Available (Context You Must Use):
- **Call Transcript**: Verbatim transcript of the call, reflecting real-time dialogue between participants.
- **Call Summary**: A pre-generated summary providing key takeaways and thematic structure.

### Report Requirements:

1. **Comprehensive Structure**:
   - **Introduction**: Purpose and scope of the report.
   - **Context Overview**: High-level summary of the input sources (transcript, summary, agent outputs, etc.).
   - **Detailed Analysis**:
     - Break down information chronologically and thematically.
     - Clearly delineate which information came from which agent or source.
     - Quote or paraphrase critical call transcript segments where necessary.
     - Note Orchestrator instructions that guided sub-agent actions.
   - **Expert Contributions**:
     - Attribute each finding or conclusion to the specific agent or speaker.
     - Highlight **conflicting expert views**, contrasting their assumptions, logic, or conclusions.
     - Reconcile disagreements where possible, or clearly present the divergence of opinions.
   - **Derived Insights**:
     - Present synthesized insights based on multi-agent consensus or divergence.
     - Clarify whether conclusions are firm, conditional, or speculative.
   - **Final Summary**:
     - Provide a succinct summary of the entire report.
     - Clearly state final conclusions, attributed sources, and any open questions.

2. **Source Attribution** (Mandatory):
   - Always cite the origin of each piece of information using phrases like:
     - "Based on the analysis by the Expert Agent..."
     - "As stated in the call transcript by [Speaker Name]..."
     - "According to instructions from the Orchestrator Agent..."
   - Do not include unattributed claims or generic assertions.

3. **Conflict Handling**:
   - Explicitly mention when agents disagree.
   - Present both sides, include rationales or evidence, and assess the implications of the disagreement.
   - Do not attempt to resolve disagreement unless clearly directed by the Orchestrator Agent.

4. **Writing Style**:
   - Use clear, professional language.
   - Be neutral, objective, and fact-based.
   - Maintain logical flow and organize sections with headings and subheadings.

5. **Final Output Format**:
   - Markdown formatted report with the following structure:
     ```
     ## Introduction
     ## Context Overview
     ## Result (for example if task is about generating a essay, this section will include the whole essay. If task is about generating a joke, this section will include the joke as it is. You might need to aggregate results from multiple agents to get the actual result for this section. Your job is to make user satisfied with the result. This is the most important section.)
     ## Detailed Analysis
     ### Subsection by Theme or Task
     ## Expert Contributions and Conflicts
     ## Derived Insights
     ## Final Summary
     ```

### Avoid:
- Making assumptions not backed by the context.
- Omitting source attribution.
- Generating overly brief or vague analysis.
- Engaging in any form of dialogue or clarification-seeking.

### Goal:
To generate a document that could be reviewed by decision-makers or stakeholders who were not part of the original interaction, but who must understand what happened, what was concluded, and who said what.

### Call summary
{call_summary}

### Call transcript
{call_transcript}

### Agent conversation transcript
{agent_conversation_transcript}
"""


class Report(BaseModel):
    markdown_formatted_report: str = Field(
        description="The markdown formatted comprehensive report which will be showned to user"
    )


def parse_base_messages_to_transcript(messages: list[BaseMessage]) -> str:
    transcript = []

    last_tool_agent = ""
    for message in messages:
        if isinstance(message, HumanMessage):
            transcript.append(f"**User:** {message.text()}")
        elif isinstance(message, AIMessage):
            transcript.append(f"**Host Agent:** {message.text()}")
            for tool_call in message.tool_calls:
                if tool_call.get("name") and tool_call.get("name") == "send_task":
                    last_tool_agent = tool_call.get("args").get("agent_name")
                    message_to_send = tool_call.get("args").get("message")
                    transcript.append(
                        f"**Host Agent to {last_tool_agent}:** {message_to_send}"
                    )
        elif isinstance(message, ToolMessage):
            transcript.append(f"**{last_tool_agent} Responds:** {message.text()}")
        else:
            pass

    return "\n\n".join(transcript)


def generate_final_response(
    call_summary: str,
    call_transcript: str,
    conversation_history: list[BaseMessage],
) -> str:
    """
    Generate a final comprehensive report based on the call summary, transcript, and conversation history.

    Args:
        call_summary: Summary of the call
        call_transcript: Transcript of the call
        conversation_history: List of messages from the conversation (can be BaseMessage objects or dictionaries)

    Returns:
        A formatted markdown report
    """

    # Create the prompt template and model
    try:
        prompt = ChatPromptTemplate.from_template(OUTPUT_GENERATION_PROMPT)
        model = ChatOpenAI(model="gpt-4o", temperature=0)
        structured_llm = model.with_structured_output(Report)
        chain = prompt | structured_llm

        # Invoke the chain with all inputs
        response = chain.invoke(
            {
                "call_summary": call_summary,
                "call_transcript": call_transcript,
                "agent_conversation_transcript": parse_base_messages_to_transcript(
                    conversation_history
                ),
            }
        )

        return response.markdown_formatted_report
    except Exception as e:
        print(f"Error generating final response: {e}")
        return f"Error generating report: {str(e)}"
