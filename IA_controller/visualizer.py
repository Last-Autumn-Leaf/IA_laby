import numpy as np
import pygame

from Constants import GAME_CLOCK, WHITE, GREEN, PERCEPTION_RADIUS
from Games2D import App
from IA_controller.Helper_fun import draw_rect_alpha


class App_2(App):
    def __init__(self, mazefile):
        super().__init__(mazefile)

        self.FOLLOW_MOUSE = False

        self.fuzz_ctrl = None
        self.plannificator = None
        self.plannificatorFun = None
        self.current_path = None

        self.Fx = 0
        self.Fy = 0

        self.vectors_to_show = []
        self.goalTypes = ['coin', 'treasure', 'exit']
        self.on_init()
        self.current_player_case = self.getPlayerCoord()

    getRadius = lambda self, size: np.sqrt(size[0] ** 2 + size[1] ** 2)

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
            player_coord = self.getPlayerCoord()
            for x, y in self.current_path:
                if (x, y) == player_coord: start_lever = True;
                if start_lever:
                    draw_rect_alpha(display_surf, color, (x * tile_size_x, y * tile_size_y, tile_size_x, tile_size_y))

    def getPlayerCoord(self):
        # coordonates are reversed !!!
        x, y = self.player.get_rect().center
        x = int(x / self.maze.tile_size_x)
        y = int(y / self.maze.tile_size_y)
        return (x, y)

    def setPlannificator(self, plannificator):
        self.plannificator = plannificator

    def setPlanFun(self, planFun):
        self.plannificatorFun = planFun

    def setGoalTypes(self, goalTypes):
        self.goalTypes = goalTypes

    def setFuzzCtrl(self, fuzz_ctrl):
        self.fuzz_ctrl = fuzz_ctrl

    def cart2Polar(self, x, y):
        r = np.sqrt(x ** 2 + y ** 2)
        theta = np.arctan2(y, x)
        return r, theta

    def Polar2Cart(self, r, theta):
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y

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

    def ChangeCaseDetector(self):
        true_case = self.getPlayerCoord()
        if self.current_player_case != true_case:
            self.current_player_case = true_case
            return True
        else:
            return False

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

    def check_goal_reach(self):
        collide_index = self.player.get_rect().collidelist(self.maze.coinList)
        if not collide_index == -1: return True;
        collide_index = self.player.get_rect().collidelist(self.maze.treasureList)
        if not collide_index == -1: return True
        return False;

    def on_execute(self):
        if self.plannificatorFun:
            self.current_path = self.plannificatorFun(self.getPlayerCoord(), self.goalTypes)

        def fix_angle(a):
            if a >= np.pi:
                a -= 2 * np.pi
            elif a < -np.pi:
                a += 2 * np.pi
            return a

        def getAbsMax(a):
            abs_max = a[0]
            for i in a:
                if abs(abs_max) < abs(i):
                    abs_max = i
            return abs_max

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

            # --- START IA INPUT ----

            if self.fuzz_ctrl is not None:
                # Let's try to get the obstacles :
                # the 4 lists are [wall_list, obstacle_list, item_list, monster_list]
                percept = self.maze.make_perception_list(self.player, self._display_surf)

                self.vectors_to_show.clear()
                allObs = []
                for walls in percept[0]:
                    allObs.append((walls.centerx, walls.centery, walls))
                for obs in percept[1]:
                    allObs.append((obs.centerx, obs.centery, obs))
                # Should avoid monster too
                for mons in percept[3]:
                    allObs.append((mons.centerx, mons.centery, mons))

                # GOAL HANDLER :
                gx, gy = None, None
                player_coord = self.getPlayerCoord()

                # if we have a current path we set the goal as the next coordinate of the player
                if self.current_path and player_coord in self.current_path:
                    current_goal_index = self.current_path.index(player_coord)
                    if current_goal_index != len(self.current_path) - 1:
                        if current_goal_index is not None and current_goal_index != len(self.current_path):
                            case_goal = self.current_path[current_goal_index + 1]
                            # next_case_right_or_left = case_goal[1] == current_case[1]
                            # next_case_top_or_bottom = case_goal[0] == current_case[0]
                            #
                            # if next_case_right_or_left:
                            #     gx = (case_goal[0]) * self.maze.tile_size_x
                            #     gy = (case_goal[1] + 0.5) * self.maze.tile_size_y
                            #
                            # if next_case_top_or_bottom:
                            #     gx = (case_goal[0]+ 0.5) * self.maze.tile_size_x
                            #     gy = (case_goal[1]) * self.maze.tile_size_y

                            gx = (case_goal[0] + 0.5) * self.maze.tile_size_x
                            gy = (case_goal[1] + 0.5) * self.maze.tile_size_y

                if len(percept[2]) != 0:  # If we percept something we set it as the goal
                    goal = percept[2][0]
                    gy = goal.centery
                    gx = goal.centerx

                elif len(percept[2]) == 0 and gx is None:
                    # get goal from coin List or Treasure List or exit
                    if len(self.maze.coinList) > 0:
                        gx = self.maze.coinList[0].centerx
                        gy = self.maze.coinList[0].centery

                    elif len(self.maze.treasureList) > 0:
                        gx = self.maze.treasureList[0].centerx
                        gy = self.maze.treasureList[0].centery

                    elif self.maze.exit:
                        gx = self.maze.exit.centerx
                        gy = self.maze.exit.centery

                    if self.FOLLOW_MOUSE:
                        gx, gy = pygame.mouse.get_pos()

                # IF WE FOUND A GOAL :
                if gx and gy:
                    self.vectors_to_show.append((gx, gy))
                    player_pos = self.player.get_rect().center
                    gx -= player_pos[0]
                    gy -= player_pos[1]

                    rG, thethaG = self.cart2Polar(gx, gy)
                    if not allObs:  # If there is no obstacles
                        allObs.append((-gx, -gy, None))
                    alldev = []
                    for (ox, oy, oObject) in allObs:
                        self.vectors_to_show.append((ox, oy))
                        # vecteur obstacle joueur
                        ox -= player_pos[0]
                        oy -= player_pos[1]
                        rO, thethaO = self.cart2Polar(ox, oy)

                        rO = self.getSmallest_distance_rects(oObject, self.player.get_rect())
                        theta = fix_angle(thethaO - thethaG)

                        theta_prime = self.fuzz_ctrl[(theta, rO)]
                        alldev.append(theta_prime)

                    # We use the absolute max
                    theta_prime = getAbsMax(alldev)
                    thethaG += theta_prime

                    R = 3
                    self.Fx, self.Fy = self.Polar2Cart(R, thethaG)
                    self.doForce_X(self.Fx)
                    self.doForce_Y(self.Fy)

            # --- END IA INPUT ----
            # we compute a new current_path everytime we change case
            # if self.plannificatorFun and self.ChangeCaseDetector():
            #     self.current_path = self.plannificatorFun(self.getPlayerCoord(), self.goalTypes)

            # check if we collide with target :
            if self.check_goal_reach():
                self.plannificator.removedFromGoal.add(self.getPlayerCoord())
                self.current_path = self.plannificatorFun(self.getPlayerCoord(), self.goalTypes)

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
