import os
import openai
import anthropic
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Set the OpenAI and Anthropic API keys for external calls
openai.api_key = os.getenv('OPENAI_API_KEY')
anthropic.api_key = os.getenv('ANTHROPIC_API_KEY')

async def call_lm_studio_api(prompt, system_prompt, model=" "):
    try:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        messages = [{"role": "user", "content": prompt}]
        if system_prompt.strip():
            messages.insert(0, {"role": "system", "content": system_prompt})

        client = openai.OpenAI(
            api_key="lm-studio", 
            base_url="http://localhost:1234/v1"
        )
        completion = await asyncio.to_thread(client.chat.completions.create,
                                             model=model,
                                             messages=messages,
                                             temperature=0.7)
        return completion.choices[0].message['content']
    except Exception as e:
        return f"Error: {e}"

async def call_openai_api(prompt, system_prompt):
    try:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        messages = [{"role": "user", "content": prompt}]
        if system_prompt.strip():
            messages.insert(0, {"role": "system", "content": system_prompt})

        completion = await asyncio.to_thread(openai.chat.completions.create,
                                             model="gpt-4",
                                             messages=messages)
        return completion.choices[0].message['content']
    except Exception as e:
        return f"Error: {e}"

async def call_anthropic_api(prompt, system_prompt):
    try:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        client = anthropic.Anthropic()
        message_payload = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 1000,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        if system_prompt.strip():
            message_payload["system"] = system_prompt

        message = await asyncio.to_thread(client.messages.create, **message_payload)
        text_content = "\n".join(block.text for block in message.content)
        return text_content
    except Exception as e:
        return f"Error: {e}"

async def fetch_all_responses(prompt, system_prompt, model_name, use_lm_studio, use_openai, use_anthropic, update_ui_callback):
    tasks = []
    if use_lm_studio:
        tasks.append(update_ui_callback("LM Studio", call_lm_studio_api(prompt, system_prompt, model_name)))
    if use_openai:
        tasks.append(update_ui_callback("OpenAI", call_openai_api(prompt, system_prompt)))
    if use_anthropic:
        tasks.append(update_ui_callback("Anthropic", call_anthropic_api(prompt, system_prompt)))
    
    await asyncio.gather(*tasks)