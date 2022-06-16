from basketball_reference_scraper.pbp import get_pbp

playoff_games = [
        # "2022-06-02",
        # "2022-06-05",
        # "2022-06-08",
        # "2022-06-10",
        # "2022-06-13",
        ]

data = list(map(lambda date: get_pbp(date, "GSW", "BOS"), playoff_games))

for game, game_data in zip(playoff_games, data):
    game_data.to_csv(f"{game}.csv", index=False)
