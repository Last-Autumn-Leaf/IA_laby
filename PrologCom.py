from swiplserver import PrologMQI

from  Constants import  *

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

cardinal_points="NE(X):- X+1. SW(X):- X-1."

adjacent_rule="adjacent(X1,Y1,X2,Y2):- " \
              "(( Y2 is Y1+1 ; Y2 is Y1-1 ), X2 is X1); " \
              "(( X2 is X1+1 ; X2 is X1-1 ), Y2 is Y1).\n"

def create_invalid_rule(n,m):
    return "invalid(X,Y):- X<0;X>={};Y<0;Y>={}.\n".format(n,m)

action_rule="action(X1,Y1,X2,Y2) :-" \
            "adjacent(X1,Y1,X2,Y2),not("+prolog_dict[WALL]+"(X2,Y2))," \
            "not(invalid(X2,Y2)).\n"


class PrologCom:
    def create_prolog_file(self,maze):
        prologfile_name='prolog/map'
        prolog_file=open(prologfile_name,'w')
        for i in range(len(maze)):
            for j in range(len(maze[i])):
                current=maze[i][j]
                prolog_file.write('{}({},{}).\t\t'.format(prolog_dict[current],i,j))
            prolog_file.write('\n')
        prolog_file.write(adjacent_rule)
        prolog_file.write(create_invalid_rule(len(maze),len(maze[0])))
        prolog_file.write(action_rule)
        prolog_file.close()
        return prologfile_name


    def __init__(self,maze):
        self.mqi=PrologMQI()
        self.prolog_thread=self.mqi.create_thread()
        self.prolog_thread.query("[{}]".format(self.create_prolog_file(maze)))

    def getAction(self,x,y):
        result= [ (d["R1"],d["R2"]) for d in self.prolog_thread.query("action({},{},R1,R2).".format(x,y))]
        return result

