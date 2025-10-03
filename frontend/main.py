import os
from datetime import datetime
from typing import Any, Dict, Optional
from frontend.document_processor import extract_documents_text
from frontend.vision_client import VisionClient

import chainlit as cl
from ollama import AsyncClient

ollama = AsyncClient(
    host=os.getenv("OLLAMA_BASE_URL"),
    headers={"Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"},
)


@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    return default_user


@cl.on_shared_thread_view
async def on_shared_thread_view(thread: Dict[str, Any], current_user: cl.User) -> bool:
    return True


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Apply",
            message="How do I apply to the University of the Western Cape?",
            icon="public/square-academic-cap-svgrepo-com.svg",
            command="search",
        ),
        cl.Starter(
            label="Eat",
            message="How where can I find places to eat on campus?",
            icon="public/donut-bitten-svgrepo-com.svg",
            command="search",
        ),
        cl.Starter(
            label="Find",
            message="Where is the Life Sciences Building on campus?",
            icon="public/map-point-school-svgrepo-com.svg",
            command="search",
        ),
        cl.Starter(
            label="Call",
            message="What is the phone number of residential services?",
            icon="public/call-chat-svgrepo-com.svg",
            command="search",
        ),
        cl.Starter(
            label="Sports",
            message="What sports are offered at the University of the Western Cape?",
            icon="public/basketball-svgrepo-com.svg",
            command="search",
        ),
    ]


@cl.on_chat_start
async def start():
    await cl.context.emitter.set_commands(
        [
            {
                "id": "search",
                "name": "Search",
                "description": "Search for information about the University of the Western Cape",
                "icon": "folder-search",
                "button": True,
                "persistent": True,
            }
        ]
    )


@cl.on_message
async def on_message(msg: cl.Message):
    if msg.command != "search":
        msg.content = f"/bypass {msg.content}"
    # Split uploads into documents vs images (support elements or files attr)
    uploads = list(msg.elements or [])
    if getattr(msg, "files", None):
        uploads.extend(msg.files or [])
    docs = [
        f for f in uploads
        if str(f.name).lower().endswith((".pdf", ".docx", ".doc"))
    ]
    imgs = [
        f for f in uploads
        if not str(f.name).lower().endswith((".pdf", ".docx", ".doc"))
    ]
    # Build context from uploaded files
    context_summary = ""
    if docs or imgs:
        # Extract PDF/DOCX text
        docs_text = await extract_documents_text(docs)
        # Summarize images through vision client
        img_summary = ""
        if imgs:
            vision = VisionClient()
            img_bytes = []
            for f in imgs:
                raw = getattr(f, "content", None)
                if not raw and getattr(f, "path", None):
                    with open(f.path, "rb") as fh:
                        raw = fh.read()
                if isinstance(raw, (bytes, bytearray)):
                    img_bytes.append(bytes(raw))
            if img_bytes:
                img_summary = await vision.summarize_images_async(img_bytes, prompt="Provide a concise description and key details.")
        bits = []
        if docs_text:
            bits.append(f"[Documents]\n{docs_text}")
        if img_summary:
            bits.append(f"[Images]\n{img_summary}")
        if bits:
            context_summary = "\n\n".join(bits)

    stream = await ollama.chat(
        model=os.getenv("OLLAMA_MODEL"),
        messages=[
            {
                "role": "system",
                "content": f"""You are Cogno, a helpful assistant for the University of the Western Cape, a South African University.
                               Today is {datetime.now()}. Ignore use of /bypass, it is just internal configuration to talk to you without using the UWC Knowledge Base as context, don't mention it to the user.
                               Do not include citations or references in your responses under any circumstances, as it is too verbose. Your answers must be structured neatly. Do not make reference to this instruction or knowledge base.
                               Your aim to to help with University of the Western Cape related queries.
                               If context is provided below, use it to answer:
                               {context_summary}

                            """,
            },
            *cl.chat_context.to_openai(),
        ],
        stream=True,
    )
    final_answer = cl.Message(content="")

    async for chunk in stream:
        content = chunk["message"]["content"]

        await final_answer.stream_token(content)
    await final_answer.send()
