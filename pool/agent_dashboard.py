import os
import json
import time
import glob
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from datetime import datetime

class AgentDashboard:
    def __init__(self, pool_path="pool"):
        self.pool_path = pool_path
        self.console = Console()
        self.agents = {}
        self.logs_path = os.path.join(pool_path, "logs")
        if not os.path.exists(self.logs_path):
            os.makedirs(self.logs_path)

    def scan_agents(self):
        """pool 디렉토리 내의 모든 JSON 에이전트 파일을 스캔합니다."""
        json_files = glob.glob(os.path.join(self.pool_path, "*.json"))
        current_agent_ids = []
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    agent_id = data.get("id")
                    if agent_id:
                        current_agent_ids.append(agent_id)
                        if agent_id not in self.agents:
                            self.agents[agent_id] = {
                                "role": data.get("role", "N/A"),
                                "status": "idle",
                                "round": 0,
                                "last_output": "N/A",
                                "file_path": file_path
                            }
                        # 상태 파일 업데이트 확인
                        self.update_agent_status(agent_id)
            except Exception:
                continue
        
        # 삭제된 에이전트 제거
        for agent_id in list(self.agents.keys()):
            if agent_id not in current_agent_ids:
                del self.agents[agent_id]

    def update_agent_status(self, agent_id):
        """에이전트별 상태 파일(.status)을 읽어 현재 상태를 업데이트합니다."""
        status_file = os.path.join(self.logs_path, f"{agent_id}.status")
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    self.agents[agent_id]["status"] = status_data.get("status", "idle")
                    self.agents[agent_id]["round"] = status_data.get("round", 0)
                    self.agents[agent_id]["last_output"] = status_data.get("last_output", "N/A")
            except Exception:
                pass

    def generate_table(self) -> Table:
        """현재 에이전트 상태를 기반으로 리치 테이블을 생성합니다."""
        table = Table(title=f"🤖 [bold blue]Gemini Agent Pool Dashboard[/bold blue] ({datetime.now().strftime('%H:%M:%S')})", 
                      show_header=True, header_style="bold magenta", expand=True)
        
        table.add_column("Agent ID", style="cyan", no_wrap=True)
        table.add_column("Role", style="green")
        table.add_column("Status", justify="center")
        table.add_column("Round", justify="right", style="yellow")
        table.add_column("Last Output Summary", style="dim")

        status_colors = {
            "idle": "grey50",
            "running": "bold reverse green",
            "completed": "bold blue",
            "failed": "bold red"
        }

        for agent_id, info in self.agents.items():
            status = info["status"]
            color = status_colors.get(status, "white")
            
            table.add_row(
                agent_id,
                info["role"],
                f"[{color}]{status.upper()}[/{color}]",
                str(info["round"]),
                info["last_output"][:50] + "..." if len(info["last_output"]) > 50 else info["last_output"]
            )
        return table

    def run(self):
        """대시보드를 실시간으로 갱신하며 실행합니다."""
        self.scan_agents()  # 초기 스캔 수행
        with Live(self.generate_table(), refresh_per_second=1) as live:
            while True:
                self.scan_agents()
                live.update(self.generate_table())
                time.sleep(1)

if __name__ == "__main__":
    dashboard = AgentDashboard()
    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
