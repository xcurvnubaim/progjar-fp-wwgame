class GameEngine:
    def __init__(self):
        self.players = []
        self.votes = {}

    def start_game(self):
        self.players = ['alice', 'bob', 'charlie']
        self.votes = {}
        return {'status': 'game started', 'players': self.players}

    def vote(self, voter, target):
        if voter not in self.players or target not in self.players:
            return {'error': 'invalid vote'}
        self.votes[voter] = target
        return {'status': 'vote recorded', 'votes': self.votes}
