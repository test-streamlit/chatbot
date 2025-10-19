import streamlit as st
import streamlit.components.v1 as components
import openai
import os
import json
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def log_to_console(message):
    # Escape quotes and use JSON for safe logging
    safe_message = json.dumps(str(message))
    html_content = """
        <script>
            console.log('🤖 ' + """ + safe_message + """);
        </script>
        """
    components.html(html_content, height=0)

def get_completion_from_messages(client, messages, model="gpt-4o", temperature=0):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def main():
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Chatbot")
    st.markdown("---")
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "🟢 Connected")
    with col2:
        st.metric("Messages", len(st.session_state.get("messages", [])) - 1)
    with col3:
        st.metric("Model", "GPT-4o")
    
    st.markdown("---")
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OPENAI_API_KEY not found in environment variables!")
        st.stop()
    
    client = openai.OpenAI(api_key=api_key)
    
    # Initialize conversation history
    if "messages" not in st.session_state:
        log_to_console("First time running the app")
        log_to_console(f"st.session_state: {st.session_state}")
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful and friendly AI assistant."}
        ]
    log_to_console(f"st.session_state: {st.session_state}")

    # Initialize model and temperature in session state if not exists
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4o"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.0
    
    # Display chat history
    for message in st.session_state.messages:
        
        # st.write(f"{message['role']}: {message['content']}")
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
    # Chat input
    prompt = st.chat_input("Type your message:")
    log_to_console(f"prompt: {prompt}")

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        log_to_console(f"st.session_state: {st.session_state}")

        # Get AI response
        response = get_completion_from_messages(client, st.session_state.messages, model=st.session_state.model, temperature=st.session_state.temperature)
        
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            log_to_console(f"st.session_state: {st.session_state}")
            st.rerun()  # Forces Streamlit to rerun the entire script, clearing the page and redisplaying everything with updated session state

    # Sidebar with settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        st.session_state.model = st.selectbox(
            "Choose Model",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            index=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"].index(st.session_state.model)
        )
        
        # Temperature slider
        st.session_state.temperature = st.slider(
            "Creativity (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Higher values make responses more creative, lower values make them more focused"
        )
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [
                {"role": "system", "content": "You are a helpful and friendly AI assistant."}
            ]
            st.rerun()
        
        # Display chat info
        st.markdown("---")
        st.markdown(f"**Messages in conversation:** {len(st.session_state.messages) - 1}")
        
        # API key status
        st.markdown("---")
        st.markdown("**API Key Status:** ✅ Connected")

if __name__ == "__main__":
    main() 