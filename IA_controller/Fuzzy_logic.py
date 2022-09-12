from IA_controller.Helper_fun import setCorrectCHWD
from IA_controller.PrologCom import PrologCom
from IA_controller.visualizer import App_2

import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

import matplotlib.pyplot as plt

#pour que le fuzzy controller puisse bouger le bonhomme
from Games2D import *

membership_naming="μ_"
def create_membership_function(ctrl_ant,value,name=membership_naming,n_function=5,saturation=True):
    assert(n_function>=1)
    vecteur1 = [x-int(n_function/2) +(0 if not n_function%2==0 else 0.5) for x in range(n_function)]
    for i in range(n_function):
        if saturation and (i==0 or i==n_function-1) :

            if i==0:
                ctrl_ant[name + str(i)] = fuzz.trapmf(ctrl_ant.universe,
                    [value * (vecteur1[i] - 2),value * (vecteur1[i] - 1), value * vecteur1[i],value * (vecteur1[i] + 1)])

            if i==n_function-1:
                ctrl_ant[name + str(i)] = fuzz.trapmf(ctrl_ant.universe,
                    [value * (vecteur1[i] - 1),value * (vecteur1[i] ), value * (vecteur1[i] + 1),value * (vecteur1[i] + 2)])
        else:
            ctrl_ant[name+str(i)]= fuzz.trimf(ctrl_ant.universe, [value*(vecteur1[i]-1), value*vecteur1[i], value*(vecteur1[i]+1)])

def create_rule(rule_matrix,input_A,input_B,output,operator='and',name=membership_naming):
    rules = []

    for i in range(len(rule_matrix)):
        for j in range(len(rule_matrix)):
            if operator=='and':
                rules.append(ctrl.Rule(antecedent=(input_A[name+str(i)] & input_B[name+str(j)]), consequent=output[name+str(rule_matrix[i][j])]))
            elif operator=='or':
                rules.append(ctrl.Rule(antecedent=(input_A[name+str(i)] | input_B[name+str(j)]), consequent=output[name+str(rule_matrix[i][j])]))

    return rules

def createFuzzyController():
    # TODO: Create the fuzzy variables for inputs and outputs.
    # Defuzzification (defuzzify_method) methods for fuzzy variables:
    #    'centroid': Centroid of area
    #    'bisector': bisector of area
    #    'mom'     : mean of maximum
    #    'som'     : min of maximum
    #    'lom'     : max of maximum
    DtoGoal = ctrl.Antecedent(np.linspace(-1, 1, 1000), 'DtoGoal')
    DtoObst = ctrl.Antecedent(np.linspace(-50, 50, 1000), 'DtoObstacle')
    Pcommand = ctrl.Consequent(np.linspace(-10, 10, 1000), 'PlayerCommand', defuzzify_method='centroid')

# Accumulation (accumulation_method) methods for fuzzy variables:
    #    np.fmax
    #    np.multiply
    Pcommand.accumulation_method = np.fmax

    # TODO: Create membership functions
    DtoGoal['neg'] = fuzz.trapmf(DtoGoal.universe, [-0.25, -0.25, -0.1, -0.05])
    DtoGoal['zero'] = fuzz.trimf(DtoGoal.universe, [-0.05, 0, 0.05])
    DtoGoal['pos'] = fuzz.trapmf(DtoGoal.universe, [0.05, 0.1, 0.25, 0.25])

    DtoObst['neg'] = fuzz.trapmf(DtoObst.universe, [-100, -100, -10, -2])
    DtoObst['zero'] = fuzz.trimf(DtoObst.universe, [-2, 0, 2])
    DtoObst['pos'] = fuzz.trapmf(DtoObst.universe, [2, 10, 100, 100])

    Pcommand['neg'] = fuzz.trapmf(Pcommand.universe, [-10, -10, -5, -1])
    Pcommand['zero'] = fuzz.trimf(Pcommand.universe, [-1, 0, 1])
    Pcommand['pos'] = fuzz.trapmf(Pcommand.universe, [1, 5, 10, 10])

    # TODO: Define the rules.
    rules = []
    rules.append(ctrl.Rule(antecedent=(DtoGoal['neg'] & DtoObst['neg']), consequent=Pcommand['zero']))
    rules.append(ctrl.Rule(antecedent=(DtoGoal['neg'] & DtoObst['pos']), consequent=Pcommand['neg']))
    rules.append(ctrl.Rule(antecedent=(DtoGoal['neg'] & DtoObst['zero']), consequent=Pcommand['neg']))

    rules.append(ctrl.Rule(antecedent=(DtoGoal['zero'] & DtoObst['neg']), consequent=Pcommand['pos']))
    rules.append(ctrl.Rule(antecedent=(DtoGoal['zero'] & DtoObst['pos']), consequent=Pcommand['neg']))
    rules.append(ctrl.Rule(antecedent=(DtoGoal['zero'] & DtoObst['zero']), consequent=Pcommand['zero']))

    rules.append(ctrl.Rule(antecedent=(DtoGoal['pos'] & DtoObst['neg']), consequent=Pcommand['pos']))
    rules.append(ctrl.Rule(antecedent=(DtoGoal['pos'] & DtoObst['pos']), consequent=Pcommand['zero']))
    rules.append(ctrl.Rule(antecedent=(DtoGoal['pos'] & DtoObst['zero']), consequent=Pcommand['pos']))

    # Conjunction (and_func) and disjunction (or_func) methods for rules:
    #     np.fmin
    #     np.fmax
    for rule in rules:
        rule.and_func = np.fmin
        rule.or_func = np.fmax

    system = ctrl.ControlSystem(rules)
    sim = ctrl.ControlSystemSimulation(system)
    return sim



def fuzzy_command(pos_joueur, pos_obstacle):
    pass
    pos_joueur = ...
    pos_obstacle =...
    taille_obstacle =...
    #return pwm_command


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Createfuzzy controller
    fuzz_ctrl = createFuzzyController()

    # Display rules
    print('------------------------ RULES ------------------------')
    for rule in fuzz_ctrl.ctrl.rules:
        print(rule)
    print('-------------------------------------------------------')

    # Display fuzzy variables
    for var in fuzz_ctrl.ctrl.fuzzy_variables:
        var.view()
    plt.show()

    VERBOSE = False

    #TODO definir une action initiale cohérente
    action = np.array([1.0], dtype=np.float32)

    setCorrectCHWD()
    map_file_name = 'assets/test_Map'
    theAPP = App_2(map_file_name)

    for _ in range(1000):

        # Execute the action
        instruction_AI = action
        #TODO convertir l'action en instruction pour deplacer le joueur
        # theAPP.on_AI_input(instruction_AI)

        # if done:
        #     # End the episode
        #     isSuccess = False
        #     break

        # Select the next action based on the observation
        # cartPosition, cartVelocity, poleAngle, poleVelocityAtTip = observation

        # TODO: set the input to the fuzzy system
        fuzz_ctrl.input['DtoGoal'] = 0
        fuzz_ctrl.input['DtoObstacle'] = 0

        fuzz_ctrl.compute()
        if VERBOSE:
            fuzz_ctrl.print_state()

        # TODO: get the output from the fuzzy system
        force = fuzz_ctrl.output['PlayerCommand']

        action = np.array(force, dtype=np.float32).flatten()


    theAPP.on_execute()
