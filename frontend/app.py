import streamlit as st
import requests
import json


st.title("📅 Gemini Calendar Assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

def format_response(reply):
    if isinstance(reply, dict) and reply.get("status") == "success":
        return (
            f"✅ **Event Created Successfully!**\n\n"
            f"🆔 **Event ID:** `{reply['eventId']}`\n\n"
            f"🔗 [Click to view the event]({reply['eventLink']})"
        )
    elif isinstance(reply, dict) and reply.get("status") == "error":
        return f"❌ **Error:** {reply.get('message', 'Something went wrong.')}"
    return str(reply)

user_input = st.chat_input("Schedule your meeting...")
if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
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

for msg in st.session_state.chat:
    st.chat_message(msg["role"]).markdown(msg["content"])
