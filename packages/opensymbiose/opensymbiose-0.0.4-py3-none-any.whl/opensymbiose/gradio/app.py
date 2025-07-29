import logging
import sys
import time
from dataclasses import asdict

import gradio as gr
from gradio import ChatMessage
from mistralai import Mistral, ToolReferenceChunk

import opensymbiose.config
from opensymbiose.agents.create_agents import get_agents

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
client = Mistral(api_key=opensymbiose.config.MISTRAL_API_KEY)
model = "mistral-medium-latest"

# Log Version Information
logger.info(f"Gradio version: {gr.__version__}")
logger.info(f"Python version: {sys.version}")


async def get_mistral_answer(message: str, history=None):
    # Start global execution timer
    global_start_time = time.time()
    logger.info(f"Processing message: {message}")

    # Dictionary to track tool execution times
    tool_timers = {}

    agents = await get_agents()
    main_agent = agents["test_agent_tools"]
    stream_response = await client.beta.conversations.start_stream_async(
        agent_id=main_agent.id, inputs=message, store=False
    )
    messages = []
    # Add an initial empty message for the assistant's response
    messages.append(asdict(ChatMessage(role="assistant", content="")))
    full_response = ""
    async for chunk in stream_response:
        logger.info(f"Chunk: {chunk}")
        if chunk.event == "message.output.delta":
            if (
                isinstance(chunk.data.content, dict)
                and "filepath" in chunk.data.content
            ):
                # Handle file messages with proper alt_text
                file_path = chunk.data.content["filepath"]
                alt_text = chunk.data.content.get(
                    "alt_text", "File attachment"
                )  # Default alt_text if not provided
                messages.append(
                    asdict(
                        ChatMessage(
                            role="assistant",
                            content=file_path,
                            metadata={"type": "file", "alt_text": alt_text},
                        )
                    )
                )
            elif isinstance(chunk.data.content, str):
                full_response += chunk.data.content
                if (
                    messages
                    and messages[-1].get("role") == "assistant"
                    and not messages[-1].get("metadata")
                ):
                    messages[-1] = asdict(
                        ChatMessage(role="assistant", content=full_response)
                    )
                else:
                    messages.append(
                        asdict(ChatMessage(role="assistant", content=full_response))
                    )
            elif isinstance(chunk.data.content, ToolReferenceChunk):
                full_response += (
                    f"([{chunk.data.content.title}]({chunk.data.content.url})) "
                )
                if (
                    messages
                    and messages[-1].get("role") == "assistant"
                    and not messages[-1].get("metadata")
                ):
                    messages[-1] = asdict(
                        ChatMessage(role="assistant", content=full_response)
                    )
                else:
                    messages.append(
                        asdict(ChatMessage(role="assistant", content=full_response))
                    )
            yield messages
        elif chunk.event == "tool.execution.started":
            # Start timer for this tool
            tool_timers[chunk.data.name] = time.time()
            # Add a new message for tool execution start
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={"title": f"🛠️ Using tool {chunk.data.name}..."},
                    )
                )
            )
            yield messages
        elif chunk.event == "tool.execution.done":
            # Calculate tool execution duration
            tool_duration = time.time() - tool_timers.get(chunk.data.name, time.time())
            # Add a new message for tool execution completion
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={
                            "title": f"🛠️ Finished using {chunk.data.name}.",
                            "duration": round(tool_duration, 2),
                        },
                    )
                )
            )
            # Add a new empty message for the continuing assistant response
            messages.append(
                asdict(ChatMessage(role="assistant", content=full_response))
            )
            yield messages
        elif chunk.event == "agent.handoff.started":
            # Start timer for agent handoff
            tool_timers["agent_handoff"] = time.time()
            # Add a new message for agent handoff start
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={
                            "title": f"🔄 Handing off from agent {chunk.data.previous_agent_name}..."
                        },
                    )
                )
            )
            yield messages
        elif chunk.event == "agent.handoff.done":
            # Calculate handoff duration
            handoff_duration = time.time() - tool_timers.get(
                "agent_handoff", time.time()
            )
            # Add a new message for agent handoff completion
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={
                            "title": f"✅ Handoff complete. Now using agent {chunk.data.next_agent_name}.",
                            "duration": round(handoff_duration, 2),
                        },
                    )
                )
            )
            # Add a new empty message for the continuing assistant response
            messages.append(
                asdict(ChatMessage(role="assistant", content=full_response))
            )
            yield messages
        elif chunk.event == "function.call.delta":
            # Start timer for function call
            function_start_time = time.time()
            # Add function call information to the response
            function_info = f"Calling function: {chunk.data.name} with arguments: {chunk.data.arguments}"
            # Store the function name for potential future duration calculation
            tool_timers[f"function_{chunk.data.name}"] = function_start_time
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={"title": f"📞 {function_info}"},
                    )
                )
            )
            yield messages
        elif chunk.event == "conversation.response.started":
            # Add a new message for conversation response start
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={
                            "title": "🚀 Symbiose agent is starting...",
                            "log": f"{chunk.data.conversation_id}",
                        },
                    )
                )
            )
            yield messages
        elif chunk.event == "conversation.response.done":
            # Calculate global execution duration
            global_duration = time.time() - global_start_time
            # Add a new message for conversation response completion
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={
                            "title": "✅ Conversation response complete.",
                            "log": f"Tokens: Prompt: {chunk.data.usage.prompt_tokens}, Completion: {chunk.data.usage.completion_tokens}, Total: {chunk.data.usage.total_tokens} Connectors: {chunk.data.usage.connector_tokens}",
                            "duration": round(global_duration, 2),
                        },
                    )
                )
            )
            logger.info(
                f"Conversation response complete. Duration: {round(global_duration, 2)}s, Total tokens: {chunk.data.usage.total_tokens}"
            )
            yield messages
        elif chunk.event == "conversation.response.error":
            # Add a new message for conversation response error
            error_message = f"Error: {chunk.data.message} (Code: {chunk.data.code})"
            logger.error(f"Conversation response error: {error_message}")
            logger.error(f"Chunk: {chunk}")
            messages.append(
                asdict(
                    ChatMessage(
                        role="assistant",
                        content="",
                        metadata={"title": f"❌ {error_message}"},
                    )
                )
            )
            yield messages
        else:
            # For other events, just update the last message
            messages[-1] = asdict(ChatMessage(role="assistant", content=full_response))
            yield messages


with gr.Blocks() as demo:
    gr.ChatInterface(
        fn=get_mistral_answer,
        type="messages",
        title="Open-Symbiose🧬",
        description="OpenSymbiose is an open-source biotechnology / biology research AI agent designed to support researcher",
        examples=[
            "search internet: CEO of google",
            "Use your calculator agent to do 1273*3/12^2",
        ],
        save_history=True,
        flagging_mode="manual",
        cache_examples=False,  # Disable caching for examples to prevent startup validation errors
        concurrency_limit=None,
    )

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.INFO)
    demo.launch(ssr_mode=False)
