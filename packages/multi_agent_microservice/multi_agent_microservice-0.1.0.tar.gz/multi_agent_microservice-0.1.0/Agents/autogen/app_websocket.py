from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from agents.utils.utils import init
init()
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image
from autogen_ext.models.openai import OpenAIChatCompletionClient
import fitz  # PyMuPDF for PDF processing
from pathlib import Path

app = FastAPI()

# Initialize the OpenAI client
model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)

# Initialize the AssistantAgent
assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant. You can answer questions based on the provided PDF content.",
    model_client=model_client,
)

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Custom input function for UserProxyAgent
        async def custom_input_func(prompt: str, **kwargs) -> str:
            """Custom input function to retrieve user input from the WebSocket."""
            await websocket.send_text(prompt)  # Send the prompt to the client
            return await websocket.receive_text()  # Wait for the client's response

        # Initialize the UserProxyAgent with the custom input function
        user_proxy = UserProxyAgent(
            name="user_proxy",
            input_func=custom_input_func,  # Pass the custom input function
        )

        # Receive the PDF file path from the client
        pdf_path = await websocket.receive_text()
        pdf_path = Path(pdf_path)

        # Extract text from the PDF
        pdf_text = extract_text_from_pdf(pdf_path)

        # Create a MultiModalMessage with the extracted content
        pdf_message = MultiModalMessage(
            content=["Here is the content from the PDF:", pdf_text],
            source="user",
        )

        # Define a termination condition for the group chat
        termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

        # Initialize the RoundRobinGroupChat with the assistant and user proxy
        group_chat = RoundRobinGroupChat(
            [user_proxy, assistant],
            termination_condition=termination,  # Custom termination condition
        )

        # Send the PDF content to the group chat
        await group_chat.run(task=pdf_message)

        # Notify the client that the PDF has been processed
        await websocket.send_text("PDF content processed. You can now ask questions.")

        while True:
            # Ask the client for a question
            question = await custom_input_func("Please ask a question about the PDF:")
            if question.lower() == "exit":
                await websocket.send_text("Exiting...")
                break

            # Send the question to the group chat
            response = await group_chat.run(task=question)

            # Extract the assistant's response from the TaskResult
            if response and hasattr(response, "messages"):
                assistant_response = next(
                    (msg.content for msg in response.messages if msg.source == "assistant"),
                    "No response from the assistant.",
                )
            else:
                assistant_response = "No response from the assistant."

            # Send the assistant's response back to the client
            await websocket.send_text(f"Assistant: {assistant_response}")

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_text(f"Error: {e}")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)