# Claude CLI Subprocess API

Claude Code CLI를 subprocess로 호출하기 위한 API 레퍼런스.

---

## 1. 데이터 구조

```python
from dataclasses import dataclass, field
from typing import Literal, Optional

OutputFormat = Literal["text", "json", "stream-json"]

@dataclass
class ClaudeRequest:
    prompt: str
    cwd: Optional[str] = None
    output_format: OutputFormat = "text"
    session_id: Optional[str] = None          # 특정 세션 재개용
    resume: bool = False                       # True면 최근 세션 재개 (-c)
    no_session_persistence: bool = False       # 세션 파일 미저장
    permission_mode: Optional[str] = None      # "plan" | "auto" | "acceptEdits" | "dontAsk" | "bypassPermissions"
    dangerously_skip_permissions: bool = False
    model: Optional[str] = None
    max_budget_usd: Optional[float] = None
    json_schema: Optional[dict] = None
    system_prompt: Optional[str] = None
    append_system_prompt: Optional[str] = None
    allowed_tools: Optional[list[str]] = None
    disallowed_tools: Optional[list[str]] = None
    add_dirs: list[str] = field(default_factory=list)
    mcp_config: Optional[str] = None
    input_format: Optional[str] = None         # "stream-json" 양방향 스트리밍용
    include_partial_messages: bool = False
    worktree: bool = False                     # git worktree 격리
    fork_session: bool = False                 # 세션 분기
    timeout_sec: int = 120


@dataclass
class ClaudeResult:
    ok: bool
    returncode: int
    stdout: str
    stderr: str
    session_id: Optional[str] = None
    error: Optional[str] = None
```

---

## 2. 출력 형식

| 플래그 | 동작 |
|--------|------|
| `--output-format text` | 기본. 사람이 읽을 수 있는 텍스트 출력 |
| `--output-format json` | 완료 후 단일 JSON 객체 반환 |
| `--output-format stream-json` | 실시간 JSONL 스트림 (줄 단위 JSON) |

### stream-json 프로토콜

stdout에 한 줄씩 JSON 객체가 출력된다.

```jsonl
{"type":"system","subtype":"init","session_id":"uuid-...","tools":[...]}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"..."}]}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"...","name":"Read","input":{...}}]}}
{"type":"result","subtype":"success","session_id":"uuid-...","cost_usd":0.03,"duration_ms":4200,"num_turns":2}
```

**양방향 스트리밍** — `--input-format stream-json`을 함께 사용하면 stdin으로 JSON을 보낼 수 있다:

```jsonl
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"추가 지시"}]}}
```

부분 메시지 청크를 받으려면 `--include-partial-messages`를 추가한다.

---

## 3. 세션 관리

| 동작 | 명령 |
|------|------|
| 1회성 실행 | `claude -p "..."` |
| 세션 미저장 | `claude --no-session-persistence -p "..."` |
| 최근 세션 재개 | `claude -c -p "..."` |
| 특정 세션 재개 | `claude -r <session_id> -p "..."` |
| 세션 분기 (원본 보존) | `claude -r <session_id> --fork-session -p "..."` |
| 새 세션에 UUID 지정 | `claude --session-id <uuid> -p "..."` |
| git worktree 격리 | `claude -w -p "..."` |
| 세션 이름 지정 | `claude -n "my-task" -p "..."` |

> `--session-id`는 **새 세션에 특정 UUID를 부여**하는 용도이며, 재개용이 아니다.
> 재개는 반드시 `-c` (최근) 또는 `-r <session_id>` (특정)을 사용한다.

---

## 4. 권한 모드

| 모드 | 플래그 | 용도 |
|------|--------|------|
| plan (읽기 전용) | `--permission-mode plan` | 코드 분석, 설명, 리뷰 |
| acceptEdits | `--permission-mode acceptEdits` | 편집 자동 승인, Bash는 확인 |
| auto | `--permission-mode auto` | 대부분의 작업 자동 승인 |
| dontAsk | `--permission-mode dontAsk` | 모든 도구 자동 실행 |
| bypassPermissions | `--permission-mode bypassPermissions` | 전체 권한 우회 |
| 위험 모드 | `--dangerously-skip-permissions` | 모든 권한 검사 생략. 외부 샌드박스 환경 전용 |

---

## 5. CLI 플래그 레퍼런스

| 기능 | 플래그 |
|------|--------|
| 비대화 실행 | `-p "<prompt>"` |
| 출력 형식 | `--output-format {text,json,stream-json}` |
| 입력 스트리밍 | `--input-format stream-json` |
| 부분 메시지 | `--include-partial-messages` |
| 세션 미저장 | `--no-session-persistence` |
| 최근 세션 재개 | `-c` |
| 특정 세션 재개 | `-r <session_id>` |
| 세션 분기 | `--fork-session` (+ `-r`) |
| 세션 이름 | `-n <name>` |
| 새 세션 UUID | `--session-id <uuid>` |
| 모델 지정 | `--model <model>` |
| 비용 상한 | `--max-budget-usd <N>` |
| 권한 모드 | `--permission-mode {plan,acceptEdits,auto,dontAsk,bypassPermissions}` |
| 전체 권한 우회 | `--dangerously-skip-permissions` |
| JSON Schema | `--json-schema '<json>'` |
| 시스템 프롬프트 (대체) | `--system-prompt "..."` |
| 시스템 프롬프트 (추가) | `--append-system-prompt "..."` |
| 허용 도구 | `--allowedTools "Bash(git:*) Edit Read"` |
| 차단 도구 | `--disallowedTools "Bash(rm:*)"` |
| 추가 디렉터리 | `--add-dir <path>` |
| MCP 서버 설정 | `--mcp-config <file>` |
| Git worktree 격리 | `-w` / `--worktree` |
| 디버그 | `-d` / `--debug` |
| 설정 파일 | `--settings <file-or-json>` |
| 에이전트 | `--agent <name>` / `--agents '<json>'` |
| 폴백 모델 | `--fallback-model <model>` |
| Bare 모드 | `--bare` (hooks, LSP, 플러그인 등 전부 생략) |
| 도구 목록 제한 | `--tools "Bash,Edit,Read"` |

---

## 6. 구현: build_command()

```python
import json


def build_claude_command(req: ClaudeRequest) -> list[str]:
    cmd = ["claude"]

    # 세션
    if req.session_id:
        cmd += ["-r", req.session_id]
        if req.fork_session:
            cmd.append("--fork-session")
    elif req.resume:
        cmd.append("-c")

    if req.no_session_persistence:
        cmd.append("--no-session-persistence")

    # 권한
    if req.dangerously_skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    elif req.permission_mode:
        cmd += ["--permission-mode", req.permission_mode]

    # 출력
    if req.output_format != "text":
        cmd += ["--output-format", req.output_format]

    if req.input_format:
        cmd += ["--input-format", req.input_format]

    if req.include_partial_messages:
        cmd.append("--include-partial-messages")

    # 모델 / 비용
    if req.model:
        cmd += ["--model", req.model]

    if req.max_budget_usd is not None:
        cmd += ["--max-budget-usd", str(req.max_budget_usd)]

    # 구조화 출력
    if req.json_schema:
        cmd += ["--json-schema", json.dumps(req.json_schema)]

    # 시스템 프롬프트
    if req.system_prompt:
        cmd += ["--system-prompt", req.system_prompt]

    if req.append_system_prompt:
        cmd += ["--append-system-prompt", req.append_system_prompt]

    # 도구 필터
    if req.allowed_tools:
        cmd += ["--allowedTools"] + req.allowed_tools

    if req.disallowed_tools:
        cmd += ["--disallowedTools"] + req.disallowed_tools

    # MCP
    if req.mcp_config:
        cmd += ["--mcp-config", req.mcp_config]

    # 추가 디렉터리
    for d in req.add_dirs:
        cmd += ["--add-dir", d]

    # worktree
    if req.worktree:
        cmd.append("-w")

    # 프롬프트
    cmd += ["-p", req.prompt]

    return cmd
```

---

## 7. 구현: run_claude() — 동기 실행

```python
import subprocess


def run_claude(req: ClaudeRequest) -> ClaudeResult:
    cmd = build_claude_command(req)

    try:
        completed = subprocess.run(
            cmd,
            cwd=req.cwd,
            text=True,
            capture_output=True,
            timeout=req.timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        return ClaudeResult(
            ok=False, returncode=-1,
            stdout=e.stdout or "", stderr=e.stderr or "",
            error=f"Timeout after {req.timeout_sec}s",
        )

    return ClaudeResult(
        ok=completed.returncode == 0,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        error=None if completed.returncode == 0 else f"Exit code {completed.returncode}",
    )
```

---

## 8. 구현: run_claude_streaming() — JSONL 스트리밍

```python
import subprocess
import json
from collections.abc import Generator


def run_claude_streaming(req: ClaudeRequest) -> Generator[dict, None, ClaudeResult]:
    req.output_format = "stream-json"
    cmd = build_claude_command(req)

    proc = subprocess.Popen(
        cmd, cwd=req.cwd,
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
        return ClaudeResult(
            ok=False, returncode=-1,
            stdout="\n".join(collected),
            stderr=proc.stderr.read() if proc.stderr else "",
            error=f"Timeout after {req.timeout_sec}s",
        )

    stderr = proc.stderr.read() if proc.stderr else ""
    return ClaudeResult(
        ok=proc.returncode == 0,
        returncode=proc.returncode or 0,
        stdout="\n".join(collected), stderr=stderr,
        error=None if proc.returncode == 0 else f"Exit code {proc.returncode}",
    )
```

