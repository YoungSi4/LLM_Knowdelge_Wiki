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

## 5. Conductor & Risk Management

Main Agent(Conductor)를 통한 위키 운영 및 서브 에이전트 관리 시 적용되는 필수 지침입니다.

### 5.1 의도 오분류 (Intent Misclassification) 방지
- Conductor는 사용자의 지시가 영구적인 위키 업데이트(Build)인지 단순 검색(QA)인지 모호할 경우, 독단적으로 서브프로세스를 실행하지 않고 사용자에게 "위키에 저장할까요, 아니면 답변만 드릴까요?"라고 명시적으로 확인(Prompting)해야 합니다.

### 5.2 문맥 과부하 (Context Bloat) 방지
- 서브 에이전트의 전체 실행 로그 및 중간 사고 과정은 대화창(Conductor Session)에 직접 출력하지 않습니다.
- 에이전트는 성공 여부(Success/Fail) 및 핵심 결과 요약(Summary)만 Conductor로 반환하며, 상세 디버그 로그는 `wiki_build.log`에 독립적으로 기록하여 세션 토큰 낭비를 방지합니다.

### 5.3 원자성 보장 (Atomicity) 및 에러 복구
- **원자적 파일 쓰기 (Atomic Write):** Writer Agent는 수정/작성할 내용을 즉시 `./wiki/`의 원본 파일에 덮어쓰지 않습니다. 반드시 임시 파일(예: `.tmp`)에 전체 내용을 작성한 후, 작업이 정상적으로 완료되었음이 확인된 순간에만 원본 파일로 이름 변경(Rename/Move)을 수행합니다. 작성 중 에러가 발생하면 임시 파일을 삭제하여 상태를 롤백(Rollback)합니다.
- **오류 시그널링 (Error Signaling):** 서브 에이전트에서 오류가 발생한 경우, 단순한 프로세스 종료(Exit Code)를 넘어 Conductor가 원인을 즉시 파악할 수 있도록 명확한 오류 원인 시그널(예: `[ERROR_SIGNAL] JSON 파싱 실패`, `[ERROR_SIGNAL] Context 길이 초과` 등)을 반환해야 합니다. Conductor는 이 시그널을 바탕으로 사용자에게 구체적인 실패 사유를 보고해야 합니다.

### 5.4 에이전트별 권한 (Permissions) 및 위임 원칙 (Delegation)
- **Conductor (Main Agent)의 단독 처리 금지:** Conductor는 정보의 파싱, 위키 작성, 질의응답용 문서 검색 등의 실제 지식 처리 프로세스를 **직접 수행해서는 안 됩니다.** 반드시 사용자의 의도를 분석한 뒤, `pool/` 디렉토리에 정의된 목적에 맞는 Sub Agent(`wiki_planner`, `wiki_writer`, `wiki_qa` 등)를 서브프로세스로 호출하여 작업을 위임(Delegation)해야 합니다.
- **Planner Agent (`wiki_planner`):** `./raw/` 폴더 내의 원시 문서에 대한 **읽기 전용(Read-only)** 권한만 부여됩니다.
- **Writer Agent (`wiki_writer`):** 설계 문서를 바탕으로 `./wiki/` 폴더에 마크다운 파일을 생성 및 덮어쓸 수 있는 **쓰기 권한(Write)**이 부여됩니다. (단, 파일 쓰기 원자성 규칙 준수)
- **QA Agent (`wiki_qa`):** 구축된 지식 베이스인 `./wiki/` 폴더의 문서들에 대한 **읽기/검색 전용(Read/Search-only)** 권한만 부여되며, 문서를 임의로 수정하거나 훼손할 수 없습니다.
