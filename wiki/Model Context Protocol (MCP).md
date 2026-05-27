# Model Context Protocol (MCP)

## 개요
Anthropic이 주도하고 주요 AI 기업들이 참여하는 표준 프로토콜로, AI 에이전트가 외부 데이터 소스 및 도구와 연결되는 방식을 표준화합니다. "AI용 USB 인터페이스"에 비유됩니다.

## 핵심 개념

### 1. 도입 배경 및 목적
- **파편화된 연결 방식**: 과거에는 각 서비스(Slack, GitHub, DB 등)와 에이전트를 연결하기 위해 전용 커넥터 코드를 매번 작성해야 했음.
- **표준화**: MCP를 통해 에이전트는 외부 시스템의 내부 구조를 깊이 알 필요 없이 표준화된 인터페이스를 통해 도구(Tools), 리소스(Resources), 프롬프트(Prompts)에 접근 가능함.
- **비용 및 성능**: 복잡한 분석 작업을 줄여 토큰 소모를 방지하고 응답 성능을 개선함.

### 2. MCP의 주요 기능
- **도구 호출 (Tool Calling)**: 에이전트가 특정 작업을 수행하기 위해 외부 함수나 API를 실행함.
- **리소스 접근 (Resources)**: DB나 파일 시스템 등 외부 데이터를 읽어옴.
- **프롬프트 템플릿 (Prompts)**: 구조화된 명령 형식을 공유함.

### 3. 기술적 특징: 캡슐화 및 추상화
- 에이전트는 MCP가 제공하는 도구의 내부 로직을 신경 쓸 필요가 없음 (**추상화**).
- 복잡한 API 호출이나 데이터 처리 과정이 MCP 서버 내부에 감춰짐 (**캡슐화**).
- 이를 통해 `Orchestrator-Worker` 모델과 같은 복잡한 에이전트 구조를 효율적으로 운영할 수 있음.

## Tradeoff: Context Explosion
- 에이전트가 사용할 수 있는 도구가 너무 많아지면, 각 도구의 기능과 사용법을 컨텍스트에 포함해야 함.
- 이는 컨텍스트 윈도우의 급격한 소모(Context Explosion)를 야기할 수 있으므로, 적절한 도구 선택(Routing) 전략이 필요함.

## 실습 사례: AgentMEMO MCP Server
- **목표**: 개인 메모 관리 시스템(`AgentMEMO`)을 MCP 서버로 구축하여 에이전트가 메모를 읽고 쓸 수 있게 함.
- **주요 도구**: `memo.create`, `memo.list`, `memo.update`, `memo.append` 등.
- **구현 도구**: `FastMCP` (Python 기반 MCP 서버 프레임워크).

## 관련 용어 및 참조
- [[Agent Pool]]
- [[Orchestrator]]
- [[Tool Calling]]
- [[Context Explosion]]

---
**Source**: `raw/8. Model Context Protocol.pdf`
**Compiled by**: Knowledge Architect (LLM)
**Date**: 2026-05-20