---

## 9. 구현: 양방향 스트리밍

```python
import subprocess
import json
import threading
from queue import Queue


class ClaudeSession:
    """Claude와의 양방향 스트리밍 세션."""

    def __init__(self, req: ClaudeRequest):
        req.output_format = "stream-json"
        req.input_format = "stream-json"
        req.include_partial_messages = True
        cmd = build_claude_command(req)

        self.proc = subprocess.Popen(
            cmd, cwd=req.cwd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )
        self.events: Queue[dict] = Queue()
        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()

    def _read(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                self.events.put(json.loads(line))
            except json.JSONDecodeError:
                self.events.put({"type": "raw", "content": line})
        self.events.put({"type": "eof"})

    def send(self, text: str):
        msg = json.dumps({
            "type": "user",
            "message": {"role": "user", "content": [{"type": "text", "text": text}]},
        })
        self.proc.stdin.write(msg + "\n")
        self.proc.stdin.flush()

    def recv(self, timeout: float = 30.0) -> dict | None:
        try:
            return self.events.get(timeout=timeout)
        except Exception:
            return None

    def close(self):
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait(timeout=10)
```

---

## 10. 사용 예시

### 코드 분석 (JSON 출력)

```python
result = run_claude(ClaudeRequest(
    prompt="main.py의 보안 취약점을 분석해줘",
    output_format="json",
    permission_mode="plan",
    cwd="/workspace/project",
))
analysis = json.loads(result.stdout)
```

### 구조화 출력으로 코드 리뷰

```python
result = run_claude(ClaudeRequest(
    prompt="이 PR의 변경사항을 리뷰해줘",
    output_format="json",
    json_schema={
        "type": "object",
        "properties": {
            "issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["critical", "warning", "info"]},
                        "file": {"type": "string"},
                        "message": {"type": "string"},
                    },
                    "required": ["severity", "file", "message"],
                },
            },
            "approved": {"type": "boolean"},
        },
        "required": ["issues", "approved"],
    },
    cwd="/workspace/project",
))
review = json.loads(result.stdout)
```

### 실시간 스트리밍

```python
req = ClaudeRequest(
    prompt="이 프로젝트를 리팩터링해줘",
    permission_mode="auto",
    cwd="/workspace/project",
)
for event in run_claude_streaming(req):
    if event.get("type") == "assistant":
        for block in event["message"]["content"]:
            if block["type"] == "text":
                print(block["text"], end="", flush=True)
    elif event.get("type") == "result":
        print(f"\n[비용: ${event.get('cost_usd', 0):.4f}]")
```

### 멀티턴 세션 재개

```python
# 첫 턴
r1 = run_claude(ClaudeRequest(
    prompt="test_auth.py의 실패 원인을 분석해줘",
    permission_mode="plan",
    cwd="/workspace/project",
))

# 두 번째 턴 — 이전 세션 이어가기
r2 = run_claude(ClaudeRequest(
    prompt="분석한 원인을 바탕으로 수정해줘",
    resume=True,
    permission_mode="auto",
    cwd="/workspace/project",
))
```

### 양방향 스트리밍

```python
session = ClaudeSession(ClaudeRequest(
    prompt="이 프로젝트의 아키텍처를 설명해줘",
    permission_mode="plan",
    cwd="/workspace/project",
))

while True:
    event = session.recv(timeout=30)
    if event is None or event.get("type") == "result":
        break
    if event.get("type") == "assistant":
        print(event["message"]["content"])

session.send("테스트 커버리지는 어떤가?")

while True:
    event = session.recv(timeout=30)
    if event is None or event.get("type") == "result":
        break
    if event.get("type") == "assistant":
        print(event["message"]["content"])

session.close()
```

### 시스템 프롬프트 + 비용 제한

```python
result = run_claude(ClaudeRequest(
    prompt="이 코드베이스의 아키텍처 문서를 작성해줘",
    system_prompt="당신은 시니어 소프트웨어 아키텍트입니다. 간결하고 정확하게 답변하세요.",
    model="opus",
    max_budget_usd=1.00,
    permission_mode="plan",
    cwd="/workspace/project",
))
```

### 격리된 작업 (git worktree)

```python
result = run_claude(ClaudeRequest(
    prompt="실험적으로 이 모듈을 TypeScript로 마이그레이션해줘",
    worktree=True,
    permission_mode="auto",
    cwd="/workspace/project",
))
```
