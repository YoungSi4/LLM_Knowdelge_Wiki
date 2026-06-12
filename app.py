import streamlit as st
import os
import glob
import subprocess
import json
import sys

# Import MCP logic directly for Streamlit Conductor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools.mcp_server import do_search_wiki, do_read_page, do_update_page

st.set_page_config(layout="wide", page_title="Agentic LLM Wiki")

WIKI_DIR = "wiki"
RAW_DIR = "raw"
os.makedirs(WIKI_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

def run_agent(agent_name, prompt):
    try:
        with open(f"harness/subagents/{agent_name}.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        return f"[ERROR] Agent config {agent_name} not found."
    
    system_prompt = config.get("system_prompt", "")
    full_prompt = f"SYSTEM: {system_prompt}\n\nUSER_REQUEST: {prompt}"
    
    # 과거 대화 맥락(History)이 섞이는 것을 방지하기 위해 새로운 세션 ID(무작위)를 부여하거나 독립적으로 실행합니다.
    import uuid
    session_id = str(uuid.uuid4())
    # 윈도우 커맨드 라인 길이 제한(8191자)을 우회하기 위해 프롬프트를 STDIN으로 넘깁니다.
    cmd = ["gemini.cmd", "--session-id", session_id, "--approval-mode", "yolo", "--skip-trust", "-m", "gemini-3.1-flash-lite", "-o", "json", "-p", " "]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", input=full_prompt)
    
    if result.returncode != 0:
        return f"[ERROR] Exit Code {result.returncode}\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}"
    
    try:
        data = json.loads(result.stdout)
        resp = data.get("response") or data.get("result")
        if resp is None:
             return f"[ERROR] JSON has no response/result field.\nRaw: {result.stdout}"
        return resp
    except Exception as e:
        return f"[ERROR] JSON parse failed: {str(e)}\nRaw output: {result.stdout}"

col1, col2 = st.columns([1, 1])

with col1:
    st.title("📚 Wiki Explorer")
    files = glob.glob(os.path.join(WIKI_DIR, "*.md"))
    wiki_pages = [os.path.basename(f).replace(".md", "") for f in files if ".tmp." not in f]
    
    if not wiki_pages:
        st.info("No wiki pages found. Drop a file in `raw/` and ask the chatbot to ingest it!")
    else:
        options = ["INDEX"] + [p for p in wiki_pages if p != "INDEX"] if "INDEX" in wiki_pages else wiki_pages
        selected_page = st.selectbox("Select Page", options)
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
            
    if st.session_state.get("pending_approval"):
        st.warning("⚠️ 작성 대기 중인 초안이 있습니다. 승인하시겠습니까?")
        cA, cB = st.columns(2)
        if cA.button("✅ Approve (Write via MCP)"):
            with st.spinner("위키 문서에 저장 중입니다..."):
                final_md = st.session_state.pending_approval["final_md"]
                target_page = st.session_state.pending_approval["page_name"]
                
                mcp_res = do_update_page(target_page, final_md)
                
                msg = f"{mcp_res}\n\n작성이 완료되었습니다!"
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.session_state.pending_approval = None
                st.rerun()
                
        if cB.button("❌ Reject"):
            st.session_state.messages.append({"role": "assistant", "content": "작성을 취소했습니다."})
            st.session_state.pending_approval = None
            st.rerun()
            
    elif prompt := st.chat_input("Ask a question or request knowledge ingestion..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            if any(keyword in prompt for keyword in ["추가", "작성", "넣어", "업데이트", "생성", "정리"]):
                raw_files = glob.glob(os.path.join(RAW_DIR, "*"))
                if not raw_files:
                    response = "`raw/` 폴더에 파일이 없습니다. 문서를 먼저 넣어주세요."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    target_file = None
                    for rf in raw_files:
                        base_name = os.path.basename(rf)
                        name_without_ext = os.path.splitext(base_name)[0]
                        if base_name.lower() in prompt.lower() or name_without_ext.lower() in prompt.lower():
                            target_file = rf
                            break
                    
                    if not target_file:
                        target_file = max(raw_files, key=os.path.getctime)
                        
                    with st.spinner(f"`{os.path.basename(target_file)}` 파일을 분석 중... (Gemini 호출)"):
                        if target_file.endswith(".pdf"):
                            try:
                                import pymupdf4llm
                                raw_text = pymupdf4llm.to_markdown(target_file)
                            except ImportError:
                                raw_text = "PDF 추출 라이브러리(pymupdf4llm)가 없습니다."
                        else:
                            with open(target_file, "r", encoding="utf-8") as f:
                                raw_text = f.read()
                                
                        plan = run_agent("wiki_planner", f"다음 텍스트를 위키로 만들기 위한 계획을 세워줘:\n\n{raw_text[:4000]}")
                        st.markdown("`Planner` 기획 완료. `Writer`가 위키용 마크다운을 작성 중입니다...")
                        final_md = run_agent("wiki_writer", f"계획: {plan}\n\n원본: {raw_text[:4000]}")
                        page_name = os.path.basename(target_file).split('.')[0]
                        
                        response = f"**[Draft Preview - 최종 문서 확인]**\n\n> **대상 문서:** `{page_name}`\n\n아래 내용이 위키에 최종적으로 기록됩니다.\n\n````markdown\n{final_md}\n````\n\n이 내용을 위키에 추가할까요?"
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        st.session_state.pending_approval = {
                            "final_md": final_md,
                            "page_name": page_name
                        }
                        st.rerun()
            else:
                with st.spinner("QA 에이전트가 위키를 검색하고 답변을 생성 중입니다..."):
                    wiki_context = ""
                    for root, dirs, files in os.walk(WIKI_DIR):
                        for file in files:
                            if file.endswith(".md") and ".tmp." not in file:
                                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                                    wiki_context += f"### {file}\n{f.read()}\n\n"
                    answer = run_agent("wiki_qa", f"지식 문서:\n{wiki_context[:8000]}\n\n질문: {prompt}")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
