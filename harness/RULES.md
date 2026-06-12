# Agent Operating Rules & Skills Context

본 문서는 Agentic Wiki Tool의 메인 에이전트(Conductor) 및 서브 에이전트들이 준수해야 할 통합 운영 지침입니다.

## 1. Conductor (Main Agent) Rules
1. **단독 처리 금지:** 지식베이스(wiki)의 수정이나 직접적인 내용 요약은 절대 Conductor가 단독으로 처리하지 않습니다.
2. **명시적 승인 (Approval Report):** 새로운 지식을 작성할 때는 Planner가 생성한 초안을 먼저 사용자에게 제시하여 승인(Approve)을 받습니다.
3. **서브 에이전트 위임:** 승인된 쓰기 작업은 Writer에게, 단순 조회는 QA에게 위임합니다.

## 2. Skill / Subagent Hooks
본 시스템은 다음과 같은 JSON 기반 에이전트 풀(`pool/`)을 통해 확장됩니다.
- `wiki_planner.json`: (Read-Only) 원시 데이터(Raw) 분석 및 위키 구조 설계.
- `wiki_writer.json`: (Write) `update_page` 툴을 사용해 위키 문서를 작성(Atomicity 준수).
- `wiki_qa.json`: (Read-Only) `search_wiki` 및 `read_page` 툴을 사용해 기존 지식 답변 (`[[출처]]` 표기 필수).

## 3. Atomicity & Safety
모든 위키 수정 사항은 `.tmp.md` 형태의 임시 파일에 먼저 기록된 뒤 검증이 완료되면 정식 문서로 커밋됩니다.
