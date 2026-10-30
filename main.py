import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch
from statsbombpy import sb

BG, BLUE, PINK, YELLOW = '#0d1117', '#38bdf8', '#f43f5e', '#eef916'


def name_of(v):
    if isinstance(v, dict):
        return v.get('name')
    if isinstance(v, str) and v not in ('', 'nan', 'None'):
        return v
    return None


def squad_block(players, minutes, arrow):
    return ''.join(
        f" #{str(jersey.get(p, '--')).ljust(2)} {p}"
        + (f"  {arrow}{minutes[p]}'" if p in minutes else '') + "\n"
        for p in players
    )


print("=== STATSBOMB PASSING NETWORK & MATCH ANALYSIS TOOL ===")

competitions = sb.competitions()
print("\n--- Available Competitions and Leagues ---")
for idx, row in competitions.iterrows():
    print(f"[{idx}] {row['competition_name']} ({row['season_name']})")

comp = competitions.iloc[int(input("\nEnter the index number of the competition you want to explore: "))]
print(f"\n>> Loading matches for {comp['competition_name']} ({comp['season_name']}), please wait...")

matches = sb.matches(competition_id=comp['competition_id'], season_id=comp['season_id'])
print(f"\n--- {comp['competition_name']} Match List & IDs ---\n" + "-" * 80)
for _, m in matches.iterrows():
    print(f"Match ID: {m['match_id']} | {m['match_date']} -> {m['home_team']} vs {m['away_team']}")
print("-" * 80)

match_id = int(input("\nEnter the Match ID you want to analyze from the list above: "))

try:
    print(f"\nLoading match data for Match ID {match_id}...")
    events = sb.events(match_id=match_id)
    lineups = sb.lineups(match_id=match_id)
except Exception as e:
    print(f"Error: Could not load match data. Details: {e}")
    exit()

teams = list(lineups.keys())
print("\nTeams in this match:")
for i, t in enumerate(teams, 1):
    print(f"[{i}] {t}")
team_name = teams[int(input("\nEnter the number of the team you want to analyze (1 or 2): ")) - 1]
print(f"\nSelected Team: {team_name} | Preparing passing network analysis...")

squad = lineups[team_name]
jersey = dict(zip(squad['player_name'], squad['jersey_number']))

team_events = events[events['team'] == team_name]

starting_players = [
    p['player']['name']
    for tactics in team_events.loc[team_events['type'] == 'Starting XI', 'tactics']
    if isinstance(tactics, dict)
    for p in tactics.get('lineup', [])
]
bench_players = [p for p in squad['player_name'] if p not in starting_players]

sub_in_minutes, sub_out_minutes = {}, {}
for _, row in team_events[team_events['type'] == 'Substitution'].iterrows():
    p_off = name_of(row.get('player'))
    p_on = name_of(row.get('substitution_replacement'))
    if p_on is None and isinstance(row.get('substitution'), dict):
        p_on = name_of(row['substitution'].get('replacement'))
    if p_off:
        sub_out_minutes[p_off] = row['minute']
    if p_on:
        sub_in_minutes[p_on] = row['minute']

actual_sub_played = list(sub_in_minutes)

passes = team_events[(team_events['type'] == 'Pass') & team_events['pass_outcome'].isna()].copy()
passes[['x', 'y']] = pd.DataFrame(
    passes['location'].apply(lambda l: l if isinstance(l, list) else [np.nan, np.nan]).tolist(),
    index=passes.index,
)
passes['player'] = passes['player'].apply(name_of)
passes['pass_recipient'] = passes['pass_recipient'].apply(name_of)

average_locs = passes.groupby('player').agg(x=('x', 'mean'), y=('y', 'mean'), count=('x', 'count'))

pass_between = (passes.groupby(['player', 'pass_recipient']).size()
                .reset_index(name='pass_count')
                .merge(average_locs[['x', 'y']], left_on='player', right_index=True)
                .merge(average_locs[['x', 'y']], left_on='pass_recipient', right_index=True,
                       suffixes=('', '_end')))

fig = plt.figure(figsize=(16, 9), facecolor=BG)
ax = fig.add_axes([0.05, 0.1, 0.62, 0.8])
pitch = Pitch(pitch_type='statsbomb', pitch_color=BG, line_color=BLUE)
pitch.draw(ax=ax)

pitch.lines(pass_between['x'], pass_between['y'], pass_between['x_end'], pass_between['y_end'],
            lw=pass_between['pass_count'] * 0.2, color=BLUE, alpha=0.6, ax=ax)

for players, color in [(starting_players, PINK), (actual_sub_played, YELLOW)]:
    locs = average_locs[average_locs.index.isin(players)]
    if not locs.empty:
        pitch.scatter(locs['x'], locs['y'], s=np.maximum(locs['count'] * 12, 350),
                      color=color, edgecolors='white', linewidth=1.5, alpha=0.9, ax=ax, zorder=3)

for player, row in average_locs.iterrows():
    pitch.annotate(str(jersey.get(player, "")), xy=(row['x'], row['y']), c='white',
                   va='center', ha='center', fontsize=10, weight='bold', ax=ax, zorder=4)

ax_text = fig.add_axes([0.68, 0.08, 0.28, 0.84])
ax_text.set_facecolor('#161b22')
ax_text.axis('off')

lineup_text = (f"{team_name} - Match Squad\n" + "-" * 32 + "\n\n[Starting XI]\n"
               + squad_block(starting_players, sub_out_minutes, '<-')
               + "\n[Substitutes]\n"
               + squad_block(bench_players, sub_in_minutes, '->'))
ax_text.text(0.05, 0.96, lineup_text, color='white', fontsize=7.5,
             family='monospace', va='top', transform=ax_text.transAxes)

plt.suptitle(f'Passing Network & Lineup - {team_name} (Match ID: {match_id})',
             fontsize=16, color=BLUE, y=0.95)

output_filename = f"passing_network_lineup_{team_name.replace(' ', '_').lower()}.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight', facecolor=BG)
plt.close()

print(f"\nSuccess! Analysis graph successfully saved as '{output_filename}'.")