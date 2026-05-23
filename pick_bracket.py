from rich.console import Console
from rich.prompt import Prompt
from predictor import GROUPS, simulate_match

console = Console()

def pick_group_winners():
    my_picks = {}

    console.print("\n[bold yellow]⚽ PICK YOUR GROUP WINNERS[/bold yellow]\n")

    for group_name, teams in GROUPS.items():
        console.print(f"\n[bold cyan]Group {group_name}:[/bold cyan]")
        for i, team in enumerate(teams, 1):
            console.print(f"  {i}. {team}")

        while True:
            pick1 = Prompt.ask(f"  Who wins Group {group_name}? (1-4)")
            pick2 = Prompt.ask(f"  Who finishes 2nd? (1-4)")
            if pick1.isdigit() and pick2.isdigit():
                p1, p2 = int(pick1)-1, int(pick2)-1
                if 0 <= p1 <= 3 and 0 <= p2 <= 3 and p1 != p2:
                    my_picks[group_name] = [teams[p1], teams[p2]]
                    console.print(f"  [green]✓ {teams[p1]} & {teams[p2]} advance[/green]")
                    break
            console.print("  [red]Invalid input, try again[/red]")

    return my_picks

def simulate_my_bracket(my_picks):
    console.print("\n[bold yellow]🏆 SIMULATING YOUR BRACKET...[/bold yellow]\n")

    advancing = []
    for group_name, top2 in my_picks.items():
        advancing.extend(top2)

    import random
    random.shuffle(advancing)

    round_names = ["Round of 32", "Round of 16", "Quarter-Finals",
                   "Semi-Finals", "Final"]
    round_idx = 0

    while len(advancing) > 1:
        console.print(f"[bold magenta]--- {round_names[min(round_idx, 4)]} ---[/bold magenta]")
        next_round = []
        for i in range(0, len(advancing), 2):
            if i + 1 < len(advancing):
                t_a, t_b = advancing[i], advancing[i+1]
                winner, _, result = simulate_match(t_a, t_b)
                if result == "draw":
                    winner = random.choice([t_a, t_b])
                console.print(f"  {t_a} vs {t_b}  →  [green]{winner}[/green]")
                next_round.append(winner)
        advancing = next_round
        round_idx += 1
        console.print()

    console.print(f"\n[bold yellow]🏆 YOUR WORLD CUP WINNER: {advancing[0].upper()} 🏆[/bold yellow]\n")

if __name__ == "__main__":
    picks = pick_group_winners()
    simulate_my_bracket(picks)