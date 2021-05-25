"""
Handles reading and writing information about game state:
which levels have been beaten, with which score (minimum number of steps),
current level pack...
"""

import json
import os
from pathlib import Path
import common as C

# global variable really simplifies things here,
# otherwise, would need to add an argument to many classes
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
        # last level is the last finished level in the pack
        t = {
                'last_level': 0,
                'levels': []
            }
        return t

    def set_pack(self, pack, do_save=True):
        """
        Set the name of the level pack, and initializes
        the level index according to stored information.
        """
        self.current_pack = pack
        self.scores["current"] = pack

        if not self.current_pack in self.scores:
            self.scores[self.current_pack] = self.template()
            self.index_level = 1
        else:
            self.index_level = self.last_level()+1

        self.save()

    def pack_name(self):
        """
        Remove the extension from filename to have a nicer pack name.
        """
        return os.path.splitext(self.current_pack)[0]

    def load(self):
        """
        Read information from previous games stored on disk.
        """
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
        """
        Get the score (minimum num of steps) for current level.
        """
        idx = self.index_level
        if len(self.scores[self.current_pack]['levels']) > idx:
            return self.scores[self.current_pack]['levels'][idx]
        else:
            return None

    def last_level(self):
        return self.scores[self.current_pack]['last_level']


    def update(self, num_moves):
        """
        Update minimum number of moves for current level.
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
