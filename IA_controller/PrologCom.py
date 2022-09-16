from swiplserver import PrologMQI, PrologError
from  Constants import  *
from IA_controller.Helper_fun import setCorrectCHWD, getMazeFromFile

prolog_dict={
COIN :'coin',
TREASURE :'treasure',
EXIT :'exit',
OBSTACLE :'obstacle',
MONSTER :'monster',
WALL:'wall',
EMPTY_CASE:'empty',
START_CASE:'start',


}

cardinal_points="NE(X):- X+1. SW(X):- X-1."
adjacent_rule="adjacent(X1,Y1,X2,Y2):- " \
              "(( Y2 is Y1+1 ; Y2 is Y1-1 ), X2 is X1); " \
              "(( X2 is X1+1 ; X2 is X1-1 ), Y2 is Y1).\n"

def create_invalid_rule(n,m):
    return "invalid(X,Y):- X<0;X>={};Y<0;Y>={}.\n".format(n,m)

action_rule="action(X1,Y1,X2,Y2) :- not("+prolog_dict[WALL]+"(X1,Y1))," \
            "adjacent(X1,Y1,X2,Y2),not("+prolog_dict[WALL]+"(X2,Y2))," \
            "not(invalid(X2,Y2)).\n"


class PrologCom:

    def __init__(self,maze):
        self.maze=maze
        self.existing_type=set()
        self.mqi=PrologMQI()
        self.prolog_thread=self.mqi.create_thread()
        self.prolog_thread.query("[{}]".format(self.create_prolog_file(maze)))
        self.n=len(maze)
        self.m=len(maze[0])
        self.createNeighborsMap()

    def create_prolog_file(self,maze):
        prologfile_name='prolog/map'
        prolog_file=open(prologfile_name,'w')
        for y in range(len(maze)):
            for x in range(len(maze[y])):
                current=maze[y][x]
                current_type=prolog_dict[current]
                self.existing_type .add(current_type)
                prolog_file.write('{}({},{}).\t\t'.format(prolog_dict[current],x,y))
            prolog_file.write('\n')
        prolog_file.write(adjacent_rule)
        prolog_file.write(create_invalid_rule(len(maze[0]),len(maze)))
        prolog_file.write(action_rule)
        prolog_file.close()
        return prologfile_name

    def getAction(self,x,y):
        result= [ (d["R1"],d["R2"]) if type(d)==dict else []
            for d in self.prolog_thread.query("action({},{},R1,R2).".format(x,y)) if type(d)==dict]
        return result

    def createNeighborsMap(self):
        self.neighbors_map={}
        for y in range(self.n):
            for x in range(self.m):
                if self.maze[y][x] != WALL :
                    self.neighbors_map[(x,y)]=self.getAction(x,y)

    def getNeighborsMap(self):
        return self.neighbors_map

    def getCoordFromType(self, x):

        if x  in prolog_dict :
            x=prolog_dict[x]
        x = x + "(R1,R2)."
        try :
            result = [(d["R1"], d["R2"]) if type(d)==dict else []
                  for d in self.prolog_thread.query(x) if type(d)==dict]
        except PrologError:
            return []
        return result

    def GetType(self,coord_case=(0,1)):
        coord_case = str(coord_case)
        for key in self.existing_type:
            type_case_test = self.prolog_thread.query(key+coord_case + ".")
            if type_case_test:
                return key

if __name__ == '__main__':
    setCorrectCHWD()

    map_file_name='assets/test_Map'
    maze=getMazeFromFile(map_file_name)
    prolog_com=PrologCom(maze)
    Position_coin = prolog_com.getCoordFromType(COIN)
    Position_treasure = prolog_com.getCoordFromType(TREASURE)
    Position_exit = prolog_com.getCoordFromType(EXIT)
    Position_start = prolog_com.getCoordFromType(START_CASE)
    Position_free_case = prolog_com.getCoordFromType(EMPTY_CASE)
    Position_wall = prolog_com.getCoordFromType(WALL)
    Position_obstacle = prolog_com.getCoordFromType(OBSTACLE)

    ### affichage de la map ###
    print('carte du labyrinthe :')
    print(*maze,sep = "\n")
    ### --- ###

    ### liste par type des cases de la carte ###
    print('Liste des coordonees (en case) des coins = \n\t{}'.format(Position_coin))
    print('Liste des coordonees (en case) des treasures = \n\t{}'.format(Position_treasure))
    print('Coordonees (en case) de l\'exit = \n\t{}'.format(Position_exit[0]))
    print('Coordonees (en case) du start = \n\t{}'.format(Position_start[0]))
    print('Liste des coordonees (en case) des cases libres = \n\t{}'.format(Position_free_case))
    print('Liste des coordonees (en case) des cases murs = \n\t{}'.format(Position_wall))
    print('Liste des coordonees (en case) des cases avec un obstacle = {}'.format(Position_obstacle))
    ### --- ###

    ### Exemple de l'appropriation du type en rentrant les coordonnees d'une case ###
    case_to_test = (1,0)
    type_case = prolog_com.GetType(coord_case = case_to_test)
    print('type de la case de coordonnees ({},{}) : {}'.format(case_to_test[0], case_to_test[1], type_case))
    ### --- ###