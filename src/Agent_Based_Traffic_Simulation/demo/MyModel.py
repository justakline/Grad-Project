import random

import mesa
from MyAgent import MyAgent

class MyModel(mesa.Model):
    space: mesa.space.ContinuousSpace
    def __init__(self, n_agents):
        super().__init__()
        self.x_max = 1000
        self.y_max = 1000
        self.initial_buffer = 100
        self.space: mesa.space.ContinuousSpace = mesa.space.ContinuousSpace(x_max=self.x_max, y_max=self.y_max,torus=True)

        for _ in range(n_agents):

            x = random.uniform(0,self.x_max - self.initial_buffer)
            y = random.uniform(0,self.y_max- self.initial_buffer)
            dx = random.randint(-2,2)
            dy = random.randint(-2,2)

            dx = 1 if dx == 0 else dx
            dy = 1 if dy == 0 else dy
            a = MyAgent(self, x,y, dx, dy)

            #
            # self.space.place_agent(a, (a.x, a.y))

    def step(self):
        self.agents.do("step")


