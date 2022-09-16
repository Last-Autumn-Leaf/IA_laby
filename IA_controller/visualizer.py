import numpy as np
import pygame

from Constants import GAME_CLOCK, WHITE, GREEN, PERCEPTION_RADIUS
from Games2D import App
from IA_controller.Helper_fun import draw_rect_alpha, getMonsterCoord
from IA_controller.Train_genetic import GeneticTrainer


class App_2(App):
    def __init__(self, mazefile,fuzz_ctrl=None,plannificator=None,goalTypes=['coin','treasure']):
        super().__init__(mazefile)

        # Fuzzy Logic
        self.fuzz_ctrl = fuzz_ctrl

        #Plannification
        self.plannificator = plannificator
        self.plannificatorFun = plannificator.default_plan_fun if plannificator is not None else None
        self.current_path = None


        self.Fx = 0
        self.Fy = 0

        self.time_before_deblock = self.timer + 2

        self.vectors_to_show = []
        self.goalTypes =goalTypes
        self.on_init()
        self.current_player_case = self.getPlayerCoord()
        self.previous_player_case = self.current_player_case
        self.current_player_quadrant = self.getPlayerQuadrant()
        self.treasure_coin_list_size= len(self.maze.treasureList + self.maze.coinList)

        monsCoord=[ self.getCoordFromPix(mob.rect.center) for mob in self.maze.monsterList]

        # De base on considère les monstres comme des nodes bloquées
        if plannificator is not None :
            plannificator.blocked_node = set(monsCoord)

        # Genetic Trainer va nous dire quels monstres sont battus dynamiquement
        self.GT = GeneticTrainer(self.maze.monsterList,monsCoord)
        self.reTrainGT()

    getRadius = lambda self, size: np.sqrt(size[0] ** 2 + size[1] ** 2)
    getCoordQuadrantFromPix = lambda self, coord: (int(((coord[0] / self.maze.tile_size_x) % 1) / 0.5), int(((coord[1] / self.maze.tile_size_y) % 1) / 0.5))
    getCoordFromPix = lambda self, coord: (int(coord[0] / self.maze.tile_size_x), int(coord[1] / self.maze.tile_size_y))
    getPlayerCoord = lambda  self : self.getCoordFromPix(self.player.get_rect().center)

    def reTrainGT(self):
        if self.GT.train(500) :
            if self.plannificator is not None :
                self.plannificator.blocked_node.clear()
                print("All monster Beatten !")
            else :
                self.plannificator.updateBlockedList(self.GT.getBeattenMonsterCoord())

    #  ---------- Math FUNCTIONS ------------- :
    def fix_angle(self, a):
        if a >= np.pi:
            a -= 2 * np.pi
        elif a < -np.pi:
            a += 2 * np.pi
        return a
    def getAbsMax(self, a):
        abs_max = a[0]
        for i in a:
            if abs(abs_max) < abs(i):
                abs_max = i
        return abs_max
    def cart2Polar(self, x, y):
        r = np.sqrt(x ** 2 + y ** 2)
        theta = np.arctan2(y, x)
        return r, theta
    def Polar2Cart(self, r, theta):
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y
    def getSmallest_distance_rects(self, rect1, rect2):
        dist = lambda p1, p2: np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

        if rect1 is None:
            return PERCEPTION_RADIUS * self.getRadius((self.maze.tile_size_x, self.maze.tile_size_y))

        (x1, y1) = rect1.topleft
        (x1b, y1b) = rect1.bottomright
        (x2, y2) = rect2.topleft
        (x2b, y2b) = rect2.bottomright

        left = x2b < x1
        right = x1b < x2
        bottom = y2b < y1
        top = y1b < y2
        if top and left:
            return dist((x1, y1b), (x2b, y2))
        elif left and bottom:
            return dist((x1, y1), (x2b, y2b))
        elif bottom and right:
            return dist((x1b, y1), (x2, y2b))
        elif right and top:
            return dist((x1b, y1b), (x2, y2))
        elif left:
            return x1 - x2b
        elif right:
            return x2 - x1b
        elif bottom:
            return y1 - y2b
        elif top:
            return y2 - y1b
        else:  # rectangles intersect
            return 0.

    # ---------- VISUALISATION FUNCTIONS ----------- :
    def on_render(self):
        self.maze_render()
        self.draw_current_path()
        self.draw_vectors()
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        pygame.display.flip()
    def draw_vectors(self):
        display_surf = self._display_surf
        player_pos = self.player.get_rect().center
        for (x, y) in self.vectors_to_show:
            pygame.draw.line(display_surf, WHITE, player_pos,
                             (x, y))
        # draw hitbox
        pygame.draw.rect(display_surf, GREEN, (self.player.x, self.player.y, self.player.size_x, self.player.size_y),
                         width=1)
        # Draw Force Vector
        pygame.draw.line(display_surf, GREEN, player_pos,
                         (player_pos[0] + int(30 * self.Fx), player_pos[1] + int(30 * self.Fy)))
    def draw_current_path(self, color=(0, 255, 0, 70)):
        display_surf = self._display_surf
        tile_size_x = self.maze.tile_size_x
        tile_size_y = self.maze.tile_size_y
        if self.current_path is not None:
            start_lever = False
            player_coord = self.current_player_case
            for x, y in self.current_path:
                if (x, y) == player_coord: start_lever = True;
                if start_lever:
                    draw_rect_alpha(display_surf, color, (x * tile_size_x, y * tile_size_y, tile_size_x, tile_size_y))

    # ----------- FUZZY PART ----------
    def doForce_Y(self, force):
        if force < 0:
            force = np.floor(force)
        else:
            force = np.ceil(force)

        force = int(force)
        for i in range(abs(force)):

            if force > 0:
                self.on_AI_input('DOWN')
            else:
                self.on_AI_input('UP')
    def doForce_X(self, force):
        if force < 0:
            force = np.floor(force)
        else:
            force = np.ceil(force)
        force = int(force)
        for i in range(abs(force)):
            if force > 0:
                self.on_AI_input('RIGHT')
            else:
                self.on_AI_input('LEFT')

    def NextCaseDetector(self):
        # renvoie false si joueur a pas change
        # renvoie true si joueur a change
        player_rect = self.player.get_rect()
        topleft_corner_player = player_rect.topleft
        bottomright_corner_player = player_rect.bottomright

        case_coord = self.current_player_case
        topleft_corner_case = (case_coord[0] * self.maze.tile_size_x, case_coord[1] * self.maze.tile_size_y)
        bottomright_corner_case = ((case_coord[0] + 1) * self.maze.tile_size_x - 1, (case_coord[1] + 1) * self.maze.tile_size_y - 1)

        x1 = topleft_corner_player[0]
        y1 = topleft_corner_player[1]

        x2 = bottomright_corner_player[0]
        y2 = bottomright_corner_player[1]

        xmin = topleft_corner_case[0]
        ymin = topleft_corner_case[1]

        xmax = bottomright_corner_case[0]
        ymax = bottomright_corner_case[1]

        if x2 < xmin or x1 > xmax or y2 < ymin or y1 > ymax:
            return True
        else:
            return False

    def getPlayerQuadrant(self):
        return self.getCoordQuadrantFromPix(self.player.get_rect().center)

    def getOpposingQuadrant(self):
        a = self.getPlayerQuadrant()
        if a[0] == 0:
            x = 1
        else:
            x = 0
        if a[1] == 0:
            y = 1
        else:
            y = 0
        return x, y

    def getOpposingQuadrantCenterPixel(self):
        nx, ny =self.current_player_case  #self.getPlayerCoord()
        qx, qy = self.getOpposingQuadrant()
        x = int((nx + 0.25) * self.maze.tile_size_x + qx * self.maze.tile_size_x / 2)
        y = int((ny + 0.25) * self.maze.tile_size_y + qy * self.maze.tile_size_y / 2)
        return x, y

    def Tick_second(self):
        # passe a True chaque seconde
        if self.timer > self.time_before_deblock:
            self.time_before_deblock +=1
            return True
        else:
            return False

    def check_goal_reach(self):
        collide_index = self.player.get_rect().collidelist(self.maze.coinList)
        if not collide_index == -1:
            return  self.getCoordFromPix(self.maze.coinList[collide_index].center)
        collide_index = self.player.get_rect().collidelist(self.maze.treasureList)
        if not collide_index == -1:
            return self.getCoordFromPix(self.maze.treasureList[collide_index].center)
        return False

    def doFuzzy(self,allObs):

        gx, gy = self.current_goal
        percept = self.maze.make_perception_list(self.player, self._display_surf)
        # If we percept something we set it as the goal
        if len(percept[2]) != 0:
            gx, gy = percept[2][0].center

        # IF WE FOUND A GOAL :
        if self.current_goal:
            self.vectors_to_show.append((gx, gy))
            player_pos = self.player.get_rect().center
            gx -= player_pos[0]
            gy -= player_pos[1]

            if not allObs:  # If there is no obstacles
                allObs.append((-gx, -gy, None))

            alldev = []
            rG, thethaG = self.cart2Polar(gx, gy)
            for (ox, oy, oObject) in allObs:
                self.vectors_to_show.append((ox, oy))
                # vecteur obstacle joueur
                ox -= player_pos[0]
                oy -= player_pos[1]
                rO, thethaO = self.cart2Polar(ox, oy)

                #Fix angle and distance
                rO = self.getSmallest_distance_rects(oObject, self.player.get_rect())
                theta = self.fix_angle(thethaO - thethaG)

                theta_prime = self.fuzz_ctrl[(theta, rO)]
                alldev.append(theta_prime)

            # We use the absolute max
            theta_prime = self.getAbsMax(alldev)
            #theta_prime = np.mean(alldev)
            thethaG += theta_prime

            R = 6
            self.Fx, self.Fy = self.Polar2Cart(R, thethaG)
            self.doForce_X(self.Fx)
            self.doForce_Y(self.Fy)
    def get_obstacles(self):
        # Let's try to get the obstacles :
        # the 4 lists are [wall_list, obstacle_list, item_list, monster_list]
        percept = self.maze.make_perception_list(self.player, self._display_surf)
        allObs = []
        for walls in percept[0]:
            allObs.append((walls.centerx, walls.centery, walls))
        for obs in percept[1]:
            allObs.append((obs.centerx, obs.centery, obs))
        # Should avoid monster too
        for mons in percept[3]:
            allObs.append((mons.centerx, mons.centery, mons))

        return allObs
    def getGoalFromPath(self):
        #TODO
        player_coord=self.current_player_case
        if self.current_path  :
            if player_coord in self.current_path:
                current_goal_index = self.current_path.index(player_coord)
                case_goal = self.current_path[
                    current_goal_index + (1 if current_goal_index != len(self.current_path) - 1 else 0)]

                gx = (case_goal[0] + 0.5) * self.maze.tile_size_x
                gy = (case_goal[1] + 0.5) * self.maze.tile_size_y
                gx=int(gx)
                gy=int(gy)
                return (gx,gy)
            else :
                self.current_path =self.plannificatorFun(self.getPlayerCoord(), self.goalTypes)
                return self.getGoalFromPath()

    def update_player_case(self):
        self.previous_player_case=self.current_player_case
        self.current_player_case=self.getPlayerCoord()

    blocked_index=0
    def unblock_player(self):
        if self.Tick_second():
            # On est bloquée si au bout de 2 secondes on est toujours sur la même case !!
            if self.current_player_case == self.previous_player_case and self.blocked_index ==0:
                self.current_goal = self.getOpposingQuadrantCenterPixel()
                self.blocked_index=1

            elif self.current_player_case == self.previous_player_case and self.blocked_index ==1 :
                self.current_goal=self.getGoalFromPath()
                self.blocked_index = 2

            elif self.current_player_case == self.previous_player_case and self.blocked_index ==2 : # case bloquante !!
                current_goal_index = self.current_path.index(self.current_player_case)
                next_case_goal = self.current_path[current_goal_index + (1 if current_goal_index != len(self.current_path)-1 else 0)]
                self.plannificator.blocked_node.add(next_case_goal)
                self.current_path = self.plannificatorFun(self.current_player_case, self.goalTypes)
                self.current_goal = self.getGoalFromPath()
                self.blocked_index = 0
            else:
                self.blocked_index = 0

            self.previous_player_case = self.current_player_case



    def on_execute(self):
        if self.plannificatorFun:
            self.current_path = self.plannificatorFun(self.getPlayerCoord(), self.goalTypes)
            self.current_goal=self.getGoalFromPath()
        while self._running:
            self._clock.tick(GAME_CLOCK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.USEREVENT:
                    self.timer += 0.01
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            self.on_keyboard_input(keys)

            self.unblock_player()


            if self.fuzz_ctrl is not None:
                self.vectors_to_show.clear()
                allObs=self.get_obstacles()

                # --- START IA INPUT ----
                if self.NextCaseDetector(): # IF we detect a change of case we change the recompute the goal
                    self.update_player_case()
                    self.current_goal = self.getGoalFromPath()

                self.doFuzzy(allObs)

            # --- END IA OUTPUT ----

            # ------ Collision check
            # check if we collide with GOAL :
            goal_coord=self.check_goal_reach()
            if goal_coord:
                self.plannificator.removedFromGoal.add(goal_coord)
                self.current_path = self.plannificatorFun(self.current_player_case, self.goalTypes)
                self.current_goal = self.getGoalFromPath()

                if len(self.current_path)==0 :
                    # If we don,t find a path and some monsters aren't beatten retrain the genetic algo
                    if not self.GT.isAllMobsBeatten() :
                        self.reTrainGT()
                        self.current_path = self.plannificatorFun(self.current_player_case, self.goalTypes)
                    else :
                        # we try to compute a path as the exit !
                        self.current_path = self.plannificatorFun(self.getPlayerCoord(), ['exit'])
                        self.current_goal = self.getGoalFromPath()

            # Check monster collision :
            monster = self.on_monster_collision()
            if monster:
                attr = self.GT.get_attributeFrom_Mons(monster)
                if attr is not None:
                    self.player.set_attributes(attr)
            # -------- END

            if self.on_coin_collision():
                self.score += 1
            if self.on_treasure_collision():
                self.score += 10
            monster = self.on_monster_collision()
            if monster:
                if monster.fight(self.player):
                    self.maze.monsterList.remove(monster)
                else:
                    self._running = False
                    self._dead = True
            if self.on_exit():
                self._running = False
                self._win = True

            self.on_render()

        while self._win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._win = False
            self.on_win_render()

        while self._dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._dead = False
            self.on_death_render()

        self.on_cleanup()


    # For CUSTOM SETTING
    def setPlannificator(self, plannificator):
        self.plannificator = plannificator
    def setPlanFun(self, planFun):
        self.plannificatorFun = planFun
    def setGoalTypes(self, goalTypes):
        self.goalTypes = goalTypes
    def setFuzzCtrl(self, fuzz_ctrl):
        self.fuzz_ctrl = fuzz_ctrl
