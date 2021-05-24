FactionNameList = ["rome", "cyprus", "lybia", "rhodos"]
PlayerNameList = ["david", "felix", "alex", "sebi"]


class Faction:
    def __init__(self, name):
        self.faction_name = name
        self.faction_wins = {'1v1': 0, '2v2': 0, '3v3': 0, '4v4': 0}
        self.faction_games = {'1v1': 0, '2v2': 0, '3v3': 0, '4v4': 0}

    def report_win(self, game_format):
        self.faction_wins[game_format] += 1
        self.faction_games[game_format] += 1

    def report_lose(self, game_format):
        self.faction_games[game_format] += 1

    def get_win_rate(self):
        try:
            rate_sum = sum(self.faction_wins.values()) / sum(self.faction_games.values())
        except ZeroDivisionError:
            rate_sum = 0
        try:
            rate_1v1 = self.faction_wins['1v1'] / self.faction_games['1v1']
        except ZeroDivisionError:
            rate_1v1 = 'no data'
        try:
            rate_2v2 = self.faction_wins['2v2'] / self.faction_games['2v2']
        except ZeroDivisionError:
            rate_2v2 = 'no data'
        try:
            rate_3v3 = self.faction_wins['3v3'] / self.faction_games['3v3']
        except ZeroDivisionError:
            rate_3v3 = 'no data'
        try:
            rate_4v4 = self.faction_wins['4v4'] / self.faction_games['4v4']
        except ZeroDivisionError:
            rate_4v4 = 'no data'
        return rate_sum, rate_1v1, rate_2v2, rate_3v3, rate_4v4

    def get_pick_rate(self, number_of_all_registered_games):
        return sum(self.faction_games.values()) / number_of_all_registered_games

    def faction_update(self):
        self.faction_games += 1

    def str__faction(self, number_of_all_registered_games):
        sum_rate, rate_1v1, rate_2v2, rate_3v3, rate_4v4 = self.get_win_rate()
        return f'{self.faction_name}:\n' \
               f'All_games: {sum(self.faction_games.values())}\n' \
               f'pick_rate: {self.get_pick_rate(number_of_all_registered_games)}\n' \
               f'Win_rate: {sum_rate}\n' \
               f'1v1_win_rate: {rate_1v1}\n' \
               f'2v2_win_rate: {rate_2v2}\n' \
               f'3v3_win_rate: {rate_3v3}\n' \
               f'4v4_win_rate: {rate_4v4}\n'


class Player:
    def __init__(self, name="unnamed", defaultRank="Decurio"):
        self.player_name = name
        self.player_wins = {'1v1': 0, '2v2': 0, '3v3': 0, '4v4': 0}
        self.player_rank = defaultRank
        self.player_games = {'1v1': 0, '2v2': 0, '3v3': 0, '4v4': 0}

    def report_win(self, game_format):
        self.player_wins[game_format] += 1
        self.player_games[game_format] += 1

    def report_lose(self, game_format):
        self.player_games[game_format] += 1

    def get_win_rate(self):
        try:
            sum_player_rate = sum(self.player_wins.values()) / sum(self.player_games.values())
        except ZeroDivisionError:
            sum_player_rate = 0
        try:
            _1v1_player_rate = self.player_wins['1v1'] / self.player_games['1v1']
        except ZeroDivisionError:
            _1v1_player_rate = 'no data'
        try:
            _2v2_player_rate = self.player_wins['2v2'] / self.player_games['2v2']
        except ZeroDivisionError:
            _2v2_player_rate = 'no data'
        try:
            _3v3_player_rate = self.player_wins['3v3'] / self.player_games['3v3']
        except ZeroDivisionError:
            _3v3_player_rate = 'no data'
        try:
            _4v4_player_rate = self.player_wins['4v4'] / self.player_games['4v4']
        except ZeroDivisionError:
            _4v4_player_rate = 'no data'
        return sum_player_rate, _1v1_player_rate, _2v2_player_rate, _3v3_player_rate, _4v4_player_rate

    def str_faction(self):
        sum_rate, rate_1v1, rate_2v2, rate_3v3, rate_4v4 = self.get_win_rate()
        return f'{self.player_name}:\n' \
               f'Rank: {self.player_rank}\n' \
               f'All_games: {self.player_games}\n' \
               f'Win_rate: {sum_rate}\n' \
               f'1v1: {rate_1v1}\n' \
               f'2v2: {rate_2v2}\n' \
               f'3v3: {rate_3v3}\n' \
               f'4v4: {rate_4v4}\n'


FactionList = [Faction(name=FactionNameList[index]) for index in range(len(FactionNameList))]
print(FactionList)
PlayerList = [Player(name=PlayerNameList[index]) for index in range(len(PlayerNameList))]
PlayerList[0].report_win('1v1')
PlayerList[1].report_lose('2v2')
PlayerList[0].report_lose('2v2')
FactionList[0].report_win('2v2')
for i in FactionList:
    print(i.str__faction(1))

for i in PlayerList:
    print(i.str_faction())
