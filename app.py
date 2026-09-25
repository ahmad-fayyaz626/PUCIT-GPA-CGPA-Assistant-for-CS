import os
import uuid
from datetime import datetime

import streamlit as st
from langchain.messages import HumanMessage, ToolMessage

from agent import agent

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PUCIT GPA Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# INLINE SVG ICONS (rendered as real markup, not text)
# ─────────────────────────────────────────────────────────────
GRAD_CAP_SVG = """
<svg width="20" height="20" viewBox="0 0 24 24" fill="none"
     xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;flex-shrink:0;">
  <path d="M12 3L1 8l11 5 9-4.09V17h2V8L12 3z" fill="#1A1A1A"/>
  <path d="M5 10.18v3.64c0 1.5 3.13 3.18 7 3.18s7-1.68 7-3.18v-3.64l-7 3.18-7-3.18z"
        fill="#1A1A1A" opacity="0.55"/>
</svg>
"""

# ─────────────────────────────────────────────────────────────
# THEME — neutral grays, tight spacing (Claude/ChatGPT-style)
# ─────────────────────────────────────────────────────────────
SIDEBAR_BG = "#FAFAF8"
BORDER = "#E8E6E1"
TEXT_PRIMARY = "#1A1A1A"
TEXT_MUTED = "#8A8A85"
HOVER_BG = "#F0EFEB"
ACTIVE_BG = "#ECECE7"

st.markdown(
    f"""
    <style>
        .stApp {{ background-color: #FFFFFF; }}

        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] > div {{
            padding-top: 0.75rem;
        }}

        .brand-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            color: {TEXT_PRIMARY};
            padding: 0.25rem 0.4rem 1rem 0.4rem;
        }}

        div[data-testid="stSidebar"] button[kind="secondary"] {{
            background-color: transparent;
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.85rem;
            padding: 0.4rem 0.6rem;
            text-align: left;
            transition: background-color 0.12s ease;
        }}
        div[data-testid="stSidebar"] button[kind="secondary"]:hover {{
            background-color: {HOVER_BG};
            border-color: {BORDER};
            color: {TEXT_PRIMARY};
        }}

        div[data-testid="stSidebar"] button[kind="primary"] {{
            background-color: {ACTIVE_BG} !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid transparent !important;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.85rem;
            text-align: left;
            padding: 0.4rem 0.6rem;
        }}

        div[data-testid="stSidebar"] .stButton {{
            margin-bottom: 2px;
        }}

        .sidebar-label {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            color: {TEXT_MUTED};
            padding: 0.9rem 0.4rem 0.3rem 0.4rem;
        }}

        .sidebar-about {{
            font-size: 0.78rem;
            color: {TEXT_MUTED};
            line-height: 1.4;
            padding: 0.3rem 0.4rem;
        }}

        .app-header {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 0.9rem;
        }}
        .app-header h1 {{
            font-size: 1.3rem;
            margin: 0;
            font-weight: 650;
            color: {TEXT_PRIMARY};
        }}
        .app-subtitle {{
            color: {TEXT_MUTED};
            font-size: 0.88rem;
            margin-bottom: 1.1rem;
        }}

        div[data-testid="stChatMessage"] {{
            border-radius: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE — multi-chat structure
# ─────────────────────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None


def create_new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "title": "New chat",
        "created": datetime.now(),
        "messages": [],
    }
    st.session_state.active_chat_id = chat_id


def set_active_chat(chat_id: str):
    st.session_state.active_chat_id = chat_id


if not st.session_state.chats:
    create_new_chat()
elif st.session_state.active_chat_id is None:
    st.session_state.active_chat_id = next(iter(st.session_state.chats))

active_chat = st.session_state.chats[st.session_state.active_chat_id]

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div class='brand-row'>{GRAD_CAP_SVG}<span>PUCIT GPA Assistant</span></div>",
        unsafe_allow_html=True,
    )

    if st.button("New chat", key="new_chat_btn", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.markdown("<div class='sidebar-label'>Recents</div>", unsafe_allow_html=True)

    sorted_chats = sorted(
        st.session_state.chats.items(),
        key=lambda kv: kv[1]["created"],
        reverse=True,
    )

    if not sorted_chats:
        st.caption("No chats yet.")
    else:
        for chat_id, chat_data in sorted_chats:
            is_active = chat_id == st.session_state.active_chat_id
            label = chat_data["title"]
            if st.button(
                label,
                key=f"chat_btn_{chat_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                set_active_chat(chat_id)
                st.rerun()

    st.markdown("<div class='sidebar-label'>About</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sidebar-about'>Ask about your semester GPA, CGPA, "
        "required GPA for a target CGPA, or course outlines.</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='app-header'>{GRAD_CAP_SVG}<h1>PUCIT GPA & CGPA Assistant</h1></div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='app-subtitle'>Your academic companion for semester GPA, "
    "cumulative CGPA, and course-related queries.</div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────────────────────
if not active_chat["messages"]:
    st.info(
        'Start by asking something like *"What GPA do I need this semester '
        'to reach a 3.5 CGPA?"*'
    )

for message in active_chat["messages"]:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    else:
        with st.chat_message("assistant"):
            st.write(message.content)

# ─────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about your GPA or CGPA...")

if user_input:
    active_chat["messages"].append(HumanMessage(content=user_input))

    if active_chat["title"] == "New chat":
        active_chat["title"] = (
            user_input[:32] + "…" if len(user_input) > 32 else user_input
        )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent.invoke({"messages": active_chat["messages"]})

        new_messages = response["messages"]
        active_chat["messages"] = new_messages

        st.write(new_messages[-1].content)

        # Check if save_report tool was called in this turn
        for msg in new_messages:
            if isinstance(msg, ToolMessage) and msg.content.startswith(
                "Report saved to "
            ):
                saved_filename = msg.content.replace("Report saved to ", "").strip()

                if os.path.exists(saved_filename):
                    with open(saved_filename, "r", encoding="utf-8") as f:
                        file_bytes = f.read()

                    st.download_button(
                        label=f"Download {saved_filename}",
                        data=file_bytes,
                        file_name=saved_filename,
                        mime="text/plain",
                        key=f"download_{saved_filename}_{len(new_messages)}",
                    )
