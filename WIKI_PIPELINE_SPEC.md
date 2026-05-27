# Agentic Wiki Pipeline Specification

## 1. Goal
`./raw` 폴더에 새로운 문서가 추가되면, AI 에이전트들이 협력하여 이를 분석하고 `./wiki` 폴더에 고밀도 마크다운 문서를 자동으로 생성/업데이트하는 파이프라인을 구축합니다.

## 2. Pipeline Architecture (Sequential Agents)

| Step | Agent / Tool | Task | Output |
| :--- | :--- | :--- | :--- |
| **Ingest** | `ingest_pdf.py` | PDF를 원시 마크다운으로 변환 | `*.raw.md` |
| **Architect** | **Planner Agent** | 원시 텍스트 분석, 핵심 개념 추출, 위키 구조 설계 | `plan.md` |
| **Compile** | **Writer Agent** | `WIKI_SCHEMA`를 준수하여 위키 문서 작성 및 상호 참조 추가 | `*.md` in `./wiki` |
| **Index** | **Orchestrator** | `INDEX.md` 최신화 및 링크 연결 | `INDEX.md` |

## 3. Harness & Constraints
- **Contract**: 모든 위키 문서는 출처(Source)를 명시하고 `[[...]]` 링크를 2개 이상 포함해야 함.
- **Journal**: 모든 파이프라인 실행 이력은 `wiki_build.log`에 기록함.
- **Safety**: 기존 위키 문서를 덮어쓰기 전에는 변경 사항을 분석하여 중요한 정보가 누락되지 않도록 함.

## 4. Implementation Strategy
- Python의 `subprocess`를 사용하여 각 에이전트(CLI)를 호출함.
- `YOLO` 모드를 활용하여 자동화 흐름이 끊기지 않게 함.
