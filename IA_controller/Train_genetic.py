
from Constants import *
from IA_controller.Helper_fun import setCorrectCHWD, getMonsterCoord
from IA_controller.visualizer import App_2
from Player import Player
import random
POP_SIZE = 100
create_random_attribute = lambda: [random.randrange(1, MAX_ATTRIBUTE) for i in range(NUM_ATTRIBUTES)]

class MonsterOrganizer:
    def __init__ (self,monsterObject,monsterPos):
        self.monsterObject=monsterObject
        self.pos=monsterPos
        self.population = [create_random_attribute() for x in range(POP_SIZE)]
        self.beatten=False
        self.Attr_To_FR={}
        self.dummy=Player()

    def computeFitnessFromFR(self):
        if not self.beatten :
            for attr in self.population :
                self.dummy.attributes=attr
                R,F=self.monsterObject.mock_fight(self.dummy)
                self.Attr_To_FR[tuple(attr)]=(R,F)
                if R==4 :
                    self.beatten=True
                    self.population=attr
                    break

    def __getitem__(self, item):
        if self.beatten :
            return self.population
        return self.population[item]
    def __repr__(self):
        return f"Monster at {self.pos}, attributeFound?={self.beatten}"

    def __bool__(self):
        return self.beatten
class genetic_trainer:
    def __init__(self,monsterList,monsterCoord):
        self.monster_list=[ MonsterOrganizer(m,pos) for m,pos in zip(monsterList,monsterCoord)]

    def computeFitnessFromFR(self):
        for mob in self.monster_list :
            mob.computeFitnessFromFR()




if __name__ == '__main__':
    setCorrectCHWD()
    map_file_name='assets/test_Map'
    theAPP = App_2(map_file_name)
    theAPP.on_init()
    GT=genetic_trainer(theAPP.maze.monsterList,getMonsterCoord(theAPP.maze.maze))
    GT.computeFitnessFromFR()



    theAPP.on_execute()

