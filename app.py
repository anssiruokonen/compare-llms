import streamlit as st
from api_calls import call_lm_studio_api, call_openai_api, call_anthropic_api

st.title("LLM Comparison")

# Checkboxes to select which LLMs to call
use_lm_studio = st.checkbox("Use LM Studio", value=True)
use_openai = st.checkbox("Use OpenAI", value=True)
use_anthropic = st.checkbox("Use Anthropic", value=True)

# Input for LM Studio model name, shown only if the LM Studio checkbox is checked
if use_lm_studio:
    lm_studio_model_name = st.text_input("Enter the LM Studio model name:", "")

# Text area for the prompt
prompt = st.text_area("Enter your prompt:")

# Function to call LLMs and display responses
def compare_responses():
    if prompt:
        if use_lm_studio:
            lm_studio_response = call_lm_studio_api(prompt, lm_studio_model_name)
            st.subheader("LM Studio Response")
            st.write(lm_studio_response)

        if use_openai:
            openai_response = call_openai_api(prompt)
            st.subheader("OpenAI Response")
            st.write(openai_response)

        if use_anthropic:
            anthropic_response = call_anthropic_api(prompt)
            st.subheader("Anthropic Response")
            st.write(anthropic_response)

# Button to compare responses
if st.button("Compare Responses", key="compare_responses"):
    compare_responses()

# Automatically call compare_responses when the prompt is entered
if st.session_state.get('last_prompt') != prompt:
    st.session_state['last_prompt'] = prompt
    compare_responses()