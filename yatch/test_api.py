import subprocess
import os
import json
from dataclasses import dataclass
from typing import Optional, Literal

# 1. 문서에 정의된 데이터 구조
OutputFormat = Literal["text", "json", "stream-json"]

@dataclass
class GeminiRequest:
    prompt: str
    cwd: Optional[str] = None
    output_format: OutputFormat = "text"
    approval_mode: Optional[str] = "yolo" # YOLO 모드: 모든 도구 승인 없이 실행
    timeout_sec: int = 30

@dataclass
class GeminiResult:
    ok: bool
    stdout: str
    stderr: str

# 2. 실행 로직 구현
def run_gemini(req: GeminiRequest) -> GeminiResult:
    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    cmd = [exe, "-p", req.prompt, "--approval-mode", req.approval_mode]
    
    if req.output_format != "text":
        cmd += ["-o", req.output_format]

    print(f"[실행 명령어]: {' '.join(cmd)}")
    
    completed = subprocess.run(
        cmd,
        cwd=req.cwd,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )

    return GeminiResult(
        ok=completed.returncode == 0,
        stdout=completed.stdout,
        stderr=completed.stderr
    )

# 3. 메인 실행 (입출력 테스트)
if __name__ == "__main__":
    request = GeminiRequest(prompt="안녕! 너의 서브프로세스 API가 잘 작동하는지 확인하기 위해 '성공'이라고 한 단어만 답해줘.")
    result = run_gemini(request)

    if result.ok:
        print("\n[Gemini 응답]:")
        print(result.stdout.strip())
    else:
        print("\n[오류 발생]:")
        print(result.stderr)
