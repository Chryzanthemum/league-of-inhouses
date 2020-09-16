import random
import fire


class Teams:
    # Look up player IDs from spreadsheet
    # >>> python teams.py random_teams [0, 1, 2, 3, 4, 6, 12, 9, 10, 11]
    def random_teams(self, players):
        random.shuffle(players)

        blue = players[:5]
        red = players[5:]

        print('blue:', blue)
        print('red:', red)


if __name__ == "__main__":
    fire.Fire(Teams)
