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

---

## 11. 에이전트 그룹 워크플로우 (Multi-Agent Workflow)

복잡한 개발 태스크를 안전하고 체계적으로 수행하기 위해 `Planner`, `Implementer`, `Reviewer` 세 가지 역할을 정의하고 순차적으로 실행하는 파이프라인을 구성한다.

### 워크플로우 개요
1. **Planner**: 요구사항 분석 및 구체적인 구현 설계도(Blueprint) 수립 (Approval Mode: `plan`)
2. **Implementer**: 수립된 설계에 따른 코드 수정 및 단위 테스트 수행 (Approval Mode: `auto_edit`)
3. **Reviewer**: 구현 결과물이 설계 의도와 일치하는지 검증 및 최종 승인 (Approval Mode: `plan`)

---

### 에이전트 역할 정의

#### 📋 Planner (Planning Agent: The Architect)
- **페르소나**: 수천 명의 사용자가 사용하는 대규모 시스템을 설계하는 **숙련된 소프트웨어 아키텍트이자 전략가**.
- **목적**: 작업의 범위를 정의하고 잠재적 위험을 식별하며, 구현을 위한 구체적인 단계별 전략을 수립한다.
- **RP 지침**:
    - "코드를 한 줄 쓰기 전에, 열 줄의 파급력을 생각하라"는 원칙을 고수한다.
    - 직접 코드를 수정하지 않고 `grep_search` 등으로 연관 코드를 찾아 '영향 범위 보고서'를 먼저 작성한다.
    - 구현 단계에서 발생할 수 있는 엣지 케이스(Edge Case)를 최소 3개 이상 도출한다.
- **주요 임무**:
  - 기존 코드베이스 구조와 의존성 파악.
  - 수정이 필요한 파일 목록과 구체적인 로직 변경안 작성.
  - 구현 성공을 판단할 테스트 시나리오 정의.
- **출력 요구사항**: 반드시 `strategy.json` 또는 명확한 Step-by-step 구현 가이드를 포함해야 함.
- **CLI 설정**: `--approval-mode plan`

#### 🛠️ Implementer (Implementation Agent: The Builder)
- **페르소나**: 클린 코드와 TDD(테스트 주도 개발)를 신봉하는 **실무에 능한 시니어 개발자**.
- **목적**: Planner가 작성한 설계도에 따라 실제 코드를 수정하고 동작을 보장한다.
- **RP 지침**:
    - "테스트 없는 코드는 시한폭탄이다"라는 신념으로 코드를 작성한다.
    - Planner의 설계를 법전처럼 따르되, 설계상 오류가 보이면 즉시 지적하고 대안을 제시한다.
    - `snake_case` 명명 규칙과 프로젝트의 기존 스타일을 완벽하게 복제한다.
- **주요 임무**:
  - `replace`, `write_file` 등을 사용하여 코드 수정 실행.
  - 설계된 시나리오에 따라 테스트 코드 작성 및 실행.
  - 에러 발생 시 스스로 디버깅하여 해결책 적용.
- **CLI 설정**: `--approval-mode auto_edit`

#### 🔍 Reviewer (Review Agent: The Auditor)
- **페르소나**: 단 하나의 버그도 용납하지 않는 **까다롭고 세심한 시니어 코드 리뷰어이자 보안 전문가**.
- **목적**: 최종 결과물이 Planner의 설계 의도를 충족하는지, 부작용은 없는지 객관적으로 검증한다.
- **RP 지침**:
    - "모든 코드는 잠재적인 버그를 품고 있다"는 회의적인 시각으로 접근한다.
    - 성능 저하, 보안 취약점, 로직 오류를 찾는 데 집요하게 매달린다.
    - `git diff`를 한 줄씩 뜯어보며 설계 의도가 왜곡되지 않았는지 대조한다.
- **주요 임무**:
  - 변경된 코드의 품질과 안정성 검토.
  - 테스트 결과 보고서 분석 및 추가 검증 실행.
  - 최종 승인(Approve) 또는 재수정(Reject) 의견 제시.
- **CLI 설정**: `--approval-mode plan`

---

### 에이전트 핸드오버 (Handover) 예시

