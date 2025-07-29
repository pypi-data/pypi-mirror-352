from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import Image
from autogen_ext.models.openai import OpenAIChatCompletionClient
import fitz  # PyMuPDF for PDF processing
import asyncio
from pathlib import Path
from agents.utils.utils import init

init()

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_images_from_pdf(pdf_path: Path) -> list[Image]:
    """Extract images from a PDF file."""
    images = []
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                image = Image.from_bytes(image_data)
                images.append(image)
    return images


async def main() -> None:
    # Initialize the OpenAI client
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)

    # Path to the PDF file
    pdf_path = Path("agents.pdf")

    # Extract text and images from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    #pdf_images = extract_images_from_pdf(pdf_path)

    # Create a shared memory dictionary
    shared_memory = {
        "pdf_text": pdf_text,  # Store the extracted images
    }

    # Initialize the AssistantAgent with access to shared memory
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. You can answer questions based on the provided PDF content.",
        model_client=model_client,
        #memory=shared_memory,  # Pass shared memory to the assistant
    )
    # Create a MultiModalMessage with the extracted content
    pdf_message = MultiModalMessage(
        content=["Here is the content from the PDF:", pdf_text],
        source="user",
    )

    # Send the PDF content to the assistant
    await assistant.run(task=pdf_message)


    # Initialize the UserProxyAgent with access to shared memory
    user_proxy = UserProxyAgent(
        name="user_proxy",
        input_func=input # Pass shared memory to the user proxy
    )

    # Define a termination condition for the group chat
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

    # Initialize the group chat with the assistant and user proxy
    group_chat = RoundRobinGroupChat(
        [user_proxy, assistant], termination_condition=termination
    )

    # Define a question to ask based on the PDF content
    question = "What is the main topic of the PDF?"

    # Send the question to the group chat
    stream = group_chat.run_stream(task=question)

    # Display the conversation in the console
    await Console(stream)


asyncio.run(main())