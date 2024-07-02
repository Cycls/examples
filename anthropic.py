from cycls import Cycls
from anthropic import AsyncAnthropic

cycls = Cycls()
client = AsyncAnthropic(api_key="API_KEY")

async def anthropic_llm(x):
    for msg in x:
        if msg['role'] == 'system':
            msg['role'] = 'assistant'

    stream = await client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=x,
        system="You are a helpful assistant.",
        stream=True,
    )
    async def event_stream():
        async for event in stream:
            if event.type == "content_block_start":
                yield event.content_block.text
            elif event.type == "content_block_delta":
                yield event.delta.text
            elif event.type == "message_stop":
                break
    return event_stream()

@cycls("@anthropic")
async def anthropic_app(message):
    history = message.history
    history+=[{"role": "user", "content": message.content}]

    return await anthropic_llm(history)

cycls.push()
