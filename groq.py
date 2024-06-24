from cycls import Cycls
from groq import AsyncGroq

cycls = Cycls()
groq = AsyncGroq(api_key="API_KEY")

async def groq_llm(x):
    stream = await groq.chat.completions.create(
        messages=x,
        model="llama3-70b-8192",
        temperature=0.5, max_tokens=1024, top_p=1, stop=None, 
        stream=True,
    )
    async def event_stream():
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    return event_stream()

@cycls("groq")
async def groq_app(message):
    history = [{"role": "system", "content": "you are a helpful assistant."}]
    history +=  message.history
    history += [{"role": "user", "content": message.content}]
    return await groq_llm(history)
  
cycls.push()
