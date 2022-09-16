from Constants import PERCEPTION_RADIUS
from IA_controller.Helper_fun import setCorrectCHWD
from IA_controller.visualizer import App_2

import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import matplotlib.pyplot as plt

class FuzzPlayer:
    def __init__(self,tile_size):
        self.set_fuzzy_angles_sim(tile_size)
    def __getitem__(self, item):
        return self.getOutputFromAngles(angle=item[0],rayon=item[1])
    def getOutputFromAngles(self,angle,rayon):
        self.sim.input['angle'] = angle
        self.sim.input['rayon'] = rayon
        self.sim.compute()
        output = self.sim.output['PlayerCommand']
        return output

    def set_fuzzy_angles_sim(self,tile_size):
        getRadius = lambda size : np.sqrt( size[0]**2 + size[1]**2 )
        max_R = PERCEPTION_RADIUS * getRadius(tile_size)

        theta = ctrl.Antecedent(np.linspace(-np.pi, np.pi, 10000), 'angle')
        distance = ctrl.Antecedent(np.linspace(-2 * max_R, 2 * max_R, 10000), 'rayon')
        Pcommand = ctrl.Consequent(np.linspace(-np.pi, np.pi, 10000), 'PlayerCommand', defuzzify_method='centroid')

        Pcommand.accumulation_method = np.fmax

        theta["G"] = fuzz.trapmf(theta.universe, [-2*np.pi, -2*np.pi, -np.pi / 4, 0])
        theta["C"] = fuzz.trimf(theta.universe, [-np.pi/128, 0, np.pi/128])
        theta["D"] = fuzz.trapmf(theta.universe, [0, np.pi / 4, 2*np.pi, 2*np.pi])

        distance["P"] = fuzz.trapmf(distance.universe, [-2 * max_R, -2 * max_R, 0, max_R])
        distance["L"] = fuzz.trapmf(distance.universe, [0, max_R, 2 * max_R, 2 * max_R])

        Pcommand_val=np.pi/4
        Pcommand["G"] = fuzz.trimf(Pcommand.universe, [-2*Pcommand_val, -Pcommand_val, 0])
        Pcommand["C"] = fuzz.trimf(Pcommand.universe, [-Pcommand_val, 0, Pcommand_val])
        Pcommand["D"] = fuzz.trimf(Pcommand.universe, [0,Pcommand_val, 2*Pcommand_val])

        rules = []
        rules.append(ctrl.Rule(antecedent=((theta["G"]  ) & distance["P"]), consequent=Pcommand["D"]))
        rules.append(ctrl.Rule(antecedent=((theta["G"] ) & distance["L"]), consequent=Pcommand["C"]))

        rules.append(ctrl.Rule(antecedent=((theta["D"]) & distance["P"]), consequent=Pcommand["G"]))
        rules.append(ctrl.Rule(antecedent=((theta["D"]) & distance["L"]), consequent=Pcommand["C"]))

        rules.append(ctrl.Rule(antecedent=(theta["C"] & distance["P"]), consequent=Pcommand["G"] ))
        rules.append(ctrl.Rule(antecedent=(theta["C"] & distance["L"]), consequent=Pcommand["C"]))

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(system)
        return self.sim




if __name__ == '__main__':
    setCorrectCHWD()
    map_file_name = 'assets/test_Map'
    theAPP = App_2(map_file_name)


    tile_size = (theAPP.maze.tile_size_x, theAPP.maze.tile_size_y)
    fuzz_ctrl = FuzzPlayer(tile_size)
    #theAPP.setFuzzCtrl(fuzz_ctrl)

    SHOW_VARIABLE=True
    if SHOW_VARIABLE :
        for i,var in enumerate(fuzz_ctrl.sim.ctrl.fuzzy_variables):
            var.view()
            #plt.savefig(f'test/fig{i}.png')
        #plt.show()

