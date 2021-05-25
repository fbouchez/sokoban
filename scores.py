import json
import common as C

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
            }

        if "current" in self.scores:
            self.current_pack = self.scores["current"]
        else:
            if not len(C.PACKS):
                raise ValueError("PACK is empty, should at least contain one level pack")
            self.current_pack = C.PACKS[0]
            self.scores["current"] = self.current_pack


        if not self.current_pack in self.scores:
            self.scores[self.current_pack] = self.template()


    def get(self):
        idx   = self.game.index_level
        if len(self.scores[self.current_pack]['levels']) > idx:
            return self.scores[self.current_pack]['levels'][idx]
        else:
            return None

    def last_level(self):
        return self.scores[self.current_pack]['last_level']

    def level_style(self):
        return self.scores[self.current_pack]['style']

    def save(self):
        # Saving score in file only when current level > saved level
        moves = self.game.level.num_moves
        idx   = self.game.index_level

        if idx > self.last_level():
            self.scores[self.current_pack]['last_level'] = idx

        lev = self.scores[self.current_pack]['levels']
        while len(lev) < idx+1:
            lev.append(None)

        if lev[idx] is None or lev[idx] > moves:
            lev[idx] = moves

        with open("scores", "w") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=4)
