import streamlit as st
import pandas as pd
import json
from collections import Counter
from predictor import GROUPS, RATINGS
from simulator import run_tournament, simulate_full_bracket, run_multiple_brackets

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="2026 World Cup Predictor",
    page_icon="⚽",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .title-block {
        background: linear-gradient(135deg, #1a472a, #2d6a4f);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
        border: 2px solid #52b788;
    }
    .title-block h1 {
        color: #FFD700;
        font-size: 2.8rem;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
    }
    .title-block p {
        color: #b7e4c7;
        font-size: 1rem;
        margin: 0.5rem 0 0;
    }
    .round-header {
        color: #a78bfa;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 1.5rem 0 0.5rem;
        padding: 0.4rem 1rem;
        background: #1e1b4b;
        border-radius: 8px;
        border-left: 4px solid #7c3aed;
    }
    .stButton > button {
        background: linear-gradient(135deg, #065f46, #047857);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #047857, #059669);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
    <h1>⚽ 2026 FIFA World Cup Predictor</h1>
    <p>Pick your group winners · Simulate the bracket · Crown your champion</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Win Odds Simulator",
    "🗳️ Pick Your Bracket",
    "📋 Groups & Teams",
    "🔁 10 Bracket Runs",
    "🌍 Team Profiles"
])

# ════════════════════════════════════════════════════════════
# TAB 1 — Win Odds Simulator
# ════════════════════════════════════════════════════════════
with tab1:
    st.subheader("🏆 Tournament Win Probabilities")
    st.markdown("Run thousands of simulations to see each team's chance of lifting the trophy.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#111827; border:1px solid #374151; border-radius:12px;
                    padding:1.2rem; text-align:center;">
            <div style="color:#FFD700; font-size:2rem; font-weight:700;">48</div>
            <div style="color:#9ca3af; font-size:0.85rem;">Teams</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#111827; border:1px solid #374151; border-radius:12px;
                    padding:1.2rem; text-align:center;">
            <div style="color:#FFD700; font-size:2rem; font-weight:700;">12</div>
            <div style="color:#9ca3af; font-size:0.85rem;">Groups</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#111827; border:1px solid #374151; border-radius:12px;
                    padding:1.2rem; text-align:center;">
            <div style="color:#FFD700; font-size:2rem; font-weight:700;">104</div>
            <div style="color:#9ca3af; font-size:0.85rem;">Matches</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    n_sims = st.slider(
        "Number of simulations",
        min_value=1000, max_value=50000,
        value=10000, step=1000,
        help="More simulations = more accurate probabilities"
    )

    if st.button("▶ Run Simulations", key="run_sims"):
        with st.spinner(f"Simulating {n_sims:,} tournaments..."):
            results = run_tournament(n_sims)

        st.success(f"Done! Simulated {n_sims:,} tournaments.")

        df = pd.DataFrame(results.items(), columns=["Team", "Win %"])
        df = df[df["Win %"] > 0].sort_values("Win %", ascending=False).reset_index(drop=True)
        df.index += 1

        top3 = df.head(3)
        c1, c2, c3 = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        for i, (col, (_, row)) in enumerate(zip([c1, c2, c3], top3.iterrows())):
            with col:
                st.metric(
                    label=f"{medals[i]} #{i+1}",
                    value=row["Team"],
                    delta=f"{row['Win %']}% chance"
                )

        st.markdown("#### Full Rankings")
        st.bar_chart(df.set_index("Team")["Win %"], height=400)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Win %": st.column_config.ProgressColumn(
                    "Win %",
                    min_value=0,
                    max_value=float(df["Win %"].max()),
                    format="%.1f%%"
                )
            }
        )

# ════════════════════════════════════════════════════════════
# TAB 2 — Bracket Picker
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🗳️ Pick Your Group Stage Winners")
    st.markdown("Select who finishes **1st and 2nd** in each group, then simulate the knockout stage.")

    my_picks = {}
    group_list = list(GROUPS.items())
    cols_per_row = 3

    for row_start in range(0, len(group_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            group_idx = row_start + col_idx
            if group_idx >= len(group_list):
                break
            group_name, teams = group_list[group_idx]
            with col:
                st.markdown(f"**Group {group_name}**")
                first = st.selectbox(
                    f"1st — Group {group_name}",
                    options=teams,
                    key=f"first_{group_name}"
                )
                remaining = [t for t in teams if t != first]
                second = st.selectbox(
                    f"2nd — Group {group_name}",
                    options=remaining,
                    key=f"second_{group_name}"
                )
                my_picks[group_name] = [first, second]
                st.caption(f"✓ {first} & {second} advance")

    st.divider()
    st.subheader("🎯 Simulate Your Bracket")

    if st.button("⚡ Simulate Knockout Stage", key="run_bracket"):
        with st.spinner("Simulating your bracket..."):
            bracket_history, champion = simulate_full_bracket(my_picks)

        st.success(f"🏆 Your World Cup Champion: **{champion}**")
        st.balloons()

        st.subheader("📜 Full Bracket Results")
        for round_data in bracket_history:
            st.markdown(f"### ⚽ {round_data['round']}")
            r_cols = st.columns(2)
            for i, match in enumerate(round_data["matchups"]):
                with r_cols[i % 2]:
                    if match["winner"] == match["team_a"]:
                        st.success(f"**{match['team_a']}** vs {match['team_b']} → ✓ {match['winner']}")
                    else:
                        st.success(f"{match['team_a']} vs **{match['team_b']}** → ✓ {match['winner']}")

        st.info("💡 Results are randomised using team strength ratings. Run again for a different outcome!")

# ════════════════════════════════════════════════════════════
# TAB 3 — Groups & Teams
# ════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📋 All 12 Groups — 2026 FIFA World Cup")
    st.caption("Green bar shows FIFA strength rating. Top 2 in each group advance automatically.")

    st.divider()

    for row_start in range(0, len(group_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            group_idx = row_start + col_idx
            if group_idx >= len(group_list):
                break
            group_name, teams = group_list[group_idx]
            with col:
                st.markdown(f"**Group {group_name}**")
                for i, team in enumerate(teams):
                    rating = RATINGS.get(team, 60)
                    label = f"⚽ {team}" if i < 2 else f"　 {team}"
                    st.text(label)
                    st.progress(rating / 100, text=f"{rating}/100")
                st.divider()

# ════════════════════════════════════════════════════════════
# TAB 4 — Run Multiple Brackets & Compare
# ════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🔁 Run Multiple Brackets & Compare")
    st.markdown("Simulate your bracket picks multiple times and see which teams consistently go deep.")
    st.info("👆 First make your group picks in the **Pick Your Bracket** tab, then come back here.")

    n_runs = st.slider("Number of runs", min_value=5, max_value=50, value=10, step=5)

    if st.button("🔁 Run Multiple Simulations", key="multi_sim"):
        current_picks = {}
        for group_name, teams in GROUPS.items():
            first_key = f"first_{group_name}"
            second_key = f"second_{group_name}"
            if first_key in st.session_state and second_key in st.session_state:
                current_picks[group_name] = [
                    st.session_state[first_key],
                    st.session_state[second_key]
                ]
            else:
                sorted_teams = sorted(teams, key=lambda t: RATINGS.get(t, 60), reverse=True)
                current_picks[group_name] = sorted_teams[:2]

        with st.spinner(f"Running {n_runs} simulations..."):
            summary, champions = run_multiple_brackets(current_picks, n=n_runs)

        # Champion frequency
        champ_counts = Counter(champions)
        st.markdown("### 🏆 Champion Frequency")
        champ_df = pd.DataFrame(champ_counts.items(), columns=["Team", "Times Won"])
        champ_df = champ_df.sort_values("Times Won", ascending=False).reset_index(drop=True)
        champ_df.index += 1

        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(champ_df, use_container_width=True)
        with c2:
            st.bar_chart(champ_df.set_index("Team")["Times Won"])

        # Deep runs table
        st.markdown("### 📈 How Far Did Each Team Go?")
        round_order = [
            "Round of 32", "Round of 16",
            "Quarter-Finals", "Semi-Finals", "Final", "Champion"
        ]

        rows = []
        for team, round_counts in summary.items():
            if round_counts:
                best_round = max(
                    round_counts.keys(),
                    key=lambda r: round_order.index(r) if r in round_order else -1
                )
                deep_runs = (
                    round_counts.get("Semi-Finals", 0) +
                    round_counts.get("Final", 0) +
                    round_counts.get("Champion", 0)
                )
                rows.append({
                    "Team": team,
                    "Best Round": best_round,
                    "Deep Runs (SF+)": deep_runs
                })

        reach_df = pd.DataFrame(rows)
        reach_df = reach_df[reach_df["Deep Runs (SF+)"] > 0].sort_values(
            "Deep Runs (SF+)", ascending=False
        ).reset_index(drop=True)
        reach_df.index += 1

        if not reach_df.empty:
            st.dataframe(reach_df, use_container_width=True)
        else:
            st.warning("No teams reached the Semi-Finals across these runs. Try more runs!")

# ════════════════════════════════════════════════════════════
# TAB 5 — Team Profiles
# ════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🌍 Team Profile Cards")

    try:
        with open("data/team_profiles.json", encoding="utf-8") as f:
            profiles = json.load(f)
    except FileNotFoundError:
        st.error("team_profiles.json not found in data/ folder.")
        profiles = {}

    if profiles:
        all_team_names = sorted(profiles.keys())
        selected_team = st.selectbox("Select a team", all_team_names)

        if selected_team and selected_team in profiles:
            p = profiles[selected_team]
            rating = RATINGS.get(selected_team, 60)

            # Find group
            team_group = "?"
            for g, teams in GROUPS.items():
                if selected_team in teams:
                    team_group = g
                    break

            wc_won = p.get("world_cups_won", 0)
            wc_display = "🏆 " * wc_won if wc_won > 0 else "None"

            st.divider()

            # Header
            flag = p.get("flag", "🏳️")
            nickname = p.get("nickname", "")
            st.title(f"{flag}  {selected_team}")
            st.caption(f"{nickname}  ·  Group {team_group}")

            st.divider()

            # Stats
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Confederation", p.get("confederation", "—"))
            c2.metric("Head Coach", p.get("coach", "—"))
            c3.metric("World Cups Won", wc_won)
            c4.metric("Strength Rating", f"{rating}/100")

            st.divider()

            # Strength bar
            st.markdown("**Strength Rating**")
            st.progress(rating / 100)

            st.divider()

            # Key players
            st.markdown("**Key Players**")
            players = p.get("key_players", [])
            if players:
                p_cols = st.columns(len(players))
                for i, player in enumerate(players):
                    with p_cols[i]:
                        st.success(f"⚽ {player}")