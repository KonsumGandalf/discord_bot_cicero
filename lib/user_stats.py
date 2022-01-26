class user:
    wins: int
    loses: int

    def __init__(self, id_user):
        self.id_user = id_user

    def get_win_rate(self):
        try:
            return self.wins/self.loses
        except ValueError:
            return ValueError('Please ensure to have at least one lose')

