import streamlit as st
import asyncio
import aiohttp
from api_calls import call_lm_studio_api, call_openai_api, call_anthropic_api

st.set_page_config(layout="wide")  # To ensure the page uses the full width

st.title("LLM Comparison")

# Initialize session state variables for conversation history and view mode
if "lm_studio_conversation" not in st.session_state:
    st.session_state["lm_studio_conversation"] = []
if "openai_conversation" not in st.session_state:
    st.session_state["openai_conversation"] = []
if "anthropic_conversation" not in st.session_state:
    st.session_state["anthropic_conversation"] = []
if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "main"
if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = None
if "rerun_trigger" not in st.session_state:
    st.session_state["rerun_trigger"] = 0
if "lm_studio_models" not in st.session_state:
    st.session_state["lm_studio_models"] = []

# Default system prompt
default_system_prompt = "You are a helpful, smart, kind, and efficient AI assistant. You always fulfill the user's requests to the best of your ability."

async def fetch_lm_studio_models():
    url = "http://localhost:1234/v1/models"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    st.session_state["lm_studio_models"] = [model["id"] for model in data.get("data", [])]
                else:
                    st.session_state["lm_studio_models"] = []
                    st.error(f"Failed to fetch LM Studio models. Status code: {response.status}")
    except aiohttp.ClientError as e:
        st.session_state["lm_studio_models"] = []
        st.error(f"Error connecting to LM Studio: {str(e)}")
    
    # Uncheck the use_lm_studio checkbox if no models are available
    if not st.session_state["lm_studio_models"]:
        st.session_state["use_lm_studio"] = True

async def fetch_all_responses(lm_studio_messages, openai_messages, anthropic_messages, system_prompt, model_name, use_lm_studio, use_openai, use_anthropic, update_ui_callback):
    tasks = []
    if use_lm_studio and lm_studio_messages is not None:
        tasks.append(update_ui_callback("LM Studio", call_lm_studio_api(lm_studio_messages, model_name)))
    if use_openai and openai_messages is not None:
        tasks.append(update_ui_callback("OpenAI", call_openai_api(openai_messages)))
    if use_anthropic and anthropic_messages is not None:
        tasks.append(update_ui_callback("Anthropic", call_anthropic_api(anthropic_messages, system_prompt)))
    
    await asyncio.gather(*tasks)

def show_main_page():
    # System prompt input
    system_prompt = st.text_area("Enter the system prompt:", value=default_system_prompt)

    # Checkboxes to select which LLMs to call
    use_lm_studio = st.checkbox("Use LM Studio", value=st.session_state.get("use_lm_studio", False))
    st.session_state["use_lm_studio"] = use_lm_studio  # Update session state
    use_openai = st.checkbox("Use OpenAI", value=True)
    use_anthropic = st.checkbox("Use Anthropic", value=True)

    # Fetch LM Studio models when checkbox is selected
    if use_lm_studio and not st.session_state["lm_studio_models"]:
        asyncio.run(fetch_lm_studio_models())

    # Dropdown for LM Studio model selection
    if use_lm_studio and st.session_state["lm_studio_models"]:
        lm_studio_model_name = st.selectbox("Select LM Studio model:", st.session_state["lm_studio_models"])
    else:
        lm_studio_model_name = None

    # Text area for the prompt
    prompt = st.text_area("Enter your prompt:")

    # Asynchronous update callback to update the UI
    async def update_ui_callback(api_name, task):
        response = await task
        st.session_state[f"{api_name.replace(' ', '_').lower()}_conversation"].append({"role": "assistant", "content": response})
        st.subheader(f"{api_name} Response")
        st.write(response)

    # Function to call LLMs and display responses
    def compare_responses():
        if prompt.strip():
            # Clear previous conversation history
            st.session_state["lm_studio_conversation"] = []
            st.session_state["openai_conversation"] = []
            st.session_state["anthropic_conversation"] = []

            model_name = lm_studio_model_name if use_lm_studio else None

            # Update session state with the new user message
            user_message = {"role": "user", "content": prompt}
            if use_lm_studio:
                st.session_state["lm_studio_conversation"].append(user_message)
            if use_openai:
                st.session_state["openai_conversation"].append(user_message)
            if use_anthropic:
                st.session_state["anthropic_conversation"].append(user_message)

            # Prepare messages for each LLM
            lm_studio_messages = [{"role": "system", "content": system_prompt}] + st.session_state["lm_studio_conversation"] if use_lm_studio else None
            openai_messages = [{"role": "system", "content": system_prompt}] + st.session_state["openai_conversation"] if use_openai else None
            anthropic_messages = st.session_state["anthropic_conversation"]

            asyncio.run(fetch_all_responses(lm_studio_messages, openai_messages, anthropic_messages,
                                            system_prompt, model_name, use_lm_studio, use_openai, use_anthropic, update_ui_callback))
        else:
            st.error("Prompt must not be empty.")

    # Button to compare responses
    if st.button("Compare Responses", key="compare_responses"):
        compare_responses()

