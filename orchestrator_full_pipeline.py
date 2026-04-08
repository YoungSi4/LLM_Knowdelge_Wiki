import subprocess
import os
import re
import argparse

# 시스템 프롬프트 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_PROMPTS = {
    "planner": None,  # 기본 개발 모드 사용
    "reviewer": os.path.join(BASE_DIR, "reviewer_system_prompt.md"),
    "coder": os.path.join(BASE_DIR, "coder_agent.md"),
    "tester": os.path.join(BASE_DIR, "tester_agent.md")
}

def run_agent(prompt, task_name, persona, approval_mode="plan", resume=True):
    """지정된 페르소나와 모드로 Gemini를 실행하고 결과를 반환"""
    print(f"\n{'='*25}\n[🚀 {task_name} 에이전트 가동]\n{'='*25}")
    
    env = os.environ.copy()
    sys_md = SYS_PROMPTS.get(persona)
    if sys_md and os.path.exists(sys_md):
        env["GEMINI_SYSTEM_MD"] = sys_md
    else:
        env.pop("GEMINI_SYSTEM_MD", None)

    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    cmd = [exe, "-p", prompt, "--approval-mode", approval_mode]
    if resume:
        cmd += ["--resume", "latest"]

    try:
        # stdin=subprocess.DEVNULL을 추가하여 인터랙티브 입력 대기 방지
        result = subprocess.run(cmd, env=env, text=True, capture_output=True, encoding='utf-8', stdin=subprocess.DEVNULL)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"[❌ 오류] {task_name} 실행 실패 (코드 {result.returncode})")
            print(f"STDOUT: {result.stdout[:500]}...")
            print(f"STDERR: {result.stderr}")
            return None
    except Exception as e:
        print(f"[💥 예외 발생]: {str(e)}")
        return None

def extract_score(text):
    """출력물에서 점수(score)를 추출"""
    if not text: return 0
    match = re.search(r"점수\s*[:\[]\s*(\d+)", text)
    return int(match.group(1)) if match else 0

def main():
    parser = argparse.ArgumentParser(description="범용 SDLC 에이전트 파이프라인")
    parser.add_argument("requirement", nargs="?", help="수행할 요구사항 (생략 시 입력 요청)")
    args = parser.parse_args()

    requirement = args.requirement
    if not requirement:
        print("--- 범용 SDLC 파이프라인 ---")
        requirement = input("수행할 요구사항을 입력하세요: ").strip()
    
    if not requirement:
        print("요구사항이 없습니다. 종료합니다.")
        return

    print(f"\n[🚀 파이프라인 시작] 요구사항: {requirement}")
    
    # 1단계: Planning Loop (Planner <-> Reviewer)
    print("\n[STEP 1] 요구사항 분석 및 설계 단계")
    plan_prompt = f"[Planner] 다음 요구사항을 달성하기 위한 상세 설계(TODO 리스트 및 수락 기준)를 작성해줘: {requirement}"
    while True:
        plan_out = run_agent(plan_prompt, "Planner", "planner", approval_mode="plan", resume=True)
        review_out = run_agent("이 계획을 리뷰하고 점수를 매겨줘. '점수: [N]' 형식을 포함해줘.", "Reviewer", "reviewer", approval_mode="plan", resume=True)
        score = extract_score(review_out)
        print(f"-> 설계 점수: {score}/10")
        if score >= 8: 
            print("✅ 설계 승인 완료!"); break
        plan_prompt = f"Reviewer 피드백을 반영하여 계획을 수정해줘: {review_out}"

    # 2단계: Implementation (Coder)
    print("\n[STEP 2] 코드 구현 단계")
    code_prompt = f"[Coder] 승인된 설계에 따라 코드를 구현하거나 수정해줘. 요구사항: {requirement}"
    # 실질적인 파일 생성을 위해 yolo 모드 사용
    code_out = run_agent(code_prompt, "Coder", "coder", approval_mode="yolo", resume=True)
    print("✅ 코드 구현 완료!")

    # 3단계: Verification (Tester)
    print("\n[STEP 3] 검증 및 품질 관리 단계")
    test_prompt = f"[Tester] 구현된 코드가 요구사항({requirement})을 만족하는지 검증하고 테스트 리포트를 작성해줘."
    while True:
        # 테스트는 코드를 실행해야 할 수 있으므로 yolo 모드 사용
        test_out = run_agent(test_prompt, "Tester", "tester", approval_mode="yolo", resume=True)
        score = extract_score(test_out)
        print(f"-> 검증 점수: {score}/10")
        if score >= 8:
            print("✅ 최종 검증 통과! 모든 공정이 완료되었습니다."); break
        
        # 테스트 실패 시 Coder에게 재수정 요청
        print("❌ 검증 실패. Coder가 코드를 수정합니다.")
        fix_prompt = f"[Coder] Tester의 피드백을 반영하여 버그를 수정해줘: {test_out}"
        run_agent(fix_prompt, "Coder Fix", "coder", approval_mode="yolo", resume=True)
        test_prompt = "수정된 코드를 다시 검증해줘."

    print("\n=== 파이프라인 전체 공정 종료 ===")

if __name__ == "__main__":
    main()
