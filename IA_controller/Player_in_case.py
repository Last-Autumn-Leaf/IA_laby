import math
from typing import Optional, Union

import numpy as np

class PlayerInCaseEnv():
    # Coord = position dans le WORLD
    def __init__(self, coord_joueur):
        self.coord_joueur = coord_joueur
        self.pos_obstacle =...