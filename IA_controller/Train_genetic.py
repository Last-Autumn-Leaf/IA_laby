import math
import numpy as np
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
        self.d_val = np.array( [create_random_attribute() for x in range(POP_SIZE)] )
        self.b_val = np.zeros_like(self.d_val,dtype=object)
        self.f_val=np.zeros((POP_SIZE,2))
        self.crossover_prob=0.9
        self.mutation_prob=0.01
        self.encode()
        self.beatten=False
        self.dummy=Player()
        self.currentGen=0
        self.F_sum=0

    def eval_fit(self):
        self.F_sum=0
        if not self.beatten :
            for i,attr in enumerate(self.d_val) :
                self.dummy.attributes=attr
                R,F=self.monsterObject.mock_fight(self.dummy)
                self.f_val[i]=np.array((R,F))
                self.F_sum +=F
                if R==4 :
                    self.beatten=True
                    self.population=attr
                    break

    def encode(self):
        def dectobin( d_array):
            temp = d_array.copy().astype(object)
            for i, val in enumerate(temp):
                temp[i] = bin(val)
            return temp

        for i,attr in enumerate(self.d_val ):
            self.b_val[i]= dectobin(attr)

    def decode(self):
        def bintodec( b_array):
            temp = b_array.copy()
            for i, val in enumerate(temp):
                temp[i] = int(val, 2)
            return temp

        for i,attr in enumerate(self.b_val ):
            self.d_val[i]= bintodec(attr)

    def doSelection(self):

        # TODO : we should implement that we alays keep the 10 % best population

        indexes_prob = np.random.rand(POP_SIZE)
        roulette = [0] * POP_SIZE
        cpt = 0
        for i,(R,F) in enumerate(self.f_val):
            roulette[i] = (cpt +F) / (self.F_sum if self.F_sum  != 0 else 1)
            cpt += F

        def getIndex(proba):
            for j, r in enumerate(roulette):
                if r > proba:
                    return j
            return len(roulette) - 1

        indexes = [getIndex(proba) for proba in indexes_prob]
        idx1 = indexes[:int(POP_SIZE / 2)]
        idx2 = indexes[int(POP_SIZE / 2):]

        return [self.b_val[idx1, :], self.b_val[idx2, :]]


    def doCrossOver(self,pairs):
        halfpop1 = pairs[0]
        halfpop2 = pairs[1]

        # we should use MODULO here
        for index, (p1, p2) in enumerate(zip(halfpop1, halfpop2)):
            p1 = p1.copy()
            p2 = p2.copy()
            if random.random() < self.crossover_prob:
                cop = random.randint(1, len(p1) - 2) # random cross-Over Point
                halfpop1[index] = np.concatenate((p1[:cop], p2[cop:]))
                halfpop2[index] = np.concatenate((p2[:cop], p1[cop:]))
        return np.vstack((halfpop1, halfpop2))

    def doMutation(self):
        for i,individu in enumerate( self.b_val ): # population
            for j,chromosome in enumerate(individu) : # individu
                chromosome=list(chromosome)[2:]
                for k,bit in enumerate(chromosome) : # every bit
                    chromosome[k] =str(int(bit)^1) if random.random()< self.mutation_prob else bit
                self.b_val[i, j]=''.join(chromosome) #'0b'+''.join(chromosome)
    def new_gen(self):
        self.encode()
        pairs=self.doSelection()
        self.b_val=self.doCrossOver(pairs)
        self.doMutation()
        #crossOver
        #Mutation
        self.currentGen+=1

    def do_step(self):
        self.decode()
        self.eval_fit()

    def __getitem__(self, item):
        if self.beatten :
            return self.population
        return self.population[item]
    def __repr__(self):
        return f"Monster at {self.pos}, attributeFound?={self.beatten}"

    def __bool__(self):
        return self.beatten

class genetic_trainer:
    def __init__(self,monsterList,monsterCoord,pc=0.9,pm=0.01):
        self.monster_list=[ MonsterOrganizer(m,pos) for m,pos in zip(monsterList,monsterCoord)]
        self.pc=pc
        self.pm=pm
        self.nbits=math.ceil( math.log2(MAX_ATTRIBUTE) )
        self.n_params=NUM_ATTRIBUTES
        # Perform Elitism, that mean 10% of fittest population
        # goes to the next generation
        # From 50% of fittest population, Individuals
        # will mate to produce offspring

    def test(self):
        for mob in self.monster_list :
            mob.do_step()
            mob.new_gen()








if __name__ == '__main__':
    setCorrectCHWD()
    map_file_name='assets/test_Map'
    theAPP = App_2(map_file_name)
    theAPP.on_init()
    GT=genetic_trainer(theAPP.maze.monsterList,getMonsterCoord(theAPP.maze.maze))
    GT.test()



    theAPP.on_execute()

