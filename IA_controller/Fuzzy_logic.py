from IA_controller.Helper_fun import setCorrectCHWD
from IA_controller.visualizer import App_2

import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

import matplotlib.pyplot as plt

class FuzzPlayer:
    membership_naming = "μ_"
    def __init__(self,tile_size):
        self.tile_size=tile_size

    def create_membership_function(self,ctrl_ant, value, name=membership_naming, n_function=5, saturation=True):
        assert (n_function >= 1)
        vecteur1 = [x - int(n_function / 2) + (0 if not n_function % 2 == 0 else 0.5) for x in range(n_function)]
        for i in range(n_function):
            if saturation and (i == 0 or i == n_function - 1):

                if i == 0:
                    ctrl_ant[name + str(i)] = fuzz.trapmf(ctrl_ant.universe,
                                                          [value * (vecteur1[i] - 2), value * (vecteur1[i] - 1),
                                                           value * vecteur1[i], value * (vecteur1[i] + 1)])

                if i == n_function - 1:
                    ctrl_ant[name + str(i)] = fuzz.trapmf(ctrl_ant.universe,
                                                          [value * (vecteur1[i] - 1), value * (vecteur1[i]),
                                                           value * (vecteur1[i] + 1), value * (vecteur1[i] + 2)])
            else:
                ctrl_ant[name + str(i)] = fuzz.trimf(ctrl_ant.universe, [value * (vecteur1[i] - 1), value * vecteur1[i],
                                                                         value * (vecteur1[i] + 1)])

    def create_rule(self,rule_matrix, input_A, input_B, output, operator='and', name=membership_naming):
        rules = []
        for i in range(len(rule_matrix)):
            for j in range(len(rule_matrix)):
                if operator == 'and':
                    rules.append(ctrl.Rule(antecedent=(input_A[name + str(i)] & input_B[name + str(j)]),
                                           consequent=output[name + str(rule_matrix[i][j])]))
                elif operator == 'or':
                    rules.append(ctrl.Rule(antecedent=(input_A[name + str(i)] | input_B[name + str(j)]),
                                           consequent=output[name + str(rule_matrix[i][j])]))

        return rules

    def createFuzzyController(self):
        # TODO: Create the fuzzy variables for inputs and outputs.
        # Defuzzification (defuzzify_method) methods for fuzzy variables:
        #    'centroid': Centroid of area
        #    'bisector': bisector of area
        #    'mom'     : mean of maximum
        #    'som'     : min of maximum
        #    'lom'     : max of maximum
        self.tile_size = 100
        DtoGoal = ctrl.Antecedent(np.linspace(-2 * self.tile_size, 2 * self.tile_size, 1000), 'DtoGoal')
        DtoObst = ctrl.Antecedent(np.linspace(-2 * self.tile_size, 2 * self.tile_size, 1000), 'DtoObstacle')
        Pcommand = ctrl.Consequent(np.linspace(-100, 100, 1000), 'PlayerCommand', defuzzify_method='centroid')

        # Accumulation (accumulation_method) methods for fuzzy variables:
        #    np.fmax
        #    np.multiply
        Pcommand.accumulation_method = np.fmax

        self.create_membership_function(DtoGoal, self.tile_size, n_function=3)
        self.create_membership_function(DtoObst, self.tile_size, n_function=3)
        self.create_membership_function(Pcommand, 50, n_function=3, saturation=False)

        '''DtoGoal['neg'] = fuzz.trapmf(DtoGoal.universe, [-0.25, -0.25, -0.1, -0.05])
        DtoGoal['zero'] = fuzz.trimf(DtoGoal.universe, [-0.05, 0, 0.05])
        DtoGoal['pos'] = fuzz.trapmf(DtoGoal.universe, [0.05, 0.1, 0.25, 0.25])

        DtoObst['neg'] = fuzz.trapmf(DtoObst.universe, [-100, -100, -10, -2])
        DtoObst['zero'] = fuzz.trimf(DtoObst.universe, [-2, 0, 2])
        DtoObst['pos'] = fuzz.trapmf(DtoObst.universe, [2, 10, 100, 100])

        Pcommand['neg'] = fuzz.trapmf(Pcommand.universe, [-10, -10, -5, -1])
        Pcommand['zero'] = fuzz.trimf(Pcommand.universe, [-1, 0, 1])
        Pcommand['pos'] = fuzz.trapmf(Pcommand.universe, [1, 5, 10, 10])'''

        RULES_MATRIX = [[1, 0, 0],
                        [2, 1, 0],
                        [2, 2, 1]]
        rules = self.create_rule(RULES_MATRIX, DtoGoal, DtoObst, Pcommand)
        '''rules.append(ctrl.Rule(antecedent=(DtoGoal['neg'] & DtoObst['neg']), consequent=Pcommand['zero']))
        rules.append(ctrl.Rule(antecedent=(DtoGoal['neg'] & DtoObst['pos']), consequent=Pcommand['neg']))
        rules.append(ctrl.Rule(antecedent=(DtoGoal['neg'] & DtoObst['zero']), consequent=Pcommand['neg']))

        rules.append(ctrl.Rule(antecedent=(DtoGoal['zero'] & DtoObst['neg']), consequent=Pcommand['pos']))
        rules.append(ctrl.Rule(antecedent=(DtoGoal['zero'] & DtoObst['pos']), consequent=Pcommand['neg']))
        rules.append(ctrl.Rule(antecedent=(DtoGoal['zero'] & DtoObst['zero']), consequent=Pcommand['zero']))

        rules.append(ctrl.Rule(antecedent=(DtoGoal['pos'] & DtoObst['neg']), consequent=Pcommand['pos']))
        rules.append(ctrl.Rule(antecedent=(DtoGoal['pos'] & DtoObst['pos']), consequent=Pcommand['zero']))
        rules.append(ctrl.Rule(antecedent=(DtoGoal['pos'] & DtoObst['zero']), consequent=Pcommand['pos']))'''

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(system)
        return self.sim

    def getOutput(self,input1,input2):
        self.sim.input['DtoGoal'] = input1
        self.sim.input['DtoObstacle'] = input2
        self.sim.compute()

        force = self.sim.output['PlayerCommand']
        return force

if __name__ == '__main__':

    # Display fuzzy variables
    '''for var in fuzz_ctrl.ctrl.fuzzy_variables:
        var.view()
    plt.show()'''


    #TODO definir une action initiale cohérente


    setCorrectCHWD()
    map_file_name = 'assets/test_Map'
    theAPP = App_2(map_file_name)


    fuzz_ctrl_x=FuzzPlayer(theAPP.maze.tile_size_x)
    fuzz_ctrl_y=FuzzPlayer(theAPP.maze.tile_size_y)
    fuzz_ctrl_x.createFuzzyController()
    fuzz_ctrl_y.createFuzzyController()
    theAPP.setIA_controller(fuzz_ctrl_x.getOutput,fuzz_ctrl_y.getOutput)

    theAPP.on_execute()
