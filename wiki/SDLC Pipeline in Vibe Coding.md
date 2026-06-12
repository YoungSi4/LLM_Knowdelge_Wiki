# SDLC Pipeline in Vibe Coding

Vibe Coding 패러다임에서의 시스템 분석 및 설계 가이드라인. 단순히 코드를 생성하는 것을 넘어, 체계적인 소프트웨어 개발 생명주기(SDLC)를 AI와 함께 수행하는 방식을 다룹니다.

## 1. Vibe Coding vs Agentic Coding
Vibe Coding의 한계를 극복하기 위해 Agentic Coding으로 진화하고 있습니다.

| 특성 | Vibe Coding | Agentic Coding |
| :--- | :--- | :--- |
| **접근 방식** | One-Shot Generation | Description per each Agent |
| **문서화** | PRD/SRS 생략 혹은 단순 붙여넣기 | 상세 Prompt + PRD/SRS 기반 |
| **인간의 역할** | Prompt Engineering | Orchestrator |
| **에이전트 구조** | Single Conversation | Sequential / Multi-Agent |
| **적합한 규모** | Small-Size Application | Large-Scale Product |

## 2. SDLC 단계별 접근 (Vibe/Agentic)

### Planning & Analysis
- **목적**: 무엇을 왜 만드는가 (Business Need, Feasibility).
- **작업**: PRD(Product Requirements Document) 우선 작성.
- **도구**: [[Plan Mode and Sequential Agents]] 활용하여 단계별 작업 분해.

### Design & Implementation
- **원칙**: Spec-Driven Development (Spec First, Code Later).
- **프로세스**: 요구사항 명세(SRS)를 LLM과 논의 후 구현.
- **검증**: [[Loop and Hooks]]를 통해 피드백 루프 형성.

## 3. 에이전트 구조
복잡한 시스템 구현을 위해 다음과 같은 에이전트 패턴을 적용합니다.

- **Single Agent**: 명확하고 구조화된 요청 기반 작업.
- **Sequential Agent**: 독립적 단계의 순차 실행 (예: Analysis -> Design -> Implementation).
- **Parallel Agent**: 전문화된 서브 에이전트의 동시 작업 (예: Research/WebSearch 단계).

---
*Raw Source: 2. SDLC pipeline in Vibe coding.pdf*