async def update_ui_callback(api_name, task):
    response = await task
    st.session_state[f"{api_name.replace(' ', '_').lower()}_conversation"].append({"role": "assistant", "content": response})
    st.subheader(f"{api_name} Response")
    st.write(response)

def show_chat_page():
    st.title("Continue Conversation")

    # Select which chat to continue
    chat_options = ["LM Studio", "OpenAI", "Anthropic"]
    selected_chat = st.selectbox("Select a chat to continue", chat_options)

    if selected_chat:
        st.session_state["current_chat"] = selected_chat

    if st.session_state["current_chat"]:
        api_name = st.session_state["current_chat"]
        
        # Initialize session state variables for conversation history if not already initialized
        if f"{api_name.replace(' ', '_').lower()}_conversation" not in st.session_state:
            st.session_state[f"{api_name.replace(' ', '_').lower()}_conversation"] = []

        # Display conversation history
        st.subheader(f"{api_name} Conversation History")
        for message in st.session_state[f"{api_name.replace(' ', '_').lower()}_conversation"]:
            st.write(f"{message['role'].capitalize()}: {message['content']}")

        # Create a form
        with st.form(key='chat_form'):
            prompt = st.text_input("Enter your message:")
            submit_button = st.form_submit_button(label='Continue Conversation')

        # Handle form submission
        if submit_button:
            if prompt.strip():
                user_message = {"role": "user", "content": prompt}
                st.session_state[f"{api_name.replace(' ', '_').lower()}_conversation"].append(user_message)

                if api_name in ["LM Studio", "OpenAI"]:
                    messages = [{"role": "system", "content": default_system_prompt}] + st.session_state[f"{api_name.replace(' ', '_').lower()}_conversation"]
                else:  # Anthropic
                    messages = st.session_state[f"{api_name.replace(' ', '_').lower()}_conversation"]

                if api_name == "LM Studio":
                    asyncio.run(update_ui_callback(api_name, call_lm_studio_api(messages)))
                elif api_name == "OpenAI":
                    asyncio.run(update_ui_callback(api_name, call_openai_api(messages)))
                elif api_name == "Anthropic":
                    asyncio.run(update_ui_callback(api_name, call_anthropic_api(messages, default_system_prompt)))

                # Force a rerun to update the displayed conversation history
                st.rerun()
            else:
                st.error("Prompt must not be empty.")
            



# Display the buttons at the top
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Main"):
        st.session_state["view_mode"] = "main"
        st.session_state["rerun_trigger"] += 1

with col2:
    if st.button("Chat"):
        st.session_state["view_mode"] = "chat"
        st.session_state["rerun_trigger"] += 1

with col3:
    if st.button("Clear All History"):
        st.session_state["lm_studio_conversation"] = []
        st.session_state["openai_conversation"] = []
        st.session_state["anthropic_conversation"] = []
        st.success("All conversation histories have been cleared.")
        st.session_state["rerun_trigger"] += 1

if st.session_state["view_mode"] == "main":
    show_main_page()
else:
    show_chat_page()