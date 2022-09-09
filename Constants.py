
GAME_CLOCK = 120

WIDTH = 1200
HEIGHT = 800
PLAYER_SIZE = 0.4
ITEM_SIZE = 0.2
PERCEPTION_RADIUS = 1.2
MAX_ATTRIBUTE = 1000000
NUM_ATTRIBUTES = 12


BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)

COIN = 'C'
TREASURE = 'T'
EXIT = 'E'
OBSTACLE = 'O'
MONSTER = 'M'
WALL= '1'
EMPTY_CASE= '0'
START_CASE= 'S'

prolog_dict={
COIN :'coin',
TREASURE :'treasure',
EXIT :'exit',
OBSTACLE :'obstacle',
MONSTER :'monster',
WALL:'wall',
EMPTY_CASE:'empty',
START_CASE:'empty',


}

adjacent_rule="adjacent(X1,Y1,X2,Y2):- " \
             "  (abs(X1-X2)=:=1,Y1=:=Y2);" \
             "  (abs(Y1-Y2)=:=1,X1=:=X2).\n"

def create_invalid_rule(n,m):
    return "invalid(x,y):- x<0;x>={};y<0;y>={}.\n".format(n,m)

action_rule="action(X1,Y1,X2,Y2) :-" \
            "adjacent(X1,Y1,X2,Y2),not("+prolog_dict[WALL]+"(X2,Y2))," \
            "not(invalid(X2,Y2)).\n"