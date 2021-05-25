import json
import common as C

scores = None

def load_scores():
    global scores
    scores = Scores()

class Scores:
    """
    Class to save number of moves for each solved level.
    Scores are writen to and read from a 'scores' file.
    """

    def __init__(self):
        self.scores = None
        self.index_level = 0
        self.load()

    def template(self):
        t = {
                'style': 'single_file',
                'last_level': 0,
                'levels': []
            }
        return t

    def set_pack(self, pack, do_save=True):
        self.current_pack = pack
        self.scores["current"] = pack

        if not self.current_pack in self.scores:
            self.scores[self.current_pack] = self.template()
            self.index_level = 1
        else:
            self.index_level = self.last_level()+1

        self.save()


    def load(self):
        try:
            with open("scores", "r") as data:
                self.scores = json.load(data)
        except FileNotFoundError:
            print("No saved data")
            self.scores = {
            }

        if "current" in self.scores:
            pack = self.scores["current"]
        else:
            if not len(C.PACKS):
                raise ValueError("PACK is empty, should at least contain one level pack")
            pack = C.PACKS[0]

        self.set_pack(pack)


    def get(self):
        idx   = self.index_level
        if len(self.scores[self.current_pack]['levels']) > idx:
            return self.scores[self.current_pack]['levels'][idx]
        else:
            return None

    def last_level(self):
        return self.scores[self.current_pack]['last_level']

    def level_style(self):
        return self.scores[self.current_pack]['style']


    def update(self, num_moves):
        """
        Update current number of moves for current level
        """
        idx   = self.index_level

        if idx > self.last_level():
            self.scores[self.current_pack]['last_level'] = idx

        lev = self.scores[self.current_pack]['levels']
        while len(lev) < idx+1:
            lev.append(None)

        if lev[idx] is None or lev[idx] > num_moves:
            lev[idx] = num_moves

        self.save()


    def save(self):
        """
        Store scores and current information in 'scores' file
        """
        with open("scores", "w") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=4)
