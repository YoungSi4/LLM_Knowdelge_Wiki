import random
import re

class YachtGame:
    def __init__(self):
        # 12개의 점수 카테고리 정의
        self.categories = [
            "Aces", "Twos", "Threes", "Fours", "Fives", "Sixes",
            "Choice", "4 of a Kind", "Full House", "S. Straight", "L. Straight", "Yacht"
        ]
        # 점수판 초기화 (None은 아직 기록되지 않음을 의미)
        self.scoreboard = {cat: None for cat in self.categories}
        
        # [Refactoring] 주사위와 고정 상태를 하나의 리스트(딕셔너리 구조)로 관리
        # 인덱스 혼동을 방지하기 위해 이 리스트의 원본 순서는 절대 변경(sort)하지 않음.
        self.dice = [{"value": 0, "kept": False} for _ in range(5)]
        
        self.rolls_left = 3
        self.current_round = 1

    def roll_dice(self):
        """고정(kept)되지 않은 주사위만 갱신 (1~6 랜덤)"""
        for die in self.dice:
            if not die["kept"]:
                die["value"] = random.randint(1, 6)

    def update_keep(self, input_str):
        """
        정규식을 활용하여 입력 문자열에서 숫자만 추출하고, 
        해당 인덱스의 고정 상태를 반전(Toggle)시킵니다.
        """
        numbers = re.findall(r'[1-5]', input_str)
        unique_indices = set(map(int, numbers))
        
        if not unique_indices and input_str.strip():
            print(">>> [알림] 유효한 주사위 번호(1-5)가 감지되지 않았습니다.")
            return

        for idx in unique_indices:
            # 1-based to 0-based
            self.dice[idx-1]["kept"] = not self.dice[idx-1]["kept"]
        
        kept_count = sum(1 for d in self.dice if d["kept"])
        if kept_count > 0:
            print(f">>> [고정 업데이트] 현재 {kept_count}개의 주사위가 고정되었습니다.")

    def calculate_scores(self, dice_values):
        """현재 주사위 값 리스트를 입력받아 12개 카테고리의 가능한 점수를 리턴"""
        counts = [dice_values.count(i) for i in range(1, 7)]
        dice_sum = sum(dice_values)
        # 판정을 위해 정렬된 복사본 사용 (원본 self.dice 영향 없음)
        unique_dice = sorted(list(set(dice_values)))
        
        scores = {}
        scores["Aces"] = dice_values.count(1) * 1
        scores["Twos"] = dice_values.count(2) * 2
        scores["Threes"] = dice_values.count(3) * 3
        scores["Fours"] = dice_values.count(4) * 4
        scores["Fives"] = dice_values.count(5) * 5
        scores["Sixes"] = dice_values.count(6) * 6
        scores["Choice"] = dice_sum
        scores["4 of a Kind"] = dice_sum if any(c >= 4 for c in counts) else 0
        
        is_full_house = (3 in counts and 2 in counts) or (5 in counts)
        scores["Full House"] = dice_sum if is_full_house else 0
        
        is_s_straight = False
        s_straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        dice_set = set(dice_values)
        for ss in s_straights:
            if ss.issubset(dice_set):
                is_s_straight = True
                break
        scores["S. Straight"] = 15 if is_s_straight else 0
        
        is_l_straight = (len(unique_dice) == 5 and (unique_dice == [1, 2, 3, 4, 5] or unique_dice == [2, 3, 4, 5, 6]))
        scores["L. Straight"] = 30 if is_l_straight else 0
        scores["Yacht"] = 50 if 5 in counts else 0
        
        return scores

    def get_sections_scores(self):
        """상단 섹션 합계, 보너스, 총점을 계산"""
        upper_scores = [self.scoreboard[cat] for cat in self.categories[:6] if self.scoreboard[cat] is not None]
        upper_sum = sum(upper_scores)
        bonus = 35 if upper_sum >= 63 else 0
        
        lower_scores = [self.scoreboard[cat] for cat in self.categories[6:] if self.scoreboard[cat] is not None]
        lower_sum = sum(lower_scores)
        
        total = upper_sum + bonus + lower_sum
        return upper_sum, bonus, lower_sum, total

    def display_board(self, show_potential=True):
        """현재 점수판, 주사위(고정 상태 시각화), 예상 점수 등을 출력"""
        upper_sum, bonus, lower_sum, total = self.get_sections_scores()
        dice_values = [d["value"] for d in self.dice]
        potential = self.calculate_scores(dice_values)
        
        print("\n" + "╔" + "═"*50 + "╗")
        print(f"║  ROUND {self.current_round:2}/12   주사위 기회: {self.rolls_left}/3   TOTAL: {total:3} ║")
        print("╠" + "═"*50 + "╣")
        
        # [Refactoring] 주사위 상태 시각화 (인덱스 고정 유지)
        dice_display = []
        for d in self.dice:
            val = d["value"]
            dice_display.append(f"[{val}]" if d["kept"] else f" {val} ")
        
        print(f"║ 주사위: {' '.join(dice_display)}  (번호:  1   2   3   4   5 ) ║")
        print("╟" + "─"*50 + "╢")
        print("║ [ID] 카테고리       [점수]      [기록 시 예상]     ║")
        
        for i, cat in enumerate(self.categories):
            score_val = self.scoreboard[cat]
            score_str = str(score_val) if score_val is not None else "-"
            potential_str = f"({potential[cat]})" if (score_val is None and show_potential) else ""
            
            print(f"║ {i+1:2}. {cat:12} : {score_str:8} {potential_str:15} ║")
            
            if cat == "Sixes":
                bonus_status = "OK" if upper_sum >= 63 else f"{upper_sum}/63"
                print("╟" + "─"*50 + "╢")
                print(f"║    상단 합계 : {upper_sum:3}/63   (보너스 +35: {bonus_status})     ║")
                print("╟" + "─"*50 + "╢")
        
        print("╚" + "═"*50 + "╝")

    def play(self):
        """메인 게임 루프"""
        print("\n" + "★"*25)
        print("   Yacht Dice Game v2.1 (Refactored)   ")
        print("★"*25)
        print("- 주사위 번호를 입력하여 '고정(Keep)'하거나 '해제'할 수 있습니다.")
        print("- 's' 또는 'skip'을 입력하면 남은 기회와 상관없이 점수를 기록합니다.")
        print("- 'exit' 또는 'quit'를 입력하여 게임을 종료할 수 있습니다.")
        
        while self.current_round <= 12:
            self.rolls_left = 3
            # 라운드 시작 시 모든 주사위 고정 해제
            for d in self.dice:
                d["kept"] = False
            
            # 1. 주사위 굴리기 및 고정 단계
            while self.rolls_left > 0:
                print(f"\n>>> {3 - self.rolls_left + 1}번째 주사위를 굴립니다...")
                self.roll_dice()
                self.rolls_left -= 1
                
                if self.rolls_left > 0:
                    while True:
                        self.display_board()
                        prompt = "고정/해제할 주사위 번호 입력 (예: 1 3 5), 또는 's'로 확정: "
                        user_input = input(prompt).strip().lower()
                        
                        if user_input in ['exit', 'quit']:
                            print("\n게임을 종료합니다. 이용해주셔서 감사합니다.")
                            return
                        
                        if user_input in ['s', 'skip']:
                            self.rolls_left = 0
                            break
                        
                        self.update_keep(user_input)
                        break
                else:
                    self.display_board()
                    print("모든 주사위 기회를 사용했습니다.")
            
            # 2. 점수 기록 단계
            while True:
                try:
                    choice_str = input(f"\n점수를 기록할 카테고리 번호(1-12)를 선택하세요: ").strip().lower()
                    if choice_str in ['exit', 'quit']:
                        print("\n게임을 종료합니다. 이용해주셔서 감사합니다.")
                        return
                    
                    if not choice_str:
                        continue
                        
                    choice = int(choice_str)
                    if 1 <= choice <= 12:
                        category = self.categories[choice - 1]
                        if self.scoreboard[category] is not None:
                            print(f">>> [오류] '{category}'는 이미 기록된 항목입니다. 다시 선택해주세요.")
                        else:
                            dice_values = [d["value"] for d in self.dice]
                            potential_scores = self.calculate_scores(dice_values)
                            recorded_score = potential_scores[category]
                            self.scoreboard[category] = recorded_score
                            print(f"\n>>> [{category}]에 {recorded_score}점을 기록했습니다!")
                            break
                    else:
                        print(">>> [오류] 1에서 12 사이의 번호를 입력해주세요.")
                except ValueError:
                    print(">>> [오류] 올바른 숫자를 입력하거나 'exit'를 입력하세요.")
            
            self.current_round += 1

        # 3. 게임 종료 및 최종 결과
        _, _, _, final_total = self.get_sections_scores()
        print("\n" + "█"*52)
        print("█" + " "*20 + "GAME OVER" + " "*20 + "█")
        print("█"*52)
        self.display_board(show_potential=False)
        
        rank = "Diamond" if final_total >= 250 else "Platinum" if final_total >= 200 else "Gold" if final_total >= 150 else "Silver"
        print(f"\n최종 점수: {final_total}점")
        print(f"당신의 랭크: {rank}")
        print("플레이해주셔서 감사합니다!")

if __name__ == "__main__":
    game = YachtGame()
    game.play()
