import os
import subprocess
import json
import sys
import time

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open("wiki_build.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def run_agent(agent_name, prompt):
    """Gemini CLI를 사용하여 에이전트 실행 (YOLO 모드)"""
    with open(f"pool/{agent_name}.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    system_prompt = config["system_prompt"]
    full_prompt = f"SYSTEM: {system_prompt}\n\nUSER_REQUEST: {prompt}"
    
    # Gemini CLI 호출 (Flash Lite 모델 사용)
    cmd = ["gemini.cmd", "--approval-mode", "yolo", "--skip-trust", "-m", "gemini-3.1-flash-lite", "-o", "json", "-p", full_prompt]
    
    # stdin=subprocess.DEVNULL을 사용하여 입력을 기다리지 않도록 합니다.
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        err_msg = f"[ERROR_SIGNAL] Agent {agent_name} failed. Reason: {result.stderr.strip()}"
        print(err_msg)
        log(err_msg)
        return None
    
    try:
        response_data = json.loads(result.stdout)
        # Gemini CLI의 응답 필드 확인 (response 또는 result)
        content = response_data.get("response") or response_data.get("result")
        if content:
            return content
        else:
            err_msg = f"[ERROR_SIGNAL] No content found in agent {agent_name} response."
            print(err_msg)
            log(err_msg)
            return None
    except json.JSONDecodeError as e:
        err_msg = f"[ERROR_SIGNAL] Failed to parse JSON from agent {agent_name}. Reason: {str(e)}"
        print(err_msg)
        log(err_msg)
        return None

def build_wiki_pipeline(pdf_path):
    file_name = os.path.basename(pdf_path)
    base_name = os.path.splitext(file_name)[0]
    raw_md_path = f"wiki/{base_name}.raw.md"
    
    log(f"Starting pipeline for: {file_name}")
    
    # 1. Ingest
    log("Step 1: Ingesting PDF...")
    subprocess.run(["python", "ingest_pdf.py", pdf_path, raw_md_path])
    
    with open(raw_md_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
    
    # 2. Architect (Planner)
    log("Step 2: Planning wiki structure...")
    plan = run_agent("wiki_planner", f"다음 텍스트를 위키로 만들기 위한 계획을 세워줘:\n\n{raw_content[:4000]}")
    if not plan: return
    
    # 3. Compile (Writer)
    log("Step 3: Compiling wiki content...")
    final_md = run_agent("wiki_writer", f"계획: {plan}\n\n원본 내용: {raw_content[:4000]}")
    if not final_md: 
        print(f"[ERROR_SIGNAL] Pipeline aborted at Step 3 due to Writer Agent failure.")
        return
    
    # 4. Save (Atomic Write)
    output_path = f"wiki/{base_name}.md"
    tmp_path = f"wiki/{base_name}.tmp.md"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(final_md)
        os.replace(tmp_path, output_path)
        log(f"Step 4: Wiki page successfully committed at {output_path}")
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        err_msg = f"[ERROR_SIGNAL] Atomic write failed for {output_path}. Rolled back. Reason: {str(e)}"
        print(err_msg)
        log(err_msg)
        return
    
    # 5. Clean up
    os.remove(raw_md_path)
    
    # 6. Update Index (간단한 구현)
    log("Step 5: Updating INDEX.md...")
    update_index(base_name)

def update_index(new_page_title):
    index_path = "wiki/INDEX.md"
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if f"[[{new_page_title}]]" not in content:
        # 최근 업데이트 섹션에 추가
        new_entry = f"- [[{new_page_title}]] ({time.strftime('%Y-%m-%d')})"
        content = content.replace("## 최근 업데이트", f"## 최근 업데이트\n{new_entry}")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wiki_orchestrator.py <pdf_path>")
        sys.exit(1)
    
    build_wiki_pipeline(sys.argv[1])
