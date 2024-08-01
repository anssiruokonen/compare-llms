import streamlit as st
import asyncio
from api_calls import fetch_all_responses

st.title("LLM Comparison")

# Default system prompt
default_system_prompt = "You are a helpful, smart, kind, and efficient AI assistant. You always fulfill the user's requests to the best of your ability."

# System prompt input
system_prompt = st.text_area("Enter the system prompt:", value=default_system_prompt)

# Checkboxes to select which LLMs to call
use_lm_studio = st.checkbox("Use LM Studio", value=True)
use_openai = st.checkbox("Use OpenAI", value=True)
use_anthropic = st.checkbox("Use Anthropic", value=True)

# Input for LM Studio model name, shown only if the LM Studio checkbox is checked
if use_lm_studio:
    lm_studio_model_name = st.text_input("Enter the LM Studio model name:", "microsoft/Phi-3-mini-4k-instruct-gguf")

# Text area for the prompt
prompt = st.text_area("Enter your prompt:")

# Asynchronous update callback to update the UI
async def update_ui_callback(api_name, task):
    response = await task
    st.subheader(f"{api_name} Response")
    st.write(response)

# Function to call LLMs and display responses
def compare_responses():
    if prompt.strip():
        model_name = lm_studio_model_name if use_lm_studio else None
        asyncio.run(fetch_all_responses(prompt, system_prompt, model_name, use_lm_studio, use_openai, use_anthropic, update_ui_callback))
    else:
        st.error("Prompt must not be empty.")

# Button to compare responses
if st.button("Compare Responses", key="compare_responses"):
    compare_responses()

# Automatically call compare_responses when the prompt is entered
if st.session_state.get('last_prompt') != prompt:
    st.session_state['last_prompt'] = prompt
    compare_responses()