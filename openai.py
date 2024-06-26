from cycls import Cycls
from openai import AsyncOpenAI

cycls = Cycls()
client = AsyncOpenAI(api_key="API_KEY")

async def openai_llm(x):
    response = await client.chat.completions.create(
        model="gpt-4o", 
        messages=x, 
        stream=True
    )
    async def event_stream():
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    return event_stream()

@cycls("@openai")
async def openai_app(message):
    history = [{"role": "system", "content": "you are a helpful assistant."}]
    history +=  message.history
    history += [{"role": "user", "content": message.content}]
    return await openai_llm(history)

cycls.push()
