import os
import subprocess
import uuid
import json

isolated_dir = "C:\\temp\\isolated"
os.makedirs(isolated_dir, exist_ok=True)

full_prompt = "Hello, what do you know about Vibe Coding?"
session_id = str(uuid.uuid4())
cmd = ["gemini.cmd", "--session-id", session_id, "--approval-mode", "yolo", "--skip-trust", "-m", "gemini-3.1-flash-lite", "-o", "json", "-p", full_prompt]

result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL, cwd=isolated_dir)
print(result.stdout)
