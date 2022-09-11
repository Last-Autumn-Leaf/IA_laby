from IA_controller.Helper_fun import setCorrectCHWD
from IA_controller.PrologCom import PrologCom
from IA_controller.visualizer import App_2

import skfuzzy as fuzz
from skfuzzy import control as ctrl

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

def fuzzy_command(pos_joueur, pos_obstacle):
    pass
    pos_joueur = ...
    pos_obstacle =...
    taille_obstacle =...
    #return pwm_command