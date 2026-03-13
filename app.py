# app.py — Streamlit frontend
import streamlit as st
from dotenv import load_dotenv
from agent import ask

load_dotenv()  # loads OPENAI_API_KEY from .env

st.set_page_config(page_title="Weather & News Assistant", page_icon="🌤️")
st.title("🌤️ Weather & News Assistant")
st.caption("Powered by Open-Meteo · HackerNews · Claude · MCP")

# ── Chat history ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── User input ────────────────────────────────────────────────────────────────
EXAMPLES = [
    "What's the weather in Tokyo?",
    "Show me the top 5 news stories",
    "What's the weather in London and the latest tech news?",
]

if not st.session_state.messages:
    st.info("Try asking:\n" + "\n".join(f"- *{e}*" for e in EXAMPLES))

if prompt := st.chat_input("Ask about weather or news…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            answer = ask(prompt)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
