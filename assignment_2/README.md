# Agentic Wiki Tool (MCP Server)

본 프로젝트는 **게임 개발 및 데이터 지향 설계(DOD)** 도메인 지식을 관리하고 상호작용하기 위해 구축된 지능형 Wiki Tool입니다.
MCP(Model Context Protocol) 서버를 기반으로 하여 대화형 AI 에이전트가 로컬 마크다운 지식 베이스를 읽고, 검색하고, 안전하게 업데이트할 수 있도록 설계되었습니다.

## 1. 프로젝트 주요 기능
- **Streamlit 기반 MVP UI:** 좌측의 위키 탐색기(Markdown 뷰어)와 우측의 Conductor 챗봇 패널로 이루어진 직관적인 분할 UI.
- **Conductor 아키텍처:** 메인 에이전트가 단독으로 처리하지 않고, 사용자 의도를 파악하여 Planner, Writer, QA 서브 에이전트로 작업을 라우팅합니다.
- **안전한 지식 업데이트 (Human-in-the-loop):** 에이전트가 위키를 수정하기 전, 작성할 내용의 초안을 보여주는 '사전 보고(Draft Preview)'를 사용자에게 제시합니다. 승인(Approve)을 받은 경우에만 원자적 파일 쓰기(Atomic Write)를 수행하여 위키 오염 및 할루시네이션을 방지합니다.

## 2. 제공되는 MCP Tools
에이전트(LLM)는 다음 MCP 도구들을 통해 위키 파일 시스템과 상호작용합니다.
- `search_wiki`: 입력된 키워드를 기반으로 위키 폴더 내 관련 마크다운 문서 목록과 요약을 반환합니다.
- `read_page`: 특정 위키 문서(`[[문서명]]`)의 전체 텍스트를 읽어옵니다. (주로 QA 에이전트가 사용)
- `update_page`: Planner가 설계한 내용을 바탕으로 `.tmp.md` 임시 파일을 생성하고, 파일 쓰기가 성공한 경우에만 원본 위키 마크다운 파일로 덮어씁니다. (주로 Writer 에이전트가 사용)

## 3. 실행 방법 및 의존성 환경

### 환경 설정 (Prerequisites)
- OS: Windows 10/11
- Python 3.10 이상
- 필수 패키지 설치:
  ```bash
  pip install -r requirements.txt
  ```
*(주요 의존성: `streamlit`, `subprocess`, `mcp-sdk` 등)*

### 실행 명령어
1. 백그라운드 MCP 서버 및 웹 인터페이스 구동:
  ```bash
  streamlit run app.py
  ```
2. 웹 브라우저에서 `http://localhost:8501` 에 접속하여 우측 패널의 Conductor 챗봇과 대화하며 위키를 탐색 및 업데이트할 수 있습니다.
