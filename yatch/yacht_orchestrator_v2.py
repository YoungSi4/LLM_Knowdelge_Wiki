import subprocess
import os
import time

def run_gemini_task(prompt, task_name):
    print(f"\n[🚀 {task_name} 시작]")
    exe = "gemini.cmd" if os.name == "nt" else "gemini"
    cmd = [exe, "-p", prompt, "--approval-mode", "yolo"]
    
    try:
        start_time = time.time()
        # capture_output을 제거하여 gemini의 출력이 실시간으로 터미널에 보이게 함
        result = subprocess.run(cmd, env=os.environ, check=False)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n[✅ {task_name} 완료] (소요시간: {elapsed:.1f}s)")
            return "Success"
        else:
            print(f"\n[❌ {task_name} 실패] 종료 코드: {result.returncode}")
            return None
    except Exception as e:
        print(f"[💥 {task_name} 실행 중 예외 발생]: {str(e)}")
        return None

def main():
    print("=== Yacht Game 개발 오케스트레이션 V2 (Refactoring 포함) ===")

    # 1. Planning (기존 파일 활용 가능하지만 새로 생성)
    run_gemini_task(
        "당신은 Planning 그룹입니다. 'yacht_plan.md'를 더 정교하게 다듬으세요. "
        "특히 주사위 고정 로직과 점수 계산 예외 처리를 강화하세요.", 
        "Planning Group"
    )

    # 2. Implementation
    run_gemini_task(
        "당신은 Implementation 그룹입니다. 'yacht_plan.md'를 바탕으로 'yacht_game.py'를 작성하세요.",
        "Implementation Group"
    )

    # 3. Review
    run_gemini_task(
        "당신은 Review 그룹입니다. 'yacht_game.py'를 리뷰하고 'review_report.md'를 작성하세요. "
        "특히 주사위 정렬(sort)이 고정 인덱스(keep_indices)에 미치는 영향을 집중적으로 체크하세요.",
        "Review Group"
    )

    # 4. Refactoring (추가된 단계)
    refactor_prompt = (
        "당신은 Refactoring 그룹입니다. 'review_report.md'에서 지적된 문제들, "
        "특히 '주사위 정렬로 인한 인덱스 혼동' 문제를 해결하도록 'yacht_game.py'를 수정하세요. "
        "수정 시 주사위 정렬을 제거하거나, 고정된 주사위는 별도로 관리하는 방식을 사용하세요. "
        "수정된 코드를 다시 'yacht_game.py'에 저장하세요."
    )
    run_gemini_task(refactor_prompt, "Refactoring Group")

    print("\n=== V2 오케스트레이션 완료 ===")
    print("개선된 파일: yacht_game.py (버그 수정 완료)")

if __name__ == "__main__":
    main()
