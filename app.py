import streamlit as st
import requests
import json
from datetime import datetime
import base64

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Streamlit app configuration
st.set_page_config(page_title="Llama3.2 Chatbot", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# Function to get available models from Ollama
def get_ollama_models():
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except requests.RequestException:
        return ["llama3.2:1b"]  # Fallback to default model

# Sidebar for settings
st.sidebar.title("🛠️ Chatbot Settings")
model = st.sidebar.selectbox("📦 Model", get_ollama_models(), index=0, help="Select the Ollama model to use.")
system_prompt = st.sidebar.text_area("📝 System Prompt", value="You are a helpful AI assistant.", help="Define the assistant's behavior.")
temperature = st.sidebar.slider("🌡️ Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, help="Controls randomness: lower is more focused, higher is more creative.")
top_p = st.sidebar.slider("🎲 Top-P", min_value=0.0, max_value=1.0, value=0.9, step=0.1, help="Controls diversity via nucleus sampling.")
max_tokens = st.sidebar.number_input("📏 Max Tokens", min_value=10, max_value=1000, value=500, step=10, help="Maximum number of tokens in response.")
theme = st.sidebar.selectbox("🎨 Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "light" else 1, help="Switch between light and dark theme.")

# Update theme
if theme.lower() != st.session_state.theme:
    st.session_state.theme = theme.lower()
    st.rerun()

# Apply custom CSS based on theme
st.markdown(f"""
    <style>
    .stApp {{
        {'background-color: #ffffff; color: #000000;' if st.session_state.theme == 'light' else 'background-color: #1e1e1e; color: #ffffff;'}
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .stSidebar {{
        {'background-color: #ffffff; color: #000000;' if st.session_state.theme == 'light' else 'background-color: #1e1e1e; color: #ffffff;'}
    }}
    .stSidebar .stSelectbox label, .stSidebar .stSlider label, .stSidebar .stTextArea label, .stSidebar .stNumberInput label {{
        color: {'#000000' if st.session_state.theme == 'light' else '#ffffff'} !important;
    }}
    .stMarkdown, .stTitle, .stText, .stChatMessage, .stChatMessage * {{
        color: {'#000000' if st.session_state.theme == 'light' else '#ffffff'} !important;
    }}
    .stChatMessage.user {{
        background-color: {'#d1e7ff' if st.session_state.theme == 'light' else '#2a4b8d'};
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .stChatMessage.assistant {{
        background-color: {'#e8ecef' if st.session_state.theme == 'light' else '#343a40'};
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .stButton>button {{
        background: {'linear-gradient(45deg, #26a69a, #4fc3f7)' if st.session_state.theme == 'light' else 'linear-gradient(45deg, #00796b, #29b6f6)'};
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: 500;
        transition: background-color 0.3s;
    }}
    .stButton>button:hover {{
        background: {'linear-gradient(45deg, #00897b, #29b6f6)' if st.session_state.theme == 'light' else 'linear-gradient(45deg, #00695c, #0288d1)'};
        cursor: pointer;
    }}
    .stSidebar .stSelectbox, .stSidebar .stSlider, .stSidebar .stTextArea, .stSidebar .stNumberInput {{
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'};
        border-radius: 8px;
        padding: 8px;
    }}
    .stSidebar .stSelectbox div, .stSidebar .stSlider div, .stSidebar .stTextArea textarea, .stSidebar .stNumberInput input {{
        color: {'#000000' if st.session_state.theme == 'light' else '#ffffff'};
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'};
    }}
    .stSlider button, .stNumberInput button {{
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'} !important;
        color: {'#000000' if st.session_state.theme == 'light' else '#ffffff'} !important;
    }}
    
    /* Target the bottom container area */
    div[data-testid="stBottom"] {{
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'} !important;
    }}
    div[data-testid="stBottom"] > div {{
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'} !important;
    }}
    /* Target the chat input container specifically */
    section[data-testid="stChatInput"] {{
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'} !important;
    }}
    .main {{
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'} !important;
    }}
    .stApp > div {{
        background-color: {'#ffffff' if st.session_state.theme == 'light' else '#1e1e1e'} !important;
    }}
    .download-link {{
        display: inline-block;
        background: {'linear-gradient(45deg, #26a69a, #4fc3f7)' if st.session_state.theme == 'light' else 'linear-gradient(45deg, #00796b, #29b6f6)'};
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 10px;
    }}
    .download-link:hover {{
        background: {'linear-gradient(45deg, #00897b, #29b6f6)' if st.session_state.theme == 'light' else 'linear-gradient(45deg, #00695c, #0288d1)'};
    }}
    </style>
""", unsafe_allow_html=True)

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Function to download chat history
def download_chat_history():
    chat_text = "\n".join([f"{msg['role'].capitalize()} ({msg['timestamp']}): {msg['content']}" for msg in st.session_state.messages])
    b64 = base64.b64encode(chat_text.encode()).decode()
    filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" class="download-link">📥 Download Chat History</a>'
    return href

# Function to count tokens (approximate)
def count_tokens(text):
    return len(text.split())

# Function to trim response to max_tokens while preserving structure
def trim_to_max_tokens(text, max_tokens):
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    # Try to trim at sentence boundaries (approximate with periods)
    sentences = text.split('. ')
    trimmed_text = ""
    token_count = 0
    for sentence in sentences:
        sentence_tokens = sentence.split()
        if token_count + len(sentence_tokens) <= max_tokens:
            trimmed_text += sentence + ". "
            token_count += len(sentence_tokens)
        else:
            break
    return trimmed_text.strip()

# Main chat interface
st.title("🤖 Llama3.2 Chatbot")
st.markdown("💬 Interact with the Llama3.2 model. Adjust settings in the sidebar and type your message below.", unsafe_allow_html=True)

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(f"**📅 {message['timestamp']}**")
        st.markdown(message["content"])

# User input
prompt = st.chat_input("✍️ Type your message here...")
if prompt:
    # Append user message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"**📅 {timestamp}**")
        st.markdown(prompt)
    
    # Prepare payload for Ollama API
    url = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    # Display loading spinner
    with st.spinner("⏳ Generating response..."):
        try:
            # Send POST request
            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()
            
            # Collect full streamed response
            assistant_response = ""
            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                for line in response.iter_lines():
                    if line:
                        try:
                            message_dict = json.loads(line.decode('utf-8'))
                            content = message_dict['message']['content']
                            assistant_response += content
                            placeholder.markdown(assistant_response)
                        except json.JSONDecodeError:
                            st.error("Failed to parse response from Ollama API.")
                            break
                
                # Trim response to max_tokens while preserving structure
                final_response = trim_to_max_tokens(assistant_response, max_tokens)
                
                # Update with trimmed response
                placeholder.markdown(final_response)
                
                # Add timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(f"**📅 {timestamp}**")
            
            # Append assistant response
            st.session_state.messages.append({"role": "assistant", "content": final_response, "timestamp": timestamp})
            
        except requests.RequestException as e:
            st.error(f"🚨 Error connecting to Ollama API: {e}. Ensure the Ollama server is running (`ollama serve` in `C:\\Users\\P SRIKANTH\\Downloads\\ollama-windows-amd64`).")
    
    # Display download link
    st.markdown(download_chat_history(), unsafe_allow_html=True)