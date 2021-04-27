import json
import constants as SOKOBAN

class Scores:
    """
    Class to save number of moves for each solved level.
    Scores are writen to and read from a 'scores' file.
    """

    def __init__(self, game):
        self.game = game
        self.scores = None
        self.load()

    def template(self):
        t = {
                'style': 'single_file',
                'last_level': 0,
                'levels': []
            }
        return t

    def load(self):
        try:
            with open("scores", "r") as data:
                self.scores = json.load(data)
        except FileNotFoundError:
            print("No saved data")
            self.scores = {
                SOKOBAN.SINGLE_FILE: self.template()
            }

    def get(self):
        idx   = self.game.index_level
        return self.scores[SOKOBAN.SINGLE_FILE]['levels'][idx]

    def last_level(self):
        if not SOKOBAN.SINGLE_FILE in self.scores:
            self.scores[SOKOBAN.SINGLE_FILE] = self.template()
        return self.scores[SOKOBAN.SINGLE_FILE]['last_level']

    def level_style(self):
        return self.scores[SOKOBAN.SINGLE_FILE]['style']

    def save(self):
        # Saving score in file only when current level > saved level
        moves = self.game.level.num_moves
        idx   = self.game.index_level

        if idx > self.last_level():
            self.scores[SOKOBAN.SINGLE_FILE]['last_level'] = idx

        lev = self.scores[SOKOBAN.SINGLE_FILE]['levels']
        while len(lev) < idx+1:
            lev.append(None)

        if lev[idx] is None or lev[idx] > moves:
            lev[idx] = moves

        with open("scores", "w") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=4)
