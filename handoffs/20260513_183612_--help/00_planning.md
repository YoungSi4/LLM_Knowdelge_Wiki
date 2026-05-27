# 📋 Initial Planning

사용자님, 입력하신 `--help` 요청에 따라 현재 구성된 **Gemini Multi-Agent SDLC Orchestrator** 시스템의 전체 구조 및 사용 가이드를 안내해 드립니다. 

이 시스템은 복잡한 소프트웨어 개발 태스크를 여러 특화된 AI 에이전트(Planner, Coder, Reviewer, Tester)가 협력하여 해결하도록 설계된 자동화 파이프라인입니다.

---

### 🚀 Gemini Multi-Agent SDLC Orchestrator 가이드

#### 1. 주요 구성 요소 및 아키텍처
본 시스템은 에이전트 그룹 워크플로우를 통해 안전하고 체계적으로 개발을 수행합니다. 핵심 파이프라인은 `orchestrator_full_pipeline.py` 스크립트를 통해 구동됩니다.

*   **Planner (설계자)**: 요구사항을 분석하고 구체적인 구현 설계도(TODO 리스트 및 수락 기준)를 수립합니다. (수정 권한 없는 `plan` 모드 사용)
*   **Reviewer (검토자)**: Planner의 계획이나 Coder의 구현 결과물을 엄격하게 리뷰하고 점수(Score)를 매깁니다. 기준(8/10점)을 넘지 못하면 반려(Reject)하여 재수정을 지시합니다. (`plan` 모드 사용)
*   **Coder (구현자)**: 승인된 설계에 따라 실제 코드를 작성하고 수정합니다. (`yolo` 또는 `auto_edit` 모드 사용)
*   **Tester (검증자)**: 구현된 코드가 요구사항을 충족하는지 검증하고 테스트 리포트를 작성합니다. 실패 시 Coder에게 피드백을 주어 재수정하도록 합니다.

#### 2. 워크플로우 (파이프라인) 진행 단계
파이프라인 실행 시 다음 3단계를 순차적으로 반복(Ping-Pong)하며 진행됩니다:
*   **STEP 1 (설계 및 리뷰)**: Planner가 계획을 세우면 Reviewer가 평가합니다. (8점 이상 통과)
*   **STEP 2 (코드 구현)**: 통과된 계획을 바탕으로 Coder가 코드를 구현합니다.
*   **STEP 3 (검증 및 품질 관리)**: Tester가 코드를 검증하고 평가합니다. (8점 이상 최종 통과, 미만 시 Coder가 다시 수정)

#### 3. 실행 방법
명령 프롬프트(CLI)에서 아래와 같이 파이프라인 스크립트를 실행할 수 있습니다.

**단일 요구사항 실행:**
```bash
python orchestrator_full_pipeline.py "로그인 기능에 대한 유효성 검사 코드를 추가해줘"
```
**대화형 프롬프트 실행 (인자 없이 실행):**
```bash
python orchestrator_full_pipeline.py
# 실행 후 프롬프트가 나타나면 요구사항을 입력하세요.
```

#### 4. 하위 시스템 (Gemini CLI Subprocess API)
이 파이프라인은 내부적으로 `gemini` 프로세스를 서브프로세스(Subprocess)로 호출하여 동작합니다. 주요 CLI 플래그는 다음과 같습니다.
*   `--approval-mode {plan|auto_edit|yolo|default}`: 에이전트의 권한 및 자율성 수준 설정
*   `--resume {latest|<session_id>}`: 이전 대화 컨텍스트 유지 및 이어서 작업
*   `-o {text|json|stream-json}`: 에이전트의 출력 형식 지정

---

**아키텍트의 질문:**
단순히 시스템 사용법을 확인하기 위해 `--help`를 입력하셨는지, 아니면 이 파이프라인 내부에 CLI 명령어로 동작하는 새로운 `--help` 기능을 구현하기 위한 전략을 구상하기 위해 입력하셨는지 알려주시면, 그에 맞춰 추가적인 계획 수립이나 모드 종료를 진행하겠습니다!
