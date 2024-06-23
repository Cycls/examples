from cycls import Cycls, Text
from groq import AsyncGroq

cycls = Cycls()
groq = AsyncGroq(api_key="API_KEY")

async def llm(messages):
    stream = await groq.chat.completions.create(
        messages=messages,
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
async def groq_app(x):
    messages  = [{"role": "system", "content": "you are a helpful assistant."}]
    messages +=  x.history
    messages += [{"role": "user", "content": x.content}]
    stream = await llm(messages)
    return Text(stream)
  
cycls.push()
