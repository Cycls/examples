# this is a raq app example using chroma db as a vectore store and llama3-70b model

from cycls import Cycls
from groq import AsyncGroq
import chromadb
import pandas as pd
import asyncio

cycls = Cycls()
groq = AsyncGroq(api_key="your_groq_api_key")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("faqs")

# Load FAQ data using pandas
# Note: Ensure you have a CSV file named "faqs.csv" in the same directory
csv_path = "faqs.csv"
df = pd.read_csv(csv_path)

if collection.count() == 0:
    collection.add(
        documents=df['question'].tolist(),
        metadatas=df[['answer', 'class']].to_dict('records'),
        ids=[f"id_{i}" for i in range(len(df))]
    )
    print("FAQ data added to the persistent database.")
else:
    print("FAQ data already exists in the persistent database.")

async def get_context(query, k=3):
    results = await asyncio.to_thread(collection.query, query_texts=[query], n_results=k)

    questions = results["documents"][0]
    answers = [meta["answer"] for meta in results["metadatas"][0]]
    classes = [meta["class"] for meta in results["metadatas"][0]]
    context = "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(questions, answers))
    return context, classes

async def groq_llm(x, context, classes):
    system_message = f"""You are a helpful bank assistant. which I would like you to answer based only on the following context and not any other information:
    {context}
    This information is related to the following categories: {', '.join(classes)}
    If there is not enough information in the context to answer the question, say "I am not sure, can you please clarify". Break your answer up into nicely readable paragraphs. Always maintain a professional and courteous tone appropriate for a bank representative."""

    full_messages = [{"role": "system", "content": system_message}] + x

    stream = await groq.chat.completions.create(
        messages=full_messages,
        model="llama3-70b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )

    async def event_stream():
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    return event_stream()

# Main function to handle user input and generate responses
@cycls("@chroma")
async def chroma_app(message):
    history = message.history
    history += [{"role": "user", "content": message.content}]

    # Retrieve relevant context based on user input
    context, classes = await get_context(message.content)

    # Generate response using Groq with context and classes
    return await groq_llm(history, context, classes)

# Start the your application
cycls.push()
