from cycls import Cycls
import google.generativeai as genai

cycls = Cycls()

genai.configure(api_key='API-KEY')

async def gemini_llm(x):
   
    for msg in x:
        if msg['role'] == 'system':
            msg['role'] = 'model'
    y = [{"role": msg["role"], "parts": [{"text": msg["content"]}]} for msg in x]
    
    model = genai.GenerativeModel(model_name='gemini-1.5-pro')
    response = await model.generate_content_async(y,stream=True)
    async for chunk in response:
        if chunk.text:
            yield chunk.text

@cycls("@gemini")
async def gemini_app(message):
    history = [{"role": "system", "content": "you are a helpful and concise assistant."}]
    history +=  message.history
    history += [{"role": "user", "content": message.content}]
    
    return gemini_llm(history)

cycls.push()
