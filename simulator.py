from predictor import simulate_group, simulate_match, GROUPS
import random

def run_tournament(n_simulations=10000):
    win_counts = {team: 0 for group in GROUPS.values() for team in group}

    for _ in range(n_simulations):
        group_results = {}
        third_place_teams = []

        for group_name in GROUPS:
            standings, points = simulate_group(group_name)
            group_results[group_name] = standings
            third_place_teams.append((standings[2], points[standings[2]]))

        third_place_teams.sort(key=lambda x: x[1], reverse=True)
        advancing_third = [t[0] for t in third_place_teams[:8]]

        round_of_32 = []
        for standings in group_results.values():
            round_of_32.append(standings[0])
            round_of_32.append(standings[1])
        round_of_32 += advancing_third
        random.shuffle(round_of_32)

        def play_knockout_round(teams):
            next_round = []
            for i in range(0, len(teams), 2):
                if i + 1 < len(teams):
                    winner, _, result = simulate_match(teams[i], teams[i+1])
                    if result == "draw":
                        winner = random.choice([teams[i], teams[i+1]])
                    next_round.append(winner)
            return next_round

        current_round = round_of_32[:]
        while len(current_round) > 1:
            current_round = play_knockout_round(current_round)

        if current_round:
            win_counts[current_round[0]] += 1

    results = {team: round(count / n_simulations * 100, 1)
               for team, count in win_counts.items()}
    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))


def simulate_full_bracket(picks):
    """
    Takes a dict of {group: [1st, 2nd]} picks and simulates
    the full knockout stage, returning each round's results.
    """
    # Build full list of 24 teams from picks
    advancing = []
    for top2 in picks.values():
        advancing.extend(top2)

    # Should be exactly 24 teams (12 groups x 2)
    # Add 8 simulated best third-place teams to make 32
    all_teams = [team for group in GROUPS.values() for team in group]
    picked = set(advancing)
    third_place_pool = [t for t in all_teams if t not in picked]

    # Pick 8 random third-place teams weighted by rating
    from predictor import RATINGS
    weights = [RATINGS.get(t, 60) for t in third_place_pool]
    total_w = sum(weights)
    norm_weights = [w / total_w for w in weights]

    import numpy as np
    third_place_picks = list(np.random.choice(
        third_place_pool,
        size=8,
        replace=False,
        p=norm_weights
    ))

    advancing = advancing + third_place_picks  # now exactly 32
    random.shuffle(advancing)

    # Verify we have exactly 32
    assert len(advancing) == 32, f"Expected 32 teams, got {len(advancing)}"

    round_names = [
        "Round of 32", "Round of 16",
        "Quarter-Finals", "Semi-Finals", "Final"
    ]
    bracket_history = []
    round_idx = 0

    while len(advancing) > 1:
        round_label = round_names[min(round_idx, len(round_names) - 1)]
        matchups = []
        next_round = []

        for i in range(0, len(advancing), 2):
            if i + 1 < len(advancing):
                t_a, t_b = advancing[i], advancing[i + 1]
                winner, _, result = simulate_match(t_a, t_b)
                if result == "draw":
                    winner = random.choice([t_a, t_b])
                matchups.append({
                    "team_a": t_a,
                    "team_b": t_b,
                    "winner": winner
                })
                next_round.append(winner)

        bracket_history.append({
            "round": round_label,
            "matchups": matchups
        })
        advancing = next_round
        round_idx += 1

    champion = advancing[0] if advancing else "Unknown"
    return bracket_history, champion
def run_multiple_brackets(picks, n=10):
    """
    Runs n bracket simulations and tracks how far each team goes.
    Returns round_reach dict and list of champions.
    """
    round_order = [
        "Round of 32", "Round of 16",
        "Quarter-Finals", "Semi-Finals", "Final", "Champion"
    ]

    round_reach = {team: [] for group in GROUPS.values() for team in group}
    champions = []

    for _ in range(n):
        bracket_history, champion = simulate_full_bracket(picks)
        champions.append(champion)

        # Track every team's furthest round
        reached = {}
        for round_data in bracket_history:
            for match in round_data["matchups"]:
                # Both teams reached this round
                for team in [match["team_a"], match["team_b"]]:
                    reached[team] = round_data["round"]
                # Winner goes further
                reached[match["winner"]] = round_data["round"]

        # Champion gets special label
        reached[champion] = "Champion"

        for team, rd in reached.items():
            if team in round_reach:
                round_reach[team].append(rd)

    # Summarise: count how many times each team reached each round
    summary = {}
    for team, rounds in round_reach.items():
        if rounds:
            counts = {r: rounds.count(r) for r in round_order if rounds.count(r) > 0}
            summary[team] = counts

    return summary, champions