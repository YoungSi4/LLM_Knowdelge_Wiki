import subprocess
import os
import json
import tempfile
import argparse

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POOL_DIR = os.path.join(BASE_DIR, "pool")

def load_agent_config(agent_name):
    """pool 디렉토리에서 에이전트 JSON 설정을 로드합니다."""
    path = os.path.join(POOL_DIR, f"{agent_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_agent(agent_name, prompt, approval_mode="plan", resume=True):
    """에이전트 설정을 적용하여 Gemini CLI를 실행합니다."""
    config = load_agent_config(agent_name)
    if not config:
        print(f"[❌ 오류] 에이전트 설정을 찾을 수 없습니다: {agent_name}")
        return False

    print(f"\n{'='*40}\n[🚀 {config['name']} 실행중...]\n{config['description']}\n{'='*40}")
    
    env = os.environ.copy()
    # 시스템 프롬프트를 임시 파일로 만들어 GEMINI_SYSTEM_MD에 주입
    with tempfile.NamedTemporaryFile(suffix=".md", prefix=f"sys_{agent_name}_", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(config['system_prompt'])
        tmp_path = tmp.name
    
    env["GEMINI_SYSTEM_MD"] = tmp_path

    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    # --resume latest를 위해 세션 ID 관리 로직이 필요할 수 있으나, 여기서는 최신 세션을 잇는 것으로 가정
    cmd = [exe, "-p", prompt, "--approval-mode", approval_mode]
    if resume:
        cmd += ["--resume", "latest"]

    try:
        # 사용자와의 인터랙션이 필요할 수 있으므로 직접 실행 (stdin=None)
        # yolo 모드이므로 대부분 자동 진행됨
        result = subprocess.run(cmd, env=env)
        return result.returncode == 0
    except Exception as e:
        print(f"[💥 예외 발생]: {str(e)}")
        return False
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def main():
    parser = argparse.ArgumentParser(description="GitHub Trend Automation Orchestrator")
    parser.add_argument("--query", default="daily", help="조사 주기 (daily, weekly, monthly)")
    args = parser.parse_args()

    print(f"\n[🌟 GitHub 트렌드 자동화 시작] 주기: {args.query}")

    # 1단계: Research (데이터 수집)
    # 웹 검색 및 파일 쓰기가 필요하므로 yolo 모드 사용
    research_prompt = f"GitHub Trending ({args.query}) 페이지를 방문하여 인기 레포지토리 정보를 수집해줘. 결과를 'raw_trends.json'에 저장해."
    if not run_agent("research_agent", research_prompt, approval_mode="yolo", resume=False):
        print("❌ Research 단계에서 실패했습니다.")
        return

    # 2단계: Analysis (데이터 분석)
    analysis_prompt = "이전 단계에서 생성된 'raw_trends.json'을 읽고 현재 기술 트렌드와 주목할만한 프로젝트를 분석해줘. 분석 결과를 'trend_analysis.json'으로 저장해."
    if not run_agent("analysis_agent", analysis_prompt, approval_mode="yolo", resume=True):
        print("❌ Analysis 단계에서 실패했습니다.")
        return

    # 3단계: Report (리포트 생성)
    report_prompt = "분석된 'trend_analysis.json'을 바탕으로 최종 마크다운 리포트 'GITHUB_TREND_REPORT.md'를 작성해줘. 시각적으로 깔끔하게 구성해야 해."
    if not run_agent("report_agent", report_prompt, approval_mode="yolo", resume=True):
        print("❌ Report 단계에서 실패했습니다.")
        return

    print("\n" + "✨" * 20)
    print("✅ 모든 단계가 완료되었습니다!")
    print("결과물: GITHUB_TREND_REPORT.md")
    print("✨" * 20)

if __name__ == "__main__":
    main()
