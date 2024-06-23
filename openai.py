from cycls import Cycls, Text
from openai import AsyncOpenAI

cycls = Cycls()
client = AsyncOpenAI(api_key="API_KEY")

async def llm(messages):
    response = await client.chat.completions.create(model="gpt-4o", messages=messages, stream=True)
    async def event_stream():
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    return event_stream()

@cycls("openai")
async def openai_app(x):
    messages  = [{"role": "system", "content": "you are a helpful assistant."}]
    messages +=  x.history
    messages += [{"role": "user", "content": x.content}]
    stream = await llm(messages)
    return Text(stream)

cycls.push()
