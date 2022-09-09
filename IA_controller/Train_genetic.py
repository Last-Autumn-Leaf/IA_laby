from random import random

from Constants import *

POP_SIZE = 100
create_random_attribute = lambda: [random.randrange(1, MAX_ATTRIBUTE) for i in range(NUM_ATTRIBUTES)]


class genetic_train:

    def __init__(self,monster_list):
        # monster_list = [(x,y),...]
        self.n_monster = len(monster_list)
        self.monsterOrderToCoord={ i:monster_list[i] for i in range(self.n_monster) }
        # Mi -> Mi(x,y)
        self.monsterToFightResults = { i: { create_random_attribute():[] for j in range(POP_SIZE)  }
                                       for i in range(self.n_monster) }
        # monsterToFightResults
        # Mi -> FR , Mi correspond a l'index du monstre 0 <=Mi<n_monster
        # FR -> Alist: [R,F]
        # FR possède POP_size Alist en clé


