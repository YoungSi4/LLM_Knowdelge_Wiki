# ✅ Implementation Todo List

최종 확정된 "상태 비저장(Stateless) 기반 독립 세션 + 컨텍스트 주입" 아키텍처를 바탕으로, 실무 개발자가 즉시 `generate_plan.py`를 구현할 수 있도록 단계별 Todo 리스트와 검증 방법을 작성했습니다.

---

# ✅ Implementation Todo List (구현 할 일 목록)

## Phase 1: 기반 모듈 및 유틸리티 설정
이 단계에서는 파이프라인의 안전한 실행을 위한 디렉토리 관리 및 필수 데이터 구조를 구현합니다.

*   **[ ] Todo 1.1: 필수 라이브러리 임포트 및 기본 구조 세팅**
    *   `subprocess`, `os`, `tempfile`, `re`, `uuid`, `datetime`, `dataclasses` 임포트.
*   **[ ] Todo 1.2: 안전한 핸드오프 디렉토리 생성 함수 구현 (`create_handoff_dir`)**
    *   **로직**:
        1. `user_request`에서 정규식(`re.sub(r'[^\w\s-]', '', text)`)을 통해 특수문자를 제거하고 최대 20자 추출.
        2. 추출된 문자열이 비어있으면 `default_task`로 대체.
        3. `YYYYMMDD_HHMMSS` 형식의 타임스탬프와 `uuid.uuid4().hex[:6]` 생성.
        4. `handoffs/{timestamp}_{uuid}_{safe_request}/` 경로 생성 및 반환.
    *   **검증 방법 (Verification)**:
        *   특수문자만 포함된 문자열(예: `"!@#$$%"`)을 함수에 전달하여 빈 문자열 예외가 발생하지 않고 `default_task`가 포함된 폴더가 생성되는지 확인합니다.
*   **[ ] Todo 1.3: 에이전트 설정 데이터 클래스 정의 (`AgentConfig`)**
    *   **필드**: `role_name` (에이전트 이름), `system_prompt` (페르소나 제약 조건), `approval_mode` (기본값 `"yolo"`), `required_headers` (리스트, 예: `["# 📋"]`), `min_length` (기본값 150).

---

## Phase 2: 코어 실행 엔진 구현
Gemini CLI를 서브프로세스로 안전하게 호출하고 결과물을 검증하는 핵심 엔진을 구축합니다.

*   **[ ] Todo 2.1: CLI 서브프로세스 호출 함수 구현 (`execute_agent`)**
    *   **로직**:
        1. `tempfile.mkstemp`로 임시 마크다운 파일을 생성하여 `config.system_prompt`를 작성하고 `GEMINI_SYSTEM_MD` 환경 변수에 매핑.
        2. `gemini -p "<prompt>" --approval-mode <config.approval_mode>` 명령 구성.
        3. `subprocess.run(timeout=300)` 실행 (타임아웃 시 예외 포착 후 실패 반환).
        4. 실행 완료 후 임시 시스템 프롬프트 파일 삭제 (finally 블록).
*   **[ ] Todo 2.2: LLM 산출물 정합성 검증 로직 추가 (in `execute_agent`)**
    *   **로직**:
        1. 서브프로세스 종료 코드가 `0`이 아니면 에러 반환.
        2. `stdout`의 길이가 `config.min_length` 미만이면 "내용이 너무 짧습니다" 에러 반환.
        3. `config.required_headers`에 정의된 헤더 문자열이 `stdout`에 포함되어 있지 않으면 "필수 마크다운 포맷 누락" 에러 반환.
    *   **검증 방법 (Verification)**:
        *   `execute_agent` 함수를 단독으로 호출하되, `min_length`를 5000으로 설정하여 의도적으로 검증 실패 에러가 반환되는지 단위 테스트합니다.

---

## Phase 3: 파이프라인 Step-by-Step 구현
각 에이전트의 역할에 맞는 프롬프트를 구성하고 컨텍스트를 주입합니다.

*   **[ ] Todo 3.1: Step 1 (Initial Planning) 구현**
    *   `PlannerConfig` 생성 (읽기 전용 제약, `# 📋` 필수 포함).
    *   프롬프트 인젝션 방어: 사용자의 요청을 `<user_request>{요청}</user_request>` 태그로 감싸서 전달.
    *   결과를 `00_planning.md`에 저장.
*   **[ ] Todo 3.2: Step 2 (Design Review) 구현**
    *   `ReviewerConfig` 생성 (까다로운 리뷰어 페르소나, 읽기 전용 제약, `# 🔍` 필수 포함).
    *   프롬프트: "다음 설계안을 비판적으로 리뷰하라:\n\n{00_planning.md의 내용}" (파일 읽어서 주입).
    *   결과를 `01_review.md`에 저장.
*   **[ ] Todo 3.3: Step 3 (Revised Planning) 구현**
    *   `RevisedPlannerConfig` 생성 (수정 설계자 페르소나, 읽기 전용 제약, `# 🏗️` 필수 포함).
    *   프롬프트: "초기 설계안:\n{00_planning.md}\n\n리뷰 피드백:\n{01_review.md}\n\n피드백을 반영하여 최종 설계안을 작성하라."
    *   결과를 `02_revised_planning.md`에 저장.
*   **[ ] Todo 3.4: Step 4 (Generating Todo) 구현**
    *   `ImplementerConfig` 생성 (실무 개발자 페르소나, `# ✅` 필수 포함).
    *   프롬프트: "다음 확정된 설계를 바탕으로 즉시 구현 가능한 구체적인 Todo 리스트를 작성하라:\n\n{02_revised_planning.md}"
    *   결과를 `03_todo_list.md`에 저장.
    *   **검증 방법 (Verification)**:
        *   더미 텍스트를 담은 `00~02.md` 파일을 준비한 후, Step별 함수가 이전 파일의 내용을 정상적으로 읽어와서 다음 파일(`01~03.md`)을 생성해내는지 중간 테스트(Integration Test)를 수행합니다.

---

## Phase 4: 오케스트레이션 및 최종화
전체 흐름을 제어하고 결과물을 병합합니다.

*   **[ ] Todo 4.1: 최종 산출물 병합 함수 구현 (`finalize_report`)**
    *   `02_revised_planning.md`와 `03_todo_list.md`의 내용을 읽어옵니다.
    *   `# 📋 Project Plan & Final Report` 제목 아래 두 내용을 결합합니다.
    *   핸드오프 폴더에 `04_final_plan_report.md`로 저장하고, 루트 디렉토리의 `PROJECT_PLAN.md`를 덮어씁니다.
*   **[ ] Todo 4.2: 메인 파이프라인 묶기 (`main_pipeline`)**
    *   Step 1부터 5(`finalize_report`)까지 순차적으로 호출.
    *   중간에 어느 단계라도 `result.ok == False`가 반환되면, `print(f"❌ [에러 발생] {단계명}: {result.stderr}")` 출력 후 프로세스를 즉시 `exit(1)`으로 종료(Fail-fast)하는 예외 처리 추가.
    *   **최종 검증 방법 (End-to-End Verification)**:
        *   `python generate_plan.py "test_api.py에 대한 단위 테스트 코드를 작성해줘"` 명령어를 터미널에서 실행합니다.
        *   CLI가 행(Hang)에 걸리지 않고 파이프라인이 끝까지 실행되는지 확인합니다.
        *   루트 폴더의 `PROJECT_PLAN.md`에 설계와 Todo가 모두 정상적으로 결합되어 출력되었는지 최종 확인합니다.
