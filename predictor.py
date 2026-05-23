import json
import numpy as np

with open("data/groups.json") as f:
    GROUPS = json.load(f)

with open("data/ratings.json") as f:
    RATINGS = json.load(f)

def win_probability(team_a, team_b):
    """Returns (p_a_wins, p_draw, p_b_wins)"""
    r_a = RATINGS.get(team_a, 60)
    r_b = RATINGS.get(team_b, 60)
    diff = r_a - r_b
    p_a = 1 / (1 + 10 ** (-diff / 30))  # Elo-style formula
    p_draw = 0.25 * (1 - abs(p_a - 0.5) * 2)
    p_a -= p_draw / 2
    p_b = 1 - p_a - p_draw
    return round(p_a, 3), round(p_draw, 3), round(p_b, 3)

def simulate_match(team_a, team_b):
    """Returns winner, or None for draw"""
    p_a, p_draw, p_b = win_probability(team_a, team_b)
    
    # Fix floating point rounding so probs always sum to exactly 1
    total = p_a + p_draw + p_b
    probs = [p_a/total, p_draw/total, p_b/total]
    
    outcome = np.random.choice(["a", "draw", "b"], p=probs)
    if outcome == "a":
        return team_a, team_b, "win"
    elif outcome == "b":
        return team_b, team_a, "win"
    else:
        return None, None, "draw"
def simulate_group(group_name):
    teams = GROUPS[group_name]
    points = {t: 0 for t in teams}
    gd = {t: 0 for t in teams}  # goal difference proxy

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            t_a, t_b = teams[i], teams[j]
            winner, loser, result = simulate_match(t_a, t_b)
            if result == "win":
                points[winner] += 3
                gd[winner] += 1
                gd[loser] -= 1
            else:
                points[t_a] += 1
                points[t_b] += 1

    standings = sorted(teams, key=lambda t: (points[t], gd[t]), reverse=True)
    return standings, points