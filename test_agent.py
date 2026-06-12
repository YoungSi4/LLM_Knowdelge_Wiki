import os
import json
import subprocess
import uuid

def run_agent(agent_name, prompt):
    try:
        with open(f"harness/subagents/{agent_name}.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        return f"[ERROR] Agent config {agent_name} not found."
    
    system_prompt = config.get("system_prompt", "")
    full_prompt = f"SYSTEM: {system_prompt}\n\nUSER_REQUEST: {prompt}"
    
    session_id = str(uuid.uuid4())
    cmd = ["gemini.cmd", "--session-id", session_id, "--approval-mode", "yolo", "--skip-trust", "-m", "gemini-3.1-flash-lite", "-o", "json", "-p", full_prompt]
    print(f"Running cmd: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    
    print(f"Return code: {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
    
    if result.returncode != 0:
        return f"[ERROR] {result.stderr}"
    
    try:
        data = json.loads(result.stdout)
        return data.get("response") or data.get("result") or "[ERROR] No response field"
    except Exception as e:
        return f"[ERROR] JSON parse failed: {str(e)}\nRaw output: {result.stdout}"

if __name__ == "__main__":
    with open("raw/dod_basics.md", "r", encoding="utf-8") as f:
        raw_text = f.read()
    print("=== PLANNER ===")
    plan = run_agent("wiki_planner", f"다음 텍스트를 위키로 만들기 위한 계획을 세워줘:\n\n{raw_text[:4000]}")
    print("\n=== WRITER ===")
    final_md = run_agent("wiki_writer", f"계획: {plan}\n\n원본: {raw_text[:4000]}")
    print("\n=== FINAL OUTPUT ===")
    print(final_md)
