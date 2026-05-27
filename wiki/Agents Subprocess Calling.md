# Agents Subprocess Calling

[[Agentic Coding]] 환경에서의 서브프로세스 기반 에이전트 실행 정책 및 제어 기술을 기술한다.

## 1. 실행 방식 및 파라미터 구조
| 구분 | 전달 방식 | 파이프라인 요소 |
| :--- | :--- | :--- |
| **명령어 전달** | Args/CLI | `-p <prompt>` |
| **데이터 파이프** | `stdin` | `subprocess.run(..., input=prompt)` |
| **결과 수신** | `stdout` | JSON 기반 자동 파싱 (예: `--format json`) |

## 2. YOLO Mode (무제한 권한) 실행 정책
| 도구 | 플래그 (Flag) | 위험성 및 권고 |
| :--- | :--- | :--- |
| **Claude** | `--dangerously-skip-permissions` | 실시간 검증 필수 |
| **Gemini** | `--yolo` | 스테이징 환경에서만 권장 |
| **Codex** | `--dangerously-bypass-approvals` | 샌드박스 제약 해제 시 주의 |

## 3. 세션 영속성 관리
* **재개 (Resume)**: `--resume <session-id>`를 통한 Context 유지.
* **휘발성 (Ephemeral)**: 테스트 목적으로 `--no-session` 또는 `--ephemeral` 사용.
* **상태 확인**: `returncode == 0` 여부 및 JSON 응답 구조의 `status` 필드 검증.

## 4. 참조 링크
* [[Agentic Coding]]
* [[Agent Pool and Orchestrator]]

---
**Source**: `raw/3. Agents subprocess calling.pdf`
**Compiled by**: Knowledge Architect
**Date**: 2026-05-20

