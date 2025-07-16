import os
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, Runner
from dotenv import load_dotenv
import chainlit as cl
import base64


load_dotenv()

keys =  os.getenv("GEMINI_API_KEY")

provider = AsyncOpenAI(
    api_key=keys,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client=provider
)

runconfig = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True,
)

Assistant = Agent(
    name="waseem",
    instructions="your primary work is to extract data from images/pictures"
)

@cl.on_chat_start
async def chat_start():
    await cl.Message(content="Welcome to AI We can Extract data from images plz upload images").send()

@cl.on_message
async def main(message : cl.Message):

    
    if not message.elements:
        await cl.Message(content="kindly upload Some images first").send()
        return
    
    img = message.elements[0]


    try:
        with open(img.path , "rb") as f:
            image_bites = f.read()
    except Exception as e:
        await cl.Message(content=f"failed to convert image in binary form with this error {str(e)}").send()
        return

    image_base64 = base64.b64encode(image_bites).decode('utf-8')
    await cl.Message(content="We are Sending Your Images to AI plz Wait").send()

    
    prompt = (
        "From this handwritten Urdu police application image, extract ONLY the following fields. "
        "Translate the content into English if needed, but DO NOT return the full application — "
        "only extract and return these fields as plain text (NOT JSON):\n\n"
        "Fields:\n"
        "1. Name (only name in English)\n"
        "2. Mobile Model\n"
        "3. IMEI Number\n"
        "4. Phone Number (only the contact number mentioned at the end of application)\n"
        "5. Date\n"
        "6. Time\n"
        "7. Type (Lost/Snatched/Theft)"

        
    )
    combined_input = [prompt , image_base64]
    
    try:
        result =await Runner.run(
            Assistant,
            input= combined_input,
            run_config=runconfig,
        )
    
        final_result = result.final_output
        if not final_result:
            await cl.Message(content="NO text extracted kindly check your image path").send()
    except Exception as e:
        await cl.Message(content=f"Output Failded plz check you code  as error : {str(e)}").send()
        return
    
    await cl.Message(content=f"Extracted Data\n\n {final_result}").send()