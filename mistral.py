from cycls import Cycls
from mistralai.async_client import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage

cycls = Cycls()
client = MistralAsyncClient(api_key="YOUR_MISTRAL_API_KEY")

async def mistral_llm(x):
    # Convert the messages to Mistral's ChatMessage format
    formatted_messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in x]

    stream = client.chat_stream(
        model="mistral-large-latest",  # or any other Mistral model you want to use
        messages=formatted_messages,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

@cycls("@mistral")
async def mistral_app(message):
    # Define the system message at the app level, you can change it to be on the LLM level by simple adding the system message in the mistral_llm function above
    history = [{"role": "system", "content": "you are a helpful assistant."}]
    history +=  message.history
    history += [{"role": "user", "content": message.content}]

    return mistral_llm(history)

cycls.push()
