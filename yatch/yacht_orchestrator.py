import subprocess
import os
import time

def run_gemini_task(prompt, task_name):
    print(f"\n[🚀 {task_name} 시작]")
    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    
    # --yolo 모드를 사용하여 각 그룹이 도구(write_file 등)를 승인 없이 사용하도록 함
    cmd = [exe, "-p", prompt, "--approval-mode", "yolo"]
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8")
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[✅ {task_name} 완료] (소요시간: {elapsed:.1f}s)")
            return result.stdout
        else:
            print(f"[❌ {task_name} 실패] 오류 메시지:\n{result.stderr}")
            return None
    except Exception as e:
        print(f"[💥 {task_name} 실행 중 예외 발생]: {str(e)}")
        return None

def main():
    print("=== Yacht Game 개발 오케스트레이션 시작 ===")

    # Stage 1: Planning Group
    plan_prompt = (
        "당신은 Planning 그룹입니다. Yacht(야추) 주사위 게임의 규칙과 시스템 구조를 설계하세요. "
        "결과물은 'yacht_plan.md' 파일로 작성하세요. "
        "포함할 내용: 게임 룰 요약, 필요한 함수 목록, 데이터 구조 설계."
    )
    run_gemini_task(plan_prompt, "Planning Group")

    # Stage 2: Implementation Group
    impl_prompt = (
        "당신은 Implementation 그룹입니다. 'yacht_plan.md' 파일을 읽고, "
        "실제로 플레이 가능한 Python 게임 코드를 작성하세요. "
        "결과물은 'yacht_game.py' 파일로 저장하세요. "
        "CLI 환경에서 주사위를 굴리고 점수판을 채우는 로직이 포함되어야 합니다."
    )
    run_gemini_task(impl_prompt, "Implementation Group")

    # Stage 3: Review Group
    review_prompt = (
        "당신은 Review 그룹입니다. 'yacht_game.py' 코드와 'yacht_plan.md' 설계를 비교 검토하세요. "
        "버그 가능성, 규칙 준수 여부, 코드 품질을 분석하여 'review_report.md'로 작성하세요."
    )
    run_gemini_task(review_prompt, "Review Group")

    print("\n=== 모든 단계가 완료되었습니다. ===")
    print("생성된 파일: yacht_plan.md, yacht_game.py, review_report.md")

if __name__ == "__main__":
    main()
