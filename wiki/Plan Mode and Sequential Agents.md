# Plan Mode and Sequential Agents

## 개요
에이전트가 코드를 직접 수정하기 전에 실행 계획을 세우고 사용자의 승인을 받는 **Plan Mode**의 개념과, 이를 활용한 **Sequential Agent** 파이프라인 설계 방법을 다룹니다.

## 핵심 개념

### 1. Plan Mode
- **정의**: 에이전트가 실제 구현(Write/Modify/Delete)에 들어가기 전, **읽기 전용(Read-only)** 권한으로 시스템을 분석하고 계획을 수립하는 단계.
- **주요 특징**:
    - 파일 읽기, 검색, 웹 조회 등 분석 도구만 활성화.
    - 파일 수정 및 쉘 명령 실행 차단.
    - 산출물은 주로 마크다운 형태의 계획서로 저장됨.
- **장점**: 토큰 낭비 방지 및 잘못된 자동화로 인한 시스템 파손 예방.

### 2. Sequential Agent 파이프라인
태스크를 순차적으로 수행하며 각 단계의 결과물(Handoff)을 다음 단계로 전달하는 구조입니다.

| 단계 | 산출물 (Hand-off) | 설명 |
| :--- | :--- | :--- |
| **00_planning.md** | 초기 구현 계획 | 사용자의 요청을 분석하고 전체적인 설계 방향 설정 |
| **01_review.md** | 리뷰 결과 | 계획의 실현 가능성, 보안, 효율성 검토 |
| **02_revised_plan.md** | 수정된 계획 | 리뷰 의견을 반영하여 정교화된 최종 계획 |
| **03_todo_list.md** | 체크리스트 | 실제 구현을 위한 세부 작업 단위 분해 |
| **04_final_report.md** | 최종 결과 보고 | 전체 프로세스 및 결과 요약 |

### 3. 멀티 에이전트 협업 전략 (예시)
- **Claude**: 설계 및 계획 (Plan) 담당.
- **Codex**: 실제 코드 구현 (Implementation) 담당.
- **Reviewer Agent**: 코드 리뷰 및 검증 담당.

## 설계 및 구현 가이드라인
1. **의도 일치**: PRD/SRS를 통해 에이전트와 의도를 먼저 맞춘 뒤 작업을 분해함.
2. **구조화된 문서화**: 파이프라인 스크립트의 명세를 재사용 가능한 마크다운 문서로 작성.
3. **Handoff 관리**: 각 단계별 또는 에이전트별 작업 내용을 별도 파일로 기록하여 추적성을 확보.

## 관련 용어 및 참조
- [[Agentic Coding]]
- [[Handoff]]
- [[SDLC]]
- [[Spec Driven Development]]

---
**Source**: `raw/4. Plan_mode Sequential and Parallel agents.pdf`
**Compiled by**: Knowledge Architect (LLM)
**Date**: 2026-05-20
