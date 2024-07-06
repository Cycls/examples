from cycls import Cycls
import httpx
import asyncio

# Initialize Cycls
cycls = Cycls()

# API base URL for mymidjourney.ai
BASE_URL = "https://api.mymidjourney.ai/api/v1/midjourney"

# Initialize the HTTP client with authentication
client = httpx.AsyncClient(
    base_url=BASE_URL,
    headers={"Authorization": "Bearer YOUR_API_KEY_HERE"}
)

# Dictionary to keep track of ongoing generation tasks
generation_tasks = {}

async def generate_image(prompt, user_id):
    """
    Asynchronous function to generate an image based on the given prompt.
    It handles the API calls and yields progress updates.
    """
    try:
        # Initiate image generation
        response = await client.post("/imagine", json={"prompt": prompt})
        response.raise_for_status()
        data = response.json()
        message_id = data["messageId"]

        while True:
            # Check if the task was cancelled
            if user_id not in generation_tasks:
                yield "Image generation cancelled."
                return

            # Check progress of image generation
            progress_response = await client.get(f"/message/{message_id}")
            progress_response.raise_for_status()
            progress_data = progress_response.json()

            if progress_data["status"] == "DONE":
                # Image generation completed successfully
                print(f"Generated image URL: {progress_data['uri']}")
                yield f"Image generated successfully!  \n\n![Generated Image]({progress_data['uri']})  \n"
                return
            elif progress_data["status"] == "FAIL":
                # Image generation failed
                yield f"Image generation failed: {progress_data.get('error', 'Unknown error')}"
                return

            # Yield progress update
            yield f"  \nImage generation in progress... {progress_data.get('progress', 0)}% complete"
            await asyncio.sleep(5)  # Wait before next progress check

    except httpx.RequestError as e:
        yield f"An error occurred: {str(e)}"
    finally:
        # Clean up the task from the dictionary
        if user_id in generation_tasks:
            del generation_tasks[user_id]

async def midjourney_llm(message):
    """
    Main function to handle user messages and manage image generation process.
    """
    user_id = message.id  # Use the session id as user_id

    # Handle cancellation request
    if message.content.lower() == "cancel":
        if user_id in generation_tasks:
            del generation_tasks[user_id]
            yield "Image generation cancelled."
        else:
            yield "No ongoing image generation to cancel."
        return

    # Check if there's already an ongoing task for this user
    if user_id in generation_tasks:
        yield "Please wait until the current image is generated or type 'cancel' to stop the current generation."
        return

    # Start new image generation task
    generation_tasks[user_id] = True

    yield "Starting image generation... This may take a few minutes. \n"

    # Process and yield updates from the generate_image function
    async for update in generate_image(message.content, user_id):
        yield update

    yield "Image generation process completed."

@cycls("@midjourney")
async def midjourney_app(message):
    """
    Cycls app entry point.
    """
    return midjourney_llm(message)

# Push the app to Cycls
cycls.push()
