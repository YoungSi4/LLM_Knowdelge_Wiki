# Agent Specifications

## 개요
에이전트틱 코딩 파이프라인에서 각 에이전트의 역할 정의(Role Specification)와 시스템 프롬프트(System Prompt) 설계, 그리고 에이전트 간의 협업 워크플로우를 다룹니다.

## 에이전트 역할 정의 (Role Specification)

### 1. Planner Agent
- **주요 단계**:
    1. **Analysis**: 요청의 목표(Goal)와 기술적 제약(Constraints) 판단.
    2. **Decomposition**: 목표를 실현 가능한 작업 단위로 쪼개고 실행 순서와 의존성 결정.
    3. **Planning**: 각 TODO 항목에 대해 입력, 출력, 구현 방법, 완료 기준(AC) 구체화.
- **산출물**: `Plan.md`, `TODO.md`

### 2. Reviewer Agent
- **주요 단계**:
    1. **Validation**: 모든 TODO에 입출력 및 완료 기준(AC)이 포함되어 있는지 확인.
    2. **Review**: 기술적 구현 가능성, 의존성 순서의 적절성, 모호성 평가.
    3. **Revise**: 1~10점 사이의 점수를 부여하고 구체적인 개선 사항 제안.
- **산출물**: `Review.md`

## 시스템 프롬프트(System Prompt) 구성 요소
에이전트의 행동을 제어하기 위한 핵심 요소들입니다.
- **Role**: 에이전트의 정체성 (예: "너는 소프트웨어 아키텍트이다").
- **Instructions**: 수행해야 할 구체적인 작업 지침.
- **Constraints**: 하지 말아야 할 행동이나 형식적 제약.
- **Context**: 프로젝트 정보, 세션 ID, 이전 단계의 산출물(Handoff) 등.

## 에이전트 협업 패턴: 핑퐁(Ping-pong) 게임
에이전트들이 서로의 결과물을 검토하고 개선하는 반복 프로세스입니다.
- **예시**: Reviewer가 Planner의 계획에 8점 이상을 줄 때까지 루프를 반복함.
- **Handoff 메커니즘**: 에이전트 간의 데이터 전달은 주로 로컬 마크다운 파일이나 세션 ID를 통해 이루어집니다.

## 확장 파이프라인 모델
복잡한 프로젝트를 위해 더 세분화된 에이전트 구성을 가질 수 있습니다.
- **Planner**: 요구사항 분석 및 설계.
- **Reviewer**: 설계 검토 및 승인.
- **Coder**: 실제 코드 구현 및 리팩토링.
- **Tester**: 테스트 코드 작성 및 검증.

## 관련 용어 및 참조
- [[Planner Agent]]
- [[Reviewer Agent]]
- [[System Prompt]]
- [[Handoff]]

---
**Source**: `raw/5. Agent Specifications.pdf`
**Compiled by**: Knowledge Architect (LLM)
**Date**: 2026-05-20
