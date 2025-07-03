import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Gemini Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header styling */
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 30px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1rem;
        margin: 10px 0 0 0;
    }
    
    /* Chat container */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* Chat messages */
    .stChatMessage {
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    /* Link styling within chat messages */
    .stChatMessage a {
        color: #FFD700 !important;
        text-decoration: underline !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatMessage a:hover {
        color: #FFFF00 !important;
        text-shadow: 0 0 8px rgba(255, 255, 0, 0.5) !important;
    }
    
    /* Make code blocks more visible */
    .stChatMessage code {
        background-color: rgba(255, 255, 255, 0.2) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        padding: 15px 20px;
        font-size: 1rem;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header with custom styling
st.markdown("""
<div class="main-header">
    <h1>📅 Gemini Calendar Assistant</h1>
    <p>Your intelligent scheduling companion powered by AI</p>
</div>
""", unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = []

def format_response(reply):
    if isinstance(reply, dict) and reply.get("status") == "success":
        event_link = reply.get('eventLink', '')
        return (
            f"✅ **Event Created Successfully!**\n\n"
            f"🆔 **Event ID:** `{reply['eventId']}`\n\n"
            f"🔗 **Event Link:** 📅 [**Click here to open your event in Google Calendar**]({event_link})\n\n"
        )
    elif isinstance(reply, dict) and reply.get("status") == "error":
        return f"❌ **Error:** {reply.get('message', 'Something went wrong.')}"
    return str(reply)

# Show welcome message if no chat history
if not st.session_state.chat:
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: rgba(255, 255, 255, 0.1); border-radius: 15px; margin: 20px 0;">
        <h3 style="color: white; margin-bottom: 20px;">👋 Welcome to your AI Calendar Assistant!</h3>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; margin-bottom: 20px;">
            I can help you schedule meetings, create events, and manage your calendar. 
            Just tell me what you need!
        </p>
        <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
            <div style="background: rgba(255, 255, 255, 0.2); padding: 10px 15px; border-radius: 20px; color: white;">
                💼 Schedule meetings
            </div>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 10px 15px; border-radius: 20px; color: white;">
                📅 Create events
            </div>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 10px 15px; border-radius: 20px; color: white;">
                ⏰ Set reminders
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chat input with enhanced placeholder
user_input = st.chat_input("✨ Tell me what you'd like to schedule...")
if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.spinner("🤔 Let me help you with that..."):
        res = requests.post("http://localhost:8000/chat", json={"message": user_input})
        try:
            raw_reply = res.json().get("reply", "Something went wrong.")
            print(raw_reply)  # Debugging line to see raw reply
            # Try to parse reply as dict if it looks like one
            if isinstance(raw_reply, str) and raw_reply.strip().startswith("{"):
                try:
                    raw_reply = json.loads(raw_reply.replace("'", '"'))
                except json.JSONDecodeError:
                    pass  # Leave as-is if it still fails
            bot_reply = format_response(raw_reply)
        except Exception as e:
            bot_reply = f"❌ Error: {e}"
        st.session_state.chat.append({"role": "bot", "content": bot_reply})

# Display chat messages in a styled container
if st.session_state.chat:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat:
        st.chat_message(msg["role"]).markdown(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced clear chat button with better positioning
if st.session_state.chat:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
            st.session_state.chat = []
            st.rerun()

# Footer with additional info
st.markdown("""
<div style="text-align: center; padding: 20px; margin-top: 40px; color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;">
    <p>🔒 Your conversations are secure • 🚀 Powered by Gemini AI • 📱 Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
