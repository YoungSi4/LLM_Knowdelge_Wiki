import subprocess
import os
import re
import time

# 설정
PLANNER_PROMPT = "[Planner] Yacht Game에서 '주사위 정렬 후에도 고정(Keep) 인덱스가 유지되는 기능'을 구현하기 위한 상세 TODO 리스트를 작성해줘. 입출력 정의와 AC(Acceptance Criteria)를 포함해."
REVIEWER_SYS_MD = r"D:\system_analysis\reviewer_system_prompt.md"
MAX_ITERATIONS = 5  # 최대 반복 횟수

def run_gemini_step(prompt, task_name, use_reviewer=False, resume=False):
    """Gemini CLI를 실행하고 결과를 반환하는 함수"""
    print(f"\n{'='*20}\n[🚀 {task_name} 시작]\n{'='*20}")
    
    env = os.environ.copy()
    if use_reviewer:
        env["GEMINI_SYSTEM_MD"] = REVIEWER_SYS_MD
    else:
        # Planner일 때는 시스템 프롬프트 해제 (일반 모드)
        env.pop("GEMINI_SYSTEM_MD", None)

    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    cmd = [exe, "-p", prompt, "--approval-mode", "plan"]
    
    if resume:
        cmd += ["--resume", "latest"]

    try:
        # 결과를 파싱하기 위해 capture_output=True 사용
        result = subprocess.run(cmd, env=env, text=True, capture_output=True, encoding='utf-8')
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"[❌ 오류] 종료 코드: {result.returncode}\n{result.stderr}")
            return None
    except Exception as e:
        print(f"[💥 예외 발생]: {str(e)}")
        return None

def extract_score(text):
    """Reviewer의 출력에서 점수를 추출하는 정규표현식"""
    # "## 점수 [8 - 10]" 형식에서 숫자 추출
    match = re.search(r"## 점수 \[(\d+)\s*-\s*10\]", text)
    if match:
        return int(match.group(1))
    return 0

def main():
    print("=== Plan-Review Ping-Pong Orchestrator (Yacht Game) ===")
    
    current_planner_prompt = PLANNER_PROMPT
    iteration = 1
    
    while iteration <= MAX_ITERATIONS:
        # 1. Planner: 계획 생성
        plan_output = run_gemini_step(current_planner_prompt, f"Round {iteration}: Planner", resume=(iteration > 1))
        if not plan_output: break
        
        print(f"\n[Planner 출력 요약]:\n{plan_output[:200]}...")

        # 2. Reviewer: 계획 평가
        review_prompt = "방금 작성된 계획을 리뷰해줘. 반드시 정해진 형식을 지키고 점수를 매겨줘."
        review_output = run_gemini_step(review_prompt, f"Round {iteration}: Reviewer", use_reviewer=True, resume=True)
        if not review_output: break
        
        print(f"\n[Reviewer 피드백]:\n{review_output}")
        
        # 3. 점수 확인 및 조건 분기
        score = extract_score(review_output)
        print(f"\n⭐ 현재 점수: {score} / 10")
        
        if score >= 8:
            print(f"\n✅ [성공] 8점 이상 획득! 최종 계획이 승인되었습니다.")
            # 최종 계획을 파일로 저장 (선택 사항)
            with open("final_yacht_plan.md", "w", encoding="utf-8") as f:
                f.write(plan_output)
            break
        else:
            print(f"\n🔄 [재수정] 점수가 낮습니다. Reviewer의 피드백을 반영하여 수정을 요청합니다.")
            current_planner_prompt = f"Reviewer가 당신의 계획에 {score}점을 주었습니다. 다음 피드백을 반영하여 계획을 보완해줘:\n\n{review_output}"
            iteration += 1
            
    if iteration > MAX_ITERATIONS:
        print(f"\n⚠️ [중단] 최대 반복 횟수({MAX_ITERATIONS})를 초과했습니다.")

if __name__ == "__main__":
    main()
