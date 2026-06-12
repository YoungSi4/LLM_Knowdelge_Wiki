# Agents Subprocess Calling

CLI 도구를 프로그래밍 방식으로 호출하여 에이전틱 코딩 시스템을 구축하는 기술적 기반입니다.

## 1. CLI 호출 방식
CLI 도구(Gemini, Claude, Codex)를 파이썬 환경에서 제어하기 위한 두 가지 인터페이스:

1. **직접 실행 (Command-line Arguments)**: 명령 인자로 프롬프트를 전달 (Gemini 방식).
2. **표준 입력 (stdin Pipe)**: 프롬프트를 파이프를 통해 전달 (Claude/Codex 방식).

### 서브프로세스 호출 핵심 파라미터 (`subprocess.run`)
| 파라미터 | 역할 |
| :--- | :--- |
| `input` | 프로세스의 `stdin`으로 문자열 전달 |
| `capture_output` | `stdout`/`stderr` 캡처 |
| `text` | 입출력을 `bytes` 대신 `str`로 처리 (`encoding="utf-8"`) |
| `timeout` | 지정 시간 초과 시 `TimeoutExpired` 예외 발생 |

## 2. 세션 관리 및 영속성
에이전트와의 연속적인 작업(Multi-turn)을 위해 세션을 관리해야 합니다.

- **Claude**: `--resume <session-id>` 활용.
- **Codex**: `resume <session-id>` 활용.
- **Gemini**: `--resume <index>` 또는 세션 리스트 확인 후 호출.

> **주의**: `--ephemeral` 또는 `--no-session-persistence` 플래그는 세션 영속성을 제거하므로, 연속 작업 시 주의가 필요합니다.

## 3. 에이전틱 코딩 파이프라인 설계
단일 도구 활용을 넘어, 에이전트 간 협업을 위한 파이프라인 구축 시 고려 사항:
- **Local File 접근**: 에이전트가 로컬 파일에 접근하도록 구성하는 메커니즘 (로컬 컨텍스트 전달).
- **Session ID 관리**: 작업 단위별 세션 ID의 효율적 관리 및 복원.
- **에이전트별 특성 대응**: 각 CLI 도구의 하드코딩된 호출 방식 및 JSON 포맷 대응.

---
*Raw Source: 3. Agents subprocess calling.pdf*
