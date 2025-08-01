import chainlit as cl
from ollama import AsyncClient

# Initialize Ollama client
ollama = AsyncClient(host="http://localhost:11434")


# Declare Chat Profile
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="UWC_Chat",
            markdown_description="Chatbot with **UWC** brand colors",
        )
    ]


# Send welcome message
@cl.on_chat_start
async def setup_ui():
    cl.user_session.set(
        "settings",
        [
            {
                "id": "header_color",
                "name": "Header Color",
                "type": "color",
                "value": "#0056A7",
                "description": "Header color",
            },
            {
                "id": "user_message_color",
                "name": "User Message Color",
                "type": "color",
                "value": "#FFD100",
                "description": "User message color",
            },
            {
                "id": "ai_message_color",
                "name": "AI Message Color",
                "type": "color",
                "value": "#78BE20",
                "description": "AI message color",
            },
            {
                "id": "background_color",
                "name": "Background Color",
                "type": "color",
                "value": "#FFFFFF",
                "description": "Background color",
            },
        ],
    )

    await cl.Message(
        content="Welcome to **UWC Chat**! If you see this, the app is running."
    ).send()


# Handle messages
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    response = await ollama.chat(
        model="qwen3:0.6b",
        messages=[
            {"role": "system", "content": "You are a helpful UWC assistant."},
            {"role": "user", "content": message.content},
        ],
        stream=True,
    )

    async for chunk in response:
        await msg.stream_token(chunk["message"]["content"])

    await msg.update()
