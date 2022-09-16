import math
import matplotlib.pyplot as plt
import numpy as np
from Constants import *
from IA_controller.Helper_fun import setCorrectCHWD, getMonsterCoord
from Player import Player
import random
POP_SIZE = 10

create_random_attribute = lambda: [random.randrange(-MAX_ATTRIBUTE, MAX_ATTRIBUTE) for i in range(NUM_ATTRIBUTES)]

class MonsterOrganizer:
    mask=str(2+ math.ceil( math.log2(MAX_ATTRIBUTE) ))

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
        self.max_F=0
        self.mean_F=0
        # For testing
        self.evolution=[]
        self.mean_evolution=[]
        self.crossOverFunction =self.uniform_crossOver

    def eval_fit(self):
        self.F_sum=0
        if not self.beatten :
            self.mean_F=0
            for i,attr in enumerate(self.d_val) :
                self.dummy.attributes=attr
                R,F=self.monsterObject.mock_fight(self.dummy)
                self.f_val[i]=np.array((R,F))
                self.F_sum +=F
                self.max_F=max(self.max_F,F)
                self.mean_F+=F
                if R==4 :
                    self.beatten=True
                    self.d_val=attr
                    print("Attribute found at p[{}]".format(i))
                    break
            self.mean_F /=i if i !=0 else F
            self.mean_evolution.append(self.mean_F)
            self.evolution.append(self.max_F)

    def encode(self):
        def dectobin( d_array):
            temp = d_array.copy().astype(object)
            for i, val in enumerate(temp):
                temp[i] = format(val, '#0'+self.mask+'b')
            return temp

        for i,attr in enumerate(self.d_val ):
            self.b_val[i]= dectobin(attr)

    def decode(self):
        def bintodec( b_array):
            temp = b_array.copy()
            for i, val in enumerate(temp):
                temp[i] = int(val, 2)   # NO CAPPING if int(val, 2) <MAX_ATTRIBUTE else MAX_ATTRIBUTE
            return temp

        for i,attr in enumerate(self.b_val ):
            self.d_val[i]= bintodec(attr)

    def doSelection(self):
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

    def randomPointCrossOver(self,p1,p2):
        cop = random.randint(1, len(p1) - 2) # random cross-Over Point
        return np.concatenate((p1[:cop], p2[cop:])),np.concatenate((p2[:cop], p1[cop:]))

    def uniform_crossOver(self,p1,p2):
        def uniformSelection():
            child=np.zeros_like(p1)
            for i in range(NUM_ATTRIBUTES):
                if random.random() < 0.5:
                    child [i]= p1[i]
                else:
                    child [i]= p2[i]
            return child

        indexes =[i for i in range(NUM_ATTRIBUTES)]
        random.shuffle(indexes)
        p1 = p1[indexes]
        random.shuffle(indexes)
        p2 = p2[indexes]

        return uniformSelection(),uniformSelection()

    def doCrossOver(self,pairs):
        halfpop1 = pairs[0]
        halfpop2 = pairs[1]

        # we should use MODULO here
        for index, (p1, p2) in enumerate(zip(halfpop1, halfpop2)):
            p1 = p1.copy()
            p2 = p2.copy()
            if random.random() < self.crossover_prob:
                halfpop1[index],halfpop2[index]=self.crossOverFunction(p1,p2)

        return np.vstack((halfpop1, halfpop2))

    def doMutation(self):
        for i,individu in enumerate( self.b_val ): # population
            for j,chromosome in enumerate(individu) : # individu
                sign= '-' if chromosome [0]== '-' else ''
                chromosome=list(chromosome)[2 if not sign else 3:]

                '''if random.random() < self.mutation_prob :
                    # mutate only one bit
                    bit_selected = random.randint(0, len(chromosome) - 1)
                    chromosome[bit_selected] =str(int(chromosome[bit_selected])^1)'''

                for k,bit in enumerate(chromosome) : # every bit as a probability of pm to mutate
                    chromosome[k] =str(int(bit)^1) if random.random()< self.mutation_prob else bit
                self.b_val[i, j]=sign+''.join(chromosome) #'0b'+''.join(chromosome)
    def new_gen(self):
        if not self.beatten:
            self.encode()
            pairs=self.doSelection()
            self.b_val=self.doCrossOver(pairs)
            self.doMutation()
            self.currentGen+=1

    def do_step(self):
        if not self.beatten:
            self.decode()
            self.eval_fit()

    def __getitem__(self, item):
        if self.beatten :
            return self.d_val
        return self.d_val[item]
    def __repr__(self):
        return f"Monster at {self.pos},maxF={self.max_F},attributeFound?={self.beatten},gen={self.currentGen}"

    def __bool__(self):
        return self.beatten


    def test_attributes(self,attr):
        self.dummy.attributes=attr
        return self.monsterObject.mock_fight(self.dummy)

class GeneticTrainer:
    def __init__(self,monsterList,monsterCoord):
        self.monster_list=[ MonsterOrganizer(m,pos) for m,pos in zip(monsterList,monsterCoord)]
        self.monster_coord=monsterCoord


    def train(self,gen):
        for i,mob in enumerate(self.monster_list ):
            if not mob :
                for j in range(gen) :
                    mob.do_step()
                    mob.new_gen()

        return self.isAllMobsBeatten()

    def isAllMobsBeatten (self) :
        for i,mob in enumerate(self.monster_list ):
            if not mob :
                return False
        return True

    def test(self):
        for i,mob in enumerate(self.monster_list ):
            for j in range(100) :
                mob.do_step()
                mob.new_gen()
            plt.plot(mob.evolution,label='max F')
            plt.plot(mob.mean_evolution,label='mean F')
            plt.legend()
            print(mob)
            plt.show()

    def getBeattenMonsterCoord(self):
        monster_set=set()
        for i, mob in enumerate(self.monster_list):
            if mob :
                monster_set.add(mob.pos)
        return monster_set

    def get_attributeFrom_Mons(self,mons):
        # check if monster is beatten
        for i, mob in enumerate(self.monster_list):
            if mob.monsterObject==mons :
                if mob :
                    return mob[0]
                else :
                    return None # Not beatten
        return None # Not in the list ??

    def get_gen(self):
        gen_list=[]
        for i,mob in enumerate(self.monster_list ):
            gen_list.append(mob.currentGen)
        return gen_list



