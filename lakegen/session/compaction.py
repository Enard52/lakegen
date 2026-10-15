from lakegen.prompt import COMPACTION_PROMPT
from lakegen.inference import Router
from lakegen.inference.model import ChatRequest, Message, Role
from lakegen.agent import Conversation
 

def compact(
    inference_router: Router,
    provider: str,
    model: str,
    conversation: Conversation,
) -> Message:
    role_conversation = remove_tool_calls_from_conversation(conversation)
    request = ChatRequest(
        model=model,
        system_prompt=COMPACTION_PROMPT,
        messages=role_conversation.messages,
        tools=[],
    )
    response = inference_router.complete(provider, request)
    return Message(
        role=Role.USER,
        content=response.message.content or ""
    )


def remove_tool_calls_from_conversation(conversation: Conversation) -> Conversation:
    stripped: list[Message] = []
    for msg in conversation.messages:
        if msg.role == Role.TOOL:
            continue
        if (
            msg.role == Role.ASSISTANT
            and msg.tool_calls
            and not (msg.content or "").strip()
        ):
            continue
        stripped.append(Message(role=msg.role, content=msg.content))
    return Conversation(messages=stripped)