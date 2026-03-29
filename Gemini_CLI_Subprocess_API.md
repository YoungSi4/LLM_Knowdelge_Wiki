# Gemini CLI Subprocess API

Gemini CLI를 subprocess로 호출하기 위한 API 레퍼런스.

---

## 1. 데이터 구조

```python
from dataclasses import dataclass, field
from typing import Literal, Optional

OutputFormat = Literal["text", "json", "stream-json"]

@dataclass
class GeminiRequest:
    prompt: str
    cwd: Optional[str] = None
    output_format: OutputFormat = "text"
    session_id: Optional[str] = None           # 특정 세션 재개용 (ID 또는 인덱스)
    resume: bool = False                        # True면 최근 세션 재개 (latest)
    approval_mode: Optional[str] = "default"    # "plan" | "auto_edit" | "yolo" | "default"
    sandbox: bool = False                       # --sandbox 격리 모드 활성화
    policy: Optional[str] = None                # --policy 정책 파일 경로
    model: Optional[str] = None                 # auto, pro, flash, flash-lite 등
    system_prompt: Optional[str] = None         # 환경변수 GEMINI_SYSTEM_MD로 주입
    include_directories: list[str] = field(default_factory=list)
    raw_output: bool = False                    # ANSI 이스케이프 허용
    timeout_sec: int = 120


@dataclass
class GeminiResult:
    ok: bool
    returncode: int                            # 0:성공, 1:오류, 42:입력오류, 53:턴제한초과
    stdout: str
    stderr: str
    session_id: Optional[str] = None
    error: Optional[str] = None
```

---

## 2. 출력 형식

| 플래그 | 동작 |
|--------|------|
| `-o text` | 기본. 사람이 읽을 수 있는 텍스트 출력 |
| `-o json` | 완료 후 단일 JSON 객체 반환 |
| `-o stream-json` | 실시간 JSONL 스트림 (줄 단위 JSON) |

### stream-json 프로토콜

stdout에 한 줄씩 JSON 객체가 출력된다.

```jsonl
{"type":"init","session_id":"...","model":"gemini-2.0-pro"}
{"type":"message","content":"분석 결과..."}
{"type":"tool_use","tool_name":"read_file","tool_id":"tc_001","parameters":{"path":"main.py"}}
{"type":"tool_result","tool_id":"tc_001","status":"success","output":"..."}
{"type":"message","content":"결론입니다."}
{"type":"result","status":"success","stats":{"input_tokens":500,"output_tokens":120}}
```

---

## 3. 세션 관리

| 동작 | 명령 |
|------|------|
| 1회성 실행 | `gemini -p "..."` (세션은 자동 저장됨) |
| 최근 세션 재개 | `gemini --resume latest -p "..."` |
| 특정 세션 재개 | `gemini --resume <session_id> -p "..."` |
| 세션 목록 확인 | `gemini --list-sessions` |
| 특정 세션 삭제 | `gemini --delete-session <index>` |
| 대화형 모드 진입 | `gemini -i -p "..."` |

---

## 4. 권한 모드

| 모드 | 플래그 | 용도 |
|------|--------|------|
| plan (읽기 전용) | `--approval-mode plan` | 코드 분석, 설명, 리뷰 (모든 도구 승인 대기) |
| auto_edit | `--approval-mode auto_edit` | 파일 편집 도구만 자동 승인 |
| yolo (전체 자동) | `--approval-mode yolo` | 모든 도구 호출 자동 승인. 외부 샌드박스 환경 전용 |
| default | `--approval-mode default` | 기본 승인 정책 (위험한 작업 시 확인) |

> `--yolo` / `-y`는 `--approval-mode yolo`와 동일하게 동작하는 단축 플래그로, 둘 다 현역이다.

---

## 5. CLI 플래그 레퍼런스

| 기능 | 플래그 |
|------|--------|
| 비대화 실행 | `-p "<prompt>"` |
| 출력 형식 | `-o {text,json,stream-json}` |
| 최근 세션 재개 | `--resume latest` |
| 특정 세션 재개 | `--resume <id>` |
| 세션 목록 | `--list-sessions` |
| 세션 삭제 | `--delete-session <index>` |
| 모델 지정 | `-m <model>` / `--model <model>` |
| 샌드박스 활성화 | `-s` / `--sandbox` |
| 정책 파일 | `--policy <file>` |
| 권한 모드 | `--approval-mode {plan,auto_edit,yolo,default}` |
| JSON Schema | *(미지원 — 프롬프트 내 지시로 대체)* |
| 시스템 프롬프트 | *(환경변수 GEMINI_SYSTEM_MD 사용)* |
| 추가 디렉터리 | `--include-directories <path>` |
| 원본 출력 | `--raw-output` |
| 디버그 | `-d` / `--debug` |
| 버전 확인 | `--version` |

---

## 6. 구현: build_command()

```python
import json
import os


def build_gemini_command(req: GeminiRequest) -> list[str]:
    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    cmd = [exe]

    # 세션
    if req.session_id:
        cmd += ["--resume", str(req.session_id)]
    elif req.resume:
        cmd += ["--resume", "latest"]

    # 권한 / 샌드박스
    if req.approval_mode:
        cmd += ["--approval-mode", req.approval_mode]
    
    if req.sandbox:
        cmd.append("--sandbox")
    
    if req.policy:
        cmd += ["--policy", req.policy]

    # 출력
    if req.output_format != "text":
        cmd += ["-o", req.output_format]
    
    if req.raw_output:
        cmd.append("--raw-output")

    # 모델
    if req.model:
        cmd += ["-m", req.model]

    # 추가 디렉터리
    for d in req.include_directories:
        cmd += ["--include-directories", d]

    # 프롬프트
    cmd += ["-p", req.prompt]

    return cmd
```

---

## 7. 구현: run_gemini() — 동기 실행

```python
import subprocess
import os
import tempfile


def run_gemini(req: GeminiRequest) -> GeminiResult:
    env = os.environ.copy()
    tmp_sys_path = None

    # 시스템 프롬프트 주입
    if req.system_prompt:
        fd, tmp_sys_path = tempfile.mkstemp(suffix=".md", prefix="gemini_sys_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(req.system_prompt)
        env["GEMINI_SYSTEM_MD"] = tmp_sys_path

    cmd = build_gemini_command(req)

    try:
        completed = subprocess.run(
            cmd,
            cwd=req.cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=req.timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        return GeminiResult(
            ok=False, returncode=-1,
            stdout=e.stdout or "", stderr=e.stderr or "",
            error=f"Timeout after {req.timeout_sec}s",
        )
    finally:
        if tmp_sys_path and os.path.exists(tmp_sys_path):
            os.unlink(tmp_sys_path)

    return GeminiResult(
        ok=completed.returncode == 0,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        error=None if completed.returncode == 0 else f"Exit code {completed.returncode}",
    )
```

---

## 8. 구현: run_gemini_streaming() — JSONL 스트리밍

```python
import subprocess
import json
from collections.abc import Generator


def run_gemini_streaming(req: GeminiRequest) -> Generator[dict, None, GeminiResult]:
    req.output_format = "stream-json"
    cmd = build_gemini_command(req)

    env = os.environ.copy()
    tmp_sys_path = None
    if req.system_prompt:
        fd, tmp_sys_path = tempfile.mkstemp(suffix=".md", prefix="gemini_sys_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(req.system_prompt)
        env["GEMINI_SYSTEM_MD"] = tmp_sys_path

    proc = subprocess.Popen(
        cmd, cwd=req.cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
    )

    collected = []
    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            collected.append(line)
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                yield {"type": "raw", "content": line}

        proc.wait(timeout=req.timeout_sec)
    except subprocess.TimeoutExpired:
        proc.kill()
        return GeminiResult(
            ok=False, returncode=-1,
            stdout="\n".join(collected),
            stderr=proc.stderr.read() if proc.stderr else "",
            error=f"Timeout after {req.timeout_sec}s",
        )

    stderr = proc.stderr.read() if proc.stderr else ""

    if tmp_sys_path and os.path.exists(tmp_sys_path):
        os.unlink(tmp_sys_path)

    return GeminiResult(
        ok=proc.returncode == 0,
        returncode=proc.returncode or 0,
        stdout="\n".join(collected), stderr=stderr,
        error=None if proc.returncode == 0 else f"Exit code {proc.returncode}",
    )
```

---

## 9. 구현: 양방향 스트리밍

*(현재 Gemini CLI는 대화형 REPL 외에 subprocess를 통한 실시간 양방향 JSONL 스트리밍 세션을 공식적으로 지원하지 않습니다. 필요 시 세션 재개(`--resume`)를 통한 반복 호출 방식을 권장합니다.)*

---

## 10. 사용 예시

### 코드 분석 (JSON 출력)

```python
result = run_gemini(GeminiRequest(
    prompt="main.py의 보안 취약점을 분석해줘",
    output_format="json",
    approval_mode="plan",
    cwd="/workspace/project",
))
analysis = json.loads(result.stdout)
```

### 구조화 출력 (프롬프트 내 지시)

Gemini CLI는 `--json-schema` 플래그를 지원하지 않는다.
JSON 형식 응답이 필요하면 프롬프트에 스키마를 직접 명시하고 `-o json`으로 출력한다.

```python
result = run_gemini(GeminiRequest(
    prompt="""이 PR의 변경사항을 리뷰해줘.

반드시 아래 JSON 형식으로만 응답해:
{"issues": [{"severity": "critical|warning|info", "file": "파일명", "message": "설명"}], "approved": true/false}""",
    output_format="json",
    approval_mode="plan",
    cwd="/workspace/project",
))
review = json.loads(result.stdout)
```

### 실시간 스트리밍

```python
req = GeminiRequest(
    prompt="이 프로젝트를 리팩터링해줘",
    approval_mode="auto_edit",
    cwd="/workspace/project",
)
for event in run_gemini_streaming(req):
    if event.get("type") == "message":
        print(event["content"], end="", flush=True)
    elif event.get("type") == "tool_use":
        print(f"\n[도구 호출: {event['tool_name']}]")
    elif event.get("type") == "result":
        stats = event.get("stats", {})
        print(f"\n[토큰: {stats.get('input_tokens')}in/{stats.get('output_tokens')}out]")
```

### 멀티턴 세션 재개

```python
# 첫 턴
r1 = run_gemini(GeminiRequest(
    prompt="test_auth.py의 실패 원인을 분석해줘",
    approval_mode="plan",
    cwd="/workspace/project",
))

# 두 번째 턴 — 최근 세션 이어가기
r2 = run_gemini(GeminiRequest(
    prompt="분석한 원인을 바탕으로 수정해줘",
    resume=True,
    approval_mode="auto_edit",
    cwd="/workspace/project",
))
```

### 시스템 프롬프트 + 샌드박스

```python
result = run_gemini(GeminiRequest(
    prompt="이 코드베이스의 아키텍처 문서를 작성해줘",
    system_prompt="당신은 시니어 소프트웨어 아키텍트입니다. 간결하고 정확하게 답변하세요.",
    model="gemini-2.0-pro",
    sandbox=True,
    approval_mode="plan",
    cwd="/workspace/project",
))
```
