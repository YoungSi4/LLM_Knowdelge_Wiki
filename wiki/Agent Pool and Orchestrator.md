# Agent Pool and Orchestrator

## 개요
개별 에이전트를 자산화하여 관리하는 **Agent Pool** 개념과, 목표에 따라 적절한 에이전트를 선택하고 실행하는 **Orchestrator**의 설계 및 운영 방식을 다룹니다.

## 핵심 개념

### 1. Agent Pool
- **정의**: 개별 에이전트의 정체성, 프롬프트, 입력/출력 형식, 도구 권한 등을 정형화된 데이터(JSON, TOML 등)로 관리하는 저장소.
- **주요 속성 (JSON 예시)**:
    - `id`: 에이전트 식별자.
    - `role`: 역할 설명.
    - `system_prompt`: 핵심 지침.
    - `input/output`: 데이터의 형식 및 출처/목적지.
    - `tools`: 사용 가능한 도구 및 권한 수준.
    - `constraints`: 최대 시도 횟수, 타임아웃 등.

### 2. Orchestrator
- **정의**: 전체 워크플로우를 관리하는 상위 에이전트 또는 시스템.
- **역할**:
    - `pool/*.json`에 정의된 에이전트 명세를 읽음.
    - 주어진 목표를 달성하기 위해 필요한 에이전트를 선택.
    - `subprocess`를 통해 독립적으로 에이전트를 실행하고 결과를 수집.
    - 에이전트 간의 상태(States) 및 전이(Transitions) 관리.

### 3. 에이전트 상태 관리
에이전트는 워크플로우 내에서 다음과 같은 상태를 가집니다:
- **Idle**: 대기 중.
- **Running (Processing)**: 작업 수행 중.
- **Completed**: 작업 완료 및 결과 반환.
- **Failed**: 오류 발생 및 중단.

## 운영 도구 및 워크플로우

### 1. Agent Dashboard
- 에이전트 풀의 상태를 실시간으로 모니터링하는 도구.
- 에이전트별 현재 상태, 라운드 번호, 실행 이력 등을 시각적으로 표시.

### 2. 컨텍스트 파일 (Schema)
오케스트레이터와 에이전트의 행동 지침을 담은 로컬 설정 파일입니다.
- `GEMINI.md`, `CLAUDE.md`, `AGENTS.md` 등으로 관리.
- 프로젝트의 규칙, 코딩 스타일, 협업 방식을 명시하여 일관성 유지.

## 확장 사례: GitHub 트렌드 조사 파이프라인
1. **Research Agent**: 웹 검색을 통해 트렌드 수집.
2. **Analysis Agent**: 수집된 데이터 분석 및 유의미한 정보 추출.
3. **Report Agent**: 최종 리포트 마크다운 문서 생성.

## 관련 용어 및 참조
- [[Agent Pool]]
- [[Orchestrator]]
- [[Context Engineering]]
- [[Subprocess Agent Team]]

---
**Source**: `raw/6. Agent pool and Orchestrator.pdf`
**Compiled by**: Knowledge Architect (LLM)
**Date**: 2026-05-20
