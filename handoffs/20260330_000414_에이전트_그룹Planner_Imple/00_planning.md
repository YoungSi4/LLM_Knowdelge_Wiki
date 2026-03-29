# 📋 Initial Planning

사용자의 요청에 따라, 에이전트 그룹(Planner, Implementer, Reviewer)을 활용해 초기 요구사항으로부터 Plan(계획)과 Todo(할 일 목록)를 도출하고, 단계별로 Markdown 형식의 핸드오프(Handoff) 파일을 저장하는 자동화 파이프라인(`generate_plan.py`)의 아키텍처 및 구현 전략을 제안합니다.

---

# 📋 자동화 파이프라인 아키텍처 및 구현 전략

## 1. 시스템 아키텍처 개요

본 파이프라인은 단일 Python 스크립트(`generate_plan.py`)가 오케스트레이터(Orchestrator) 역할을 수행하며, Gemini CLI Subprocess API를 호출하여 세 개의 에이전트(Planner, Reviewer, Implementer)를 순차적으로 실행하는 구조입니다. 

*   **오케스트레이터 (`generate_plan.py`)**: 사용자 입력 처리, 디렉토리/파일 I/O 관리, 에이전트 간 세션 유지(`--resume`), 에러 및 타임아웃 처리를 담당합니다.
*   **에이전트 세션(Context)**: 첫 번째 에이전트가 생성한 대화 세션을 후속 에이전트들이 `--resume latest` 플래그를 통해 이어받음으로써, 이전 단계의 고민과 설계 내역을 완벽히 공유합니다.

### 에이전트 역할 정의
1.  **Planner (The Architect)**: 요구사항을 분석하고 전반적인 시스템 아키텍처와 초기 구현 전략을 수립합니다.
2.  **Reviewer (The Auditor)**: Planner의 초기 전략을 비판적으로 검토하여 누락된 엣지 케이스, 보안 문제, 논리적 결함을 찾아냅니다.
3.  **Implementer (The Builder)**: 확정된 최종 설계를 바탕으로, 개발자가 즉시 코드로 구현할 수 있는 구체적인 단계별 `Todo` 리스트와 검증 방법론을 도출합니다.

---

## 2. 데이터 흐름 및 핸드오프(Handoff) 전략

파이프라인 실행 시, 결과물 추적 및 디버깅을 용이하게 하기 위해 각 단계마다 고유 폴더에 Markdown 파일로 산출물을 저장합니다.

*   **저장소 구조**: `handoffs/{YYYYMMDD_HHMMSS}_{요청키워드}/`
*   **단계별 데이터 흐름**:
    *   **Step 1. Initial Planning**
        *   **주체**: Planner
        *   **입력**: User Request + Planner Persona 시스템 프롬프트
        *   **산출물**: `00_planning.md` (초기 설계안)
    *   **Step 2. Design Review**
        *   **주체**: Reviewer
        *   **입력**: Step 1 세션 유지 + Reviewer Persona 시스템 프롬프트
        *   **산출물**: `01_review.md` (설계 비판 및 개선점 리스트)
    *   **Step 3. Revised Planning**
        *   **주체**: Planner
        *   **입력**: Step 2 세션 유지 + 수정보완 지시 프롬프트
        *   **산출물**: `02_revised_planning.md` (최종 확정된 설계안)
    *   **Step 4. Generating Todo**
        *   **주체**: Implementer
        *   **입력**: Step 3 세션 유지 + Implementer Persona 시스템 프롬프트
        *   **산출물**: `03_todo_list.md` (구체화된 할 일 목록 및 테스트 방법)
    *   **Step 5. Final Aggregation**
        *   **주체**: Orchestrator (Script)
        *   **동작**: 3단계(Revised Plan)와 4단계(Todo)의 결과를 취합.
        *   **산출물**: `04_final_plan_report.md` (최종 요약본) 및 프로젝트 루트의 `PROJECT_PLAN.md` 덮어쓰기.

---

## 3. 핵심 구현 전략 (Implementation Strategy)

### 3.1. Gemini CLI 연동 모듈 최적화
*   `GeminiRequest` 데이터 클래스를 활용하여 파라미터를 규격화합니다.
*   `subprocess.run`을 통해 동기적으로 CLI를 호출하되, 무한 대기를 방지하기 위해 반드시 `timeout_sec` (예: 300초)을 설정합니다.
*   각 에이전트의 페르소나(시스템 프롬프트)는 임시 파일(`tempfile`)을 생성하여 `GEMINI_SYSTEM_MD` 환경 변수로 주입한 뒤, 호출 완료 후 안전하게 삭제합니다.

### 3.2. 상태 유지 (Session Management)
*   에이전트 그룹이 하나의 컨텍스트를 공유해야 하므로, Step 2부터는 파라미터에 `resume=True`를 전달하여 CLI 명령에 `--resume latest`가 포함되도록 강제합니다.
*   권한 모드(`approval_mode`)는 코드 자동 생성을 제한하고 기획에 집중하도록 `--approval-mode plan`을 유지합니다.

### 3.3. 견고한 에러 핸들링 방안 (Robustness)
*   CLI 호출 결과의 `returncode`가 `0`이 아닐 경우(예: 컨텍스트 길이 초과, 타임아웃, 포맷 에러), 파이프라인을 즉시 중단하고 명확한 에러 로그(stderr)를 출력하도록 예외 처리를 구성합니다.
*   폴더 및 파일명 생성 시, 윈도우/리눅스 환경에서 모두 작동하도록 불법 문자(Special Characters)를 정규식(`re.sub`)으로 필터링합니다.

### 3.4. 확장성 고려
*   추후 `Implementer`가 실제 코드를 수정하는 Auto-Coding 워크플로우로 확장할 수 있도록, 현재의 스크립트 구조(직관적인 순차 실행)를 유지하되 각 단계를 함수로 분리할 수 있는 여지를 남겨둡니다. 

---

**요약**: 위 전략을 기반으로 구축된 `generate_plan.py`는 사용자의 모호한 요구사항을 다각도로 분석하고, 안정성이 확보된 아키텍처 청사진과 실행 가능한 Todo 리스트로 변환하는 강력한 기획 전위대(Vanguard) 역할을 수행하게 될 것입니다.
