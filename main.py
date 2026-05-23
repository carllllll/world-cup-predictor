from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from simulator import run_tournament
from predictor import simulate_group, GROUPS

console = Console()

def show_group_predictions():
    console.print(Panel.fit("⚽ 2026 FIFA WORLD CUP PREDICTOR", style="bold yellow"))
    console.print("\n[bold cyan]GROUP STAGE PREDICTIONS[/bold cyan]\n")

    for group_name in GROUPS:
        standings, points = simulate_group(group_name)
        table = Table(title=f"Group {group_name}", box=box.SIMPLE_HEAVY)
        table.add_column("Pos", style="bold")
        table.add_column("Team")
        table.add_column("Points", justify="right")

        for i, team in enumerate(standings):
            style = "green" if i < 2 else "dim"
            table.add_row(str(i+1), team, str(points[team]), style=style)

        console.print(table)

def show_winner_odds(n=10000):
    console.print(f"\n[bold cyan]RUNNING {n:,} TOURNAMENT SIMULATIONS...[/bold cyan]\n")
    results = run_tournament(n)

    table = Table(title="🏆 World Cup Winner Probabilities", box=box.ROUNDED)
    table.add_column("Rank", style="bold yellow")
    table.add_column("Team", style="bold")
    table.add_column("Win %", justify="right")
    table.add_column("Chance", style="green")

    for rank, (team, pct) in enumerate(list(results.items())[:15], 1):
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        bar = bar[:20]
        table.add_row(str(rank), team, f"{pct}%", bar)

    console.print(table)

if __name__ == "__main__":
    show_group_predictions()
    show_winner_odds(n=10000)