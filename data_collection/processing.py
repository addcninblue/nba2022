import pandas as pd
import csv


def calc_time_seconds(quarter, time_remaining):
    time_remaining, _ = time_remaining.split(".")  # Take off unused .0 ?
    minutes, seconds = time_remaining.split(":")
    minutes = int(minutes)
    seconds = int(seconds)
    return (quarter-1) * 12 * 60 + (12 * 60 - (minutes * 60 + seconds))


def calc_quarter_time_remaining(seconds):
    quarter = seconds // (12 * 60)
    seconds = 12*60 - seconds % (12 * 60)
    minutes = seconds // 60
    seconds = seconds % 60
    return quarter, minutes, seconds


# https://stackoverflow.com/a/60544597
def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def generate_event(
        gsw_roster_0, gsw_roster_1, gsw_roster_2, gsw_roster_3, gsw_roster_4,
        bos_roster_0, bos_roster_1, bos_roster_2, bos_roster_3, bos_roster_4,
        gsw_score_norm48, bos_score_norm48, time_elapsed, time_ending,
        is_gsw_home
        ):
    if is_gsw_home:
        home_roster_0, home_roster_1, home_roster_2, home_roster_3, home_roster_4 = gsw_roster_0, gsw_roster_1, gsw_roster_2, gsw_roster_3, gsw_roster_4
        away_roster_0, away_roster_1, away_roster_2, away_roster_3, away_roster_4 = bos_roster_0, bos_roster_1, bos_roster_2, bos_roster_3, bos_roster_4
        home_score_norm48 = gsw_score_norm48
        away_score_norm48 = bos_score_norm48
    else:
        home_roster_0, home_roster_1, home_roster_2, home_roster_3, home_roster_4 = bos_roster_0, bos_roster_1, bos_roster_2, bos_roster_3, bos_roster_4
        away_roster_0, away_roster_1, away_roster_2, away_roster_3, away_roster_4 = gsw_roster_0, gsw_roster_1, gsw_roster_2, gsw_roster_3, gsw_roster_4
        home_score_norm48 = bos_score_norm48
        away_score_norm48 = gsw_score_norm48
    return {
            "HOME_ROSTER_0": home_roster_0,
            "HOME_ROSTER_1": home_roster_1,
            "HOME_ROSTER_2": home_roster_2,
            "HOME_ROSTER_3": home_roster_3,
            "HOME_ROSTER_4": home_roster_4,
            "AWAY_ROSTER_0": away_roster_0,
            "AWAY_ROSTER_1": away_roster_1,
            "AWAY_ROSTER_2": away_roster_2,
            "AWAY_ROSTER_3": away_roster_3,
            "AWAY_ROSTER_4": away_roster_4,
            "HOME_SCORE_NORM48": home_score_norm48,
            "AWAY_SCORE_NORM48": away_score_norm48,
            "TIME_ELAPSED": time_elapsed,
            "TIME_ENDING": time_ending,
            }


playoff_games = [
        "2022-06-02",
        "2022-06-05",
        "2022-06-08",
        "2022-06-10",
        "2022-06-13",
        ]

gsw_home = [True, True, False, False, True]

data = [pd.read_csv(f"{game}.csv") for game in playoff_games]

gsw_starting_lineups = [
        set(["S. Curry", "D. Green", "K. Looney", "K. Thompson", "A. Wiggins"]),
        set(["S. Curry", "D. Green", "K. Looney", "K. Thompson", "A. Wiggins"]),
        set(["S. Curry", "D. Green", "K. Looney", "K. Thompson", "A. Wiggins"]),
        set(["S. Curry", "D. Green", "O. Porter", "K. Thompson", "A. Wiggins"]),
        ]

bos_starting_lineups = [
        set(["J. Brown", "A. Horford", "M. Smart", "J. Tatum", "R. Williams"]),
        set(["J. Brown", "A. Horford", "M. Smart", "J. Tatum", "R. Williams"]),
        set(["J. Brown", "A. Horford", "M. Smart", "J. Tatum", "R. Williams"]),
        set(["J. Brown", "A. Horford", "M. Smart", "J. Tatum", "R. Williams"]),
        ]


# date = playoff_games[2]
# day = data[2]
# gsw_lineup = gsw_starting_lineups[2]
# bos_lineup = bos_starting_lineups[2]
# print(date)

all_events = []

for date, day, gsw_lineup, bos_lineup, is_gsw_home in zip(playoff_games, data, gsw_starting_lineups, bos_starting_lineups, gsw_home):
    gsw_player_swap_actions = day["GOLDEN STATE_ACTION"][day["GOLDEN STATE_ACTION"].str.contains("enters").fillna(False)]
    bos_player_swap_actions = day["BOSTON_ACTION"][day["BOSTON_ACTION"].str.contains("enters").fillna(False)]

    gsw_player_changes = gsw_player_swap_actions.str.split(" enters the game for ")
    bos_player_changes = bos_player_swap_actions.str.split(" enters the game for ")

    player_change_rows = pd.concat([gsw_player_changes, bos_player_changes]).sort_index().index

    events = []

    gsw_score = 0
    bos_score = 0
    time = 0

    for row in player_change_rows:
        if row in gsw_player_changes and row in bos_player_changes:
            raise Exception("WTF")
        print(row)
        old_gsw_score, gsw_score = gsw_score, day.loc[row]["GOLDEN STATE_SCORE"]
        old_bos_score, bos_score = bos_score, day.loc[row]["BOSTON_SCORE"]
        old_time, time = time, calc_time_seconds(day.loc[row]["QUARTER"], day.loc[row]["TIME_REMAINING"])
        if old_time != time:
            gsw_lineup_list = list(gsw_lineup)
            bos_lineup_list = list(bos_lineup)
            events.append(
                    generate_event(
                        gsw_lineup_list[0], gsw_lineup_list[1], gsw_lineup_list[2], gsw_lineup_list[3], gsw_lineup_list[4],
                        bos_lineup_list[0], bos_lineup_list[1], bos_lineup_list[2], bos_lineup_list[3], bos_lineup_list[4],
                        int((gsw_score - old_gsw_score) / (time - old_time) * 60 * 48),
                        int((bos_score - old_bos_score) / (time - old_time) * 60 * 48),
                        int(time - old_time), int(time), is_gsw_home
                        ))
        # process new lineup
        if row in gsw_player_changes:
            new, old = gsw_player_changes[row]
            gsw_lineup.remove(old)
            gsw_lineup.add(new)
        else:
            new, old = bos_player_changes[row]
            bos_lineup.remove(old)
            bos_lineup.add(new)

    # For now, analyze all events that are more than 1 minute long.
    events = list(filter(lambda item: item["TIME_ELAPSED"] > 60, events))
    with open(f'{date}_processed.csv', 'w') as f:
        keys = events[0].keys()
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(events)
        # json.dump(events, f, default=list)
    all_events.extend(events)
    # max(events, key=lambda item: item["GSW_SCORE_NORM30"])

with open('all_processed_mid.csv', 'w') as f:
    keys = all_events[0].keys()
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(all_events)

# import matplotlib.pyplot as plt
# from scipy.stats import poisson
# import numpy as np
# lin = np.arange(0, 300)
# plt.hist([event["HOME_SCORE_NORM48"] for event in all_events], density=True)
# plt.plot(lin, poisson(148).pmf(lin))
# plt.show()
