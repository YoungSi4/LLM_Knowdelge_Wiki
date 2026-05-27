import subprocess
import os
import re
import argparse

# 시스템 프롬프트 경로
SYS_PROMPTS = {
    "planner": None,
    "reviewer": r"D:\system_analysis\generic_reviewer.md",
    "coder": r"D:\system_analysis\generic_coder.md",
    "tester": r"D:\system_analysis\generic_tester.md"
}

def run_agent(prompt, task_name, persona, approval_mode="plan", resume=True):
    print(f"\n{'='*30}\n[🚀 {task_name} 에이전트 시작]\n{'='*30}")
    
    env = os.environ.copy()
    sys_md = SYS_PROMPTS.get(persona)
    if sys_md:
        env["GEMINI_SYSTEM_MD"] = sys_md
    else:
        env.pop("GEMINI_SYSTEM_MD", None)

    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    cmd = [exe, "-p", prompt, "--approval-mode", approval_mode]
    if resume:
        cmd += ["--resume", "latest"]

    try:
        result = subprocess.run(cmd, env=env, text=True, capture_output=True, encoding='utf-8')
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"[❌ 오류] {task_name} 에러:\n{result.stderr}")
            return None
    except Exception as e:
        print(f"[💥 예외] {str(e)}")
        return None

def extract_score(text):
    match = re.search(r"점수\s*[:\[]\s*(\d+)", text)
    return int(match.group(1)) if match else 0

def main():
    parser = argparse.ArgumentParser(description="Gemini 범용 SDLC 파이프라인")
    parser.add_argument("--requirement", "-r", required=True, help="구현할 요구사항을 입력하세요.")
    parser.add_argument("--target_file", "-f", required=True, help="작성하거나 수정할 주요 파일명을 입력하세요.")
    args = parser.parse_args()

    print(f"📌 [목표] {args.target_file} 파일을 기반으로 다음 기능을 구현합니다: {args.requirement}")

    # 1. Planning 단계
    plan_prompt = f"[Planner] 요구사항 '{args.requirement}'를 달성하기 위해 {args.target_file}을 어떻게 수정/작성해야 하는지 상세 TODO와 AC를 설계하라."
    while True:
        plan_out = run_agent(plan_prompt, "Planner", "planner")
        review_out = run_agent("이전 계획의 완성도와 실현 가능성을 평가하고 점수를 매겨라.", "Reviewer", "reviewer")
        score = extract_score(review_out)
        print(f"📍 [Planner 점수] {score}/10")
        if score >= 8: break
        plan_prompt = f"[Planner] Reviewer의 피드백을 반영하여 다시 설계하라:\n{review_out}"

    # 2. Coding 단계
    code_prompt = f"[Coder] 승인된 설계에 따라 {args.target_file} 코드를 완성하라."
    run_agent(code_prompt, "Coder", "coder", approval_mode="auto_edit")
    print(f"📍 [Coder] 코드 구현 완료")

    # 3. Testing 단계
    test_prompt = f"[Tester] 구현된 {args.target_file} 코드가 요구사항 '{args.requirement}'를 완벽히 충족하는지 검증하라."
    while True:
        test_out = run_agent(test_prompt, "Tester", "tester")
        score = extract_score(test_out)
        print(f"📍 [Tester 점수] {score}/10")
        if score >= 8: break
        
        # 수정 요청 루프
        print("⚠️ [Tester] 검증 실패. Coder에게 재수정을 요청합니다.")
        fix_prompt = f"[Coder] Tester의 피드백을 반영하여 {args.target_file}의 버그를 수정하라:\n{test_out}"
        run_agent(fix_prompt, "Coder Fix", "coder", approval_mode="auto_edit")
        test_prompt = "수정된 코드를 다시 검증하라."

    print("\n✅ 모든 파이프라인 공정 성공!")

if __name__ == "__main__":
    main()