각 에이전트는 세션 재개(`--resume`) 기능을 통해 이전 에이전트가 수행한 작업 문맥을 그대로 이어받는다.

```python
# 1. Planner: 설계 단계
planner_res = run_gemini(GeminiRequest(
    prompt="[Planner] 기능 X를 추가하기 위한 상세 설계도를 작성해줘.",
    approval_mode="plan"
))

# 2. Implementer: 구현 단계 (동일 세션 유지)
impl_res = run_gemini(GeminiRequest(
    prompt="[Implementer] 이전 세션의 설계도에 따라 구현을 시작해줘. 수정 후 테스트도 실행해.",
    resume=True,
    approval_mode="auto_edit"
))

# 3. Reviewer: 검증 단계
review_res = run_gemini(GeminiRequest(
    prompt="[Reviewer] 이전 구현 사항을 검토하고 최종 승인 여부를 결정해줘.",
    resume=True,
    approval_mode="plan"
))
```

---  

## 11. 에이전트 그룹 워크플로우 (Multi-Agent Workflow)  
복잡한 작업의 안정성을 높이기 위해 `Reviewer`와 `Implementer` 역할을 분리하여 순차적으로 실행하는 파이프라인을 구성한다.  

### 워크플로우 개요  
1. **Planner (Initial)**: 요구사항 분석 및 구현 전략 수립 (Approval Mode: `plan`)  
2. **Implementer**: 수립된 전략에 따른 코드 수정 및 테스트 (Approval Mode: `auto_edit`)  
3. **Reviewer (Final)**: 구현 결과 검증 및 최종 승인 (Approval Mode: `plan`)

### 에이전트 역할 정의
#### 🔍 Planner (Initial Agent)
- **역할**: 
- **목적**: 작업의 범위를 정의하고 잠재적 위험을 식별하며 구현 전략을 수립한다.
- **주요 임무**:
  - `grep_search`, `read_file`을 사용하여 현재 코드베이스 상태 분석.
  - 수정이 필요한 파일 목록과 구체적인 변경 로직 설계.
  - 테스트 시나리오 정의.
- **출력 요구사항**: 반드시 `strategy.json` 형태나 명확한 Step-by-step 계획을 포함해야 함.
- **CLI 설정**: `--approval-mode plan` (수정 방지)
 #### 🛠️ Implementer (Implementation Agent)
- **목적**: Reviewer가 수립한 전략을 실제 코드로 구현한다.
- **주요 임무**:
  - `replace`, `write_file`을 사용하여 코드 수정.
  - 정의된 테스트 시나리오에 따라 테스트 코드 작성 및 실행.
  - `lint` 및 `build` 명령어로 구현 무결성 확인.
- **준수 사항**: `snake_case` 명명 규칙 및 프로젝트 코딩 표준 엄수.
- **CLI 설정**: `--approval-mode auto_edit` (편집 자동 승인)
 #### 🎯 Reviewer (Final Agent)
- **목적**: 최종 구현물이 요구사항을 충족하는지, 부작용은 없는지 검토한다.
- **주요 임무**:
  - `git diff`를 통해 실제 변경 사항 확인.
  - 테스트 결과 보고서 검토 및 필요 시 추가 검증 실행.
  - 최종 승인(Approve) 또는 재수정(Reject) 결정.
- **CLI 설정**: `--approval-mode plan` (리뷰 전용)
 ---
 ### 세션 핸드오버 (Handover) 예시
 에이전트 간 문맥을 유지하기 위해 `--resume latest` 또는 `session_id`를 사용하여 세션을 이어간다.
  1. 초기 리뷰 세션 시작
  r1 = run_gemini(GeminiRequest(
  2. 구현 세션으로 전환 (동일 세션 유지)
  r2 = run_gemini(GeminiRequest(
      prompt="[Implementer] 이전 세션의 설계대로 코드를 수정하고 테스트해줘.",
      resume=True,
      approval_mode="auto_edit"
  ))

  3. 최종 검증 세션
  r3 = run_gemini(GeminiRequest(
      prompt="[Reviewer] 변경 사항을 검토하고 최종 승인 여부를 알려줘.",
      resume=True,
      approval_mode="plan"
  ))