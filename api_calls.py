import os
import openai
import anthropic
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Set the OpenAI and Anthropic API keys for external calls
openai.api_key = os.getenv('OPENAI_API_KEY')
anthropic.api_key = os.getenv('ANTHROPIC_API_KEY')

async def call_lm_studio_api(messages, model=""):
    try:
        client = openai.OpenAI(
            api_key="lm-studio", 
            base_url="http://localhost:1234/v1"
        )
        completion = await asyncio.to_thread(client.chat.completions.create,
                                             model=model,
                                             messages=messages,
                                             temperature=0.7)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

async def call_openai_api(messages):
    try:
        completion = await asyncio.to_thread(openai.chat.completions.create,
                                             model="gpt-4",
                                             messages=messages)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

async def call_anthropic_api(messages, system_prompt):
    try:
        client = anthropic.Anthropic()
        message_payload = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 1000,
            "temperature": 0,
            "system": system_prompt,
            "messages": messages
        }
        message = await asyncio.to_thread(client.messages.create, **message_payload)
        text_content = "\n".join(block.text for block in message.content)
        return text_content
    except Exception as e:
        return f"Error: {e}"

async def fetch_all_responses(lm_studio_messages, openai_messages, anthropic_messages, system_prompt, model_name, use_lm_studio, use_openai, use_anthropic, update_ui_callback):
    tasks = []
    if use_lm_studio and lm_studio_messages is not None:
        tasks.append(update_ui_callback("LM Studio", call_lm_studio_api(lm_studio_messages, model_name)))
    if use_openai and openai_messages is not None:
        tasks.append(update_ui_callback("OpenAI", call_openai_api(openai_messages)))
    if use_anthropic and anthropic_messages is not None:
        tasks.append(update_ui_callback("Anthropic", call_anthropic_api(anthropic_messages, system_prompt)))
    
    await asyncio.gather(*tasks)