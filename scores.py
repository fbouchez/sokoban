import json

class Scores:
    def __init__(self, game):
        self.game = game
        self.scores = None

    def load(self):
        try:
            with open("scores", "r") as data:
                self.scores = json.load(data)
        except FileNotFoundError:
            print("No saved data")
            self.scores = {
                    'style': 'single_file',
                    'last_level': 0,
                    'levels': []
            }

    def last_level(self):
        return self.scores['last_level']

    def level_style(self):
        return self.scores['style']

    def save(self):
        # Saving score in file only when current level > saved level
        moves = self.game.level.num_moves
        idx   = self.game.index_level

        if idx > self.last_level():
            self.scores['last_level'] = idx

        lev = self.scores['levels']
        while len(lev) < idx+1:
            lev.append(None)

        if lev[idx] is None or lev[idx] > moves:
            lev[idx] = moves

        with open("scores", "w") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=4)
