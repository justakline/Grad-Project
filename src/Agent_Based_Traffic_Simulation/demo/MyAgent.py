import math
import random

import mesa

import MyModel
from mesa.space import ContinuousSpace

class MyAgent(mesa.Agent):
    model: MyModel
    turn_reset_len: int
    current_turn: int
    def __init__(self, model:MyModel, x, y, dx, dy):
        super().__init__(model)
        self.dx = dx
        self.dy =dy
        self.model.space.place_agent(self, (x, y))
        self.turn_reset_len = random.randint(50,200)
        self.current_turn = 0

    def step(self):
        new_x = self.pos[0] + self.dx
        new_y = self.pos[1] + self.dy

        self.model.space.move_agent(self, (new_x, new_y))
        neighbors = self.model.space.get_neighbors(self.pos, 30)
        if len(neighbors) > 1:
            self.run_away(neighbors)

        self.current_turn += 1


        # Whatever else the agent does when activated


    def run_away(self, neighbors):

        # Basically, if the current amount of time that has passed is less than the turn reset len
        # Then we are still cooling down so do not do anything, else we can now take a turn

        if self.current_turn < self.turn_reset_len:
            return


        dx = abs(self.dx)
        dy = abs(self.dy)
        speed = math.sqrt(dx ** 2 + dy ** 2)

        deg45 = [math.pi/4 + x*math.pi/2 for x in range(4)]
        deg90 = [x*math.pi/2 for x in range(4)]

        angle = random.choice(deg45+deg90)

        # rotate vector
        new_dx = dx * math.cos(angle) - dy * math.sin(angle)
        new_dy = dx * math.sin(angle) + dy * math.cos(angle)

        # rescale to preserve speed
        new_speed = math.sqrt(new_dx ** 2 + new_dy ** 2)
        self.dx = (new_dx / new_speed) * speed
        self.dy = (new_dy / new_speed) * speed


        # print(f"From ({self.dx}, {self.dy}) to ({self.dx *new_direction[0] }, {self.dy * new_direction[1]})")


        self.current_turn = 0



        # flip the dx of the current thing if the neighbors avg is negative

