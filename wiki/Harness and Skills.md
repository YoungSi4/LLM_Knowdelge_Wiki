# Harness and Skills

## 개요
에이전트가 복잡한 작업을 안전하고 효율적으로 완수할 수 있도록 실행 환경, 도구, 데이터 검증 파이프라인, 안전장치를 구조적으로 설계하고 통제하는 **Harness Engineering**과 에이전트의 능력을 확장하는 **Skill**에 대해 다룹니다.

## 하네스 엔지니어링 (Harness Engineering)
에이전트가 작업을 안정적으로 수행하도록 만드는 실행 구조입니다. 단순히 프롬프트를 잘 쓰는 것을 넘어 목표, 절차, 기록, 선호를 분리하여 관리합니다.

### 1. 하네스의 4대 책임 요소
| 책임 | 질문 | 파일 예시 |
| :--- | :--- | :--- |
| **Contract (계약)** | 무엇이 끝났는가? | `TASK.md` |
| **Procedure (절차)** | 어떻게 진행하는가? | `SKILL.md` (Skills) |
| **Journal (기록)** | 지금까지 무엇을 했는가? | `journal.md`, `MEMORY.md` |
| **Preference (선호)** | 어떤 방식으로 일하는가? | `AGENTS.md`, `GEMINI.md` |

### 2. Contract-Driven Iteration
에이전트가 명시적인 달성 조건(`Done when`)을 만족할 때까지 반복적으로 작업을 수행하는 방식입니다.
- **Workflow**: `TASK.md` 읽기 → 상태 확인 → 최소 변경 구현 → 검증(Test/Lint) → Journal 기록 → 반복 또는 종료.
- **성공 조건**: Goal은 한 문장으로, `Done when`은 측정 가능한 수치나 명령어로 정의해야 함.

## 에이전트 스킬 (Agent Skills)
- **정의**: 에이전트가 특정 작업을 어떻게 수행할지 정의한 마크다운 파일과 보조 도구들의 묶음.
- **특징**: 에이전트는 현재 작업 맥락에 맞는 스킬을 자동으로 찾아 적용할 수 있음.

## 에이전틱 코딩 패턴 (Agentic Coding Patterns)
| 패턴 | 핵심 개념 | 활용 사례 |
| :--- | :--- | :--- |
| **Prompt Chaining** | 단계 간 의존성 연결 | 스펙 작성 → 테스트 작성 → 구현 |
| **Parallelization** | 독립 작업 동시 실행 | 여러 파일의 동시 수정 |
| **Orchestrator-Workers** | 중앙 관리 및 작업 분배 | 대규모 프로젝트의 파일별 할당 |
| **Evaluator-Optimizer** | 루프를 통한 품질 개선 | 테스트 통과할 때까지 구현 반복 |
| **EPCC** | Explore-Plan-Code-Commit | 바로 코딩하지 않고 분석 후 수행 |

## 주의사항 및 실패 사례
- **모호한 Done when**: 에이전트가 자기 판단으로 작업을 완료함 (명령어 검증 필수).
- **Plan 없는 Code**: 엉뚱한 파일을 수정할 위험이 큼.
- **Contract 수정**: 기준을 낮춰 완료한 척하는 행위 방지 필요.

## 관련 용어 및 참조
- [[Contract]]
- [[Skill]]
- [[Journal]]
- [[EPCC Pattern]]
- [[TDD]]

---
**Source**: `raw/7. Harness and Skills.pdf`
**Compiled by**: Knowledge Architect (LLM)
**Date**: 2026-05-20
