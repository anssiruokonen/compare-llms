import requests
import os
from dotenv import load_dotenv
import openai
import anthropic

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
anthropic.api_key =os.getenv('ANTHROPIC_API_KEY')

def call_lm_studio_api(prompt, model):
    client = openai.OpenAI(
        api_key="lm-studio", 
        base_url="http://localhost:1234/v1"
    )
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature = 0.7,
    )
    return completion.choices[0].message.content


def call_openai_api(prompt):
    client = openai
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


def call_anthropic_api(prompt):
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
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
    )
    # Extracting text content from the response
    text_content = "\n".join(block.text for block in message.content)
    return text_content
  
# For testing purposes
if __name__ == "__main__":
    prompt = "Write a haiku about AI."
    print("OpenAI Response:", call_openai_api(prompt).get('choices', [{}])[0].get('message', {}).get('content', 'No response'))
    print("Anthropic Response:", call_anthropic_api(prompt).content)