import streamlit as st
import datetime
import google.generativeai as genai
import time
import random
import os

# Load environment variables (recommended for sensitive data like API keys)
from dotenv import load_dotenv
load_dotenv()

private_google_api_key = os.getenv("GOOGLE_API_KEY")

# Set page configuration
st.set_page_config(
    page_title="Chat with Gemini Pro",
    page_icon=""
)

def save_chat_history(history, filename):
    """Saves chat history to a file with a timestamp."""
    with open(filename, 'w') as f:
        for message in history:
            role = "assistant" if message.role == 'model' else message.role
            text = message.parts[0].text
            f.write(f"{role}: {text}\n")

def load_chat_history(filename, default_history=[]):
    """Loads chat history from a file, returning an empty list if no file exists."""
    if not os.path.exists(filename):
        return default_history

    with open(filename, 'r') as f:
        history = []
        for line in f:
            role, text = line.strip().split(':', 1)
            history.append(genai.types.conversation_history_types.ConversationHistoryEntry(role=role, parts=[genai.types.text_types.TextPart(text=text)]))
    return history

def get_daily_chat_history_filename():
    """Returns the filename for the chat history of the current day."""
    today = datetime.date.today()
    return f"chat_history_{today.strftime('%Y-%m-%d')}.txt"

# Session state variables
st.session_state.app_key = private_google_api_key
st.session_state.history = load_chat_history(get_daily_chat_history_filename())

# Title and caption
st.title("Chat with Gemini Pro")
st.caption("A Chatbot Powered by Google Gemini Pro")

# Check for API key
if "app_key" not in st.session_state:
    app_key = st.text_input("Please enter your Gemini API Key", type='password')
    if app_key:
        st.session_state.app_key = app_key

# Configure connection
try:
    genai.configure(api_key=st.session_state.app_key)
except AttributeError as e:
    st.warning("Please Put Your Gemini API Key First")

# Initialize model and chat
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=st.session_state.history)

# Sidebar
with st.sidebar:
    # Chat options
    st.subheader("Chat Options")
    st.button("Clear Chat Window", use_container_width=True, type="primary")
    st.write("---")

    # Save Chat History button
    if st.button("Save Chat History", use_container_width=True, type="primary"):
        filename = get_daily_chat_history_filename()
        save_chat_history(chat.history, filename)  # Save the current chat history
        st.success(f"Chat history saved to {filename}")

    # Additional menus (replace with desired content)
    st.subheader("Additional Menus")
    st.button("Help", key="help_button")
    if st.session_state["help_button"]:
        st.write("This is the Help menu content.")
    st.button("Settings", key="settings_button")
    if st.session_state["settings_button"]:
        st.write("This is the Settings menu content.")

# Chat history display
for message in chat.history:
    role = "assistant" if message.role == 'model' else message.role
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# User input and response generation
if "app_key" in st.session_state:
    if prompt := st.chat_input(""):
        prompt = prompt.replace('\n', ' \n')
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                full_response = ""
                for chunk in chat.send_message(prompt, stream=True):
                    word_count = 0
                    random_int = random.randint(5, 10)
                    for word in chunk.text:
                        full_response += word
                        word_count += 1
                        if word_count == random_int:
                            time.sleep(0.05)
                            message_placeholder.markdown(full_response + "_")
                            word_count = 0
                            random_int = random.randint(5, 10)
                message_placeholder.markdown(full_response)
            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.exception(e)
            st.session_state.history = chat.history