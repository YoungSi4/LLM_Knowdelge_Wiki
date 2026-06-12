import streamlit as st
import os
import glob

st.set_page_config(layout="wide", page_title="Agentic LLM Wiki")

WIKI_DIR = "wiki"
if not os.path.exists(WIKI_DIR):
    os.makedirs(WIKI_DIR)

# Left Column: Wiki Viewer, Right Column: Chat
col1, col2 = st.columns([1, 1])

with col1:
    st.title("📚 Wiki Explorer")
    files = glob.glob(os.path.join(WIKI_DIR, "*.md"))
    wiki_pages = [os.path.basename(f).replace(".md", "") for f in files if ".tmp." not in f]
    
    if not wiki_pages:
        st.info("No wiki pages found. Start chatting to create one!")
    else:
        selected_page = st.selectbox("Select Page", ["INDEX"] + [p for p in wiki_pages if p != "INDEX"])
        page_path = os.path.join(WIKI_DIR, f"{selected_page}.md")
        if os.path.exists(page_path):
            with open(page_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())

with col2:
    st.title("🤖 Conductor Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask a question or add knowledge..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            if "추가해" in prompt or "작성해" in prompt or "넣어" in prompt:
                response = f"**[Draft Preview - 사전 보고]**\n\n지시하신 내용을 바탕으로 다음 내용을 위키에 추가하려고 합니다.\n\n> **대상 문서:** `New_Knowledge`\n> **주요 내용 요약:** {prompt}\n\n이 내용을 추가할까요?"
                st.markdown(response)
                # Placeholder buttons for MVP demonstration
                cA, cB = st.columns(2)
                cA.button("✅ Approve (Write via MCP)")
                cB.button("❌ Reject")
            else:
                response = "해당 내용에 대해 QA 에이전트에게 조회를 요청했습니다. (MCP 서버 검색 중...)"
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
