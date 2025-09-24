# ui.py
import math
import solara

from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.visualization import SolaraViz, make_space_component

# ---- Agents -------------------------------------------------
class CarAgent(Agent):
    def __init__(self, model, speed=0.4):
        super().__init__(model)          # Mesa 3 pattern: unique_id is auto assigned
        self.pos = None
        self.speed = speed
        self.heading = self.model.random.uniform(0, 2 * math.pi)

    def step(self):
        # simple move with clamping at boundaries for non-toroidal space
        x, y = self.pos
        dx = self.speed * math.cos(self.heading)
        dy = self.speed * math.sin(self.heading)
        nx = min(max(0.0, x + dx), self.model.space.x_max)
        ny = min(max(0.0, y + dy), self.model.space.y_max)

        # bounce by picking a new random heading if we hit an edge
        if nx in (0.0, self.model.space.x_max) or ny in (0.0, self.model.space.y_max):
            self.heading = self.model.random.uniform(0, 2 * math.pi)

        self.model.space.move_agent(self, (nx, ny))


# ---- Model --------------------------------------------------
class TrafficModel(Model):
    def __init__(self, width=20, height=20, n_agents=30, seed=None):
        super().__init__(seed=seed)      # required in Mesa 3
        self.space = ContinuousSpace(width, height, torus=False)

        # create and place agents
        for _ in range(n_agents):
            a = CarAgent(self)
            x = self.random.uniform(0, width)
            y = self.random.uniform(0, height)
            self.space.place_agent(a, (x, y))

    def step(self):
        # replacement for RandomActivation: shuffle agents and call their step
        self.agents.shuffle_do("step")   # Mesa 3 AgentSet activation


# ---- Visualization ------------------------------------------
def agent_portrayal(agent):
    # Matplotlib backend keys: color, shape, size, alpha, layer
    return {"color": "blue", "shape": "o", "size": 30, "alpha": 1.0, "layer": 0}

# Optional: tweak the axes
def post_process(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

# Sliders must match TrafficModel __init__ keywords
model_params = {
    "width":  {"type": "SliderInt", "label": "Width",  "value": 20, "min": 5,  "max": 100, "step": 1},
    "height": {"type": "SliderInt", "label": "Height", "value": 20, "min": 5,  "max": 100, "step": 1},
    "n_agents": {"type": "SliderInt", "label": "Agents", "value": 30, "min": 1, "max": 300, "step": 1},
    "seed": 42,  # fixed parameter, not user controlled
}

@solara.component
def Page():
    # Create the initial model instance
    model = TrafficModel(
        width=model_params["width"]["value"],
        height=model_params["height"]["value"],
        n_agents=model_params["n_agents"]["value"],
        seed=model_params["seed"],
    )

    # Space component uses matplotlib by default
    Space = make_space_component(agent_portrayal, post_process=post_process, draw_grid=False)

    # SolaraViz handles play, pause, step, speed, and re-instantiation from sliders
    return SolaraViz(
        model,
        components=[Space],
        model_params=model_params,
        name="Traffic on ContinuousSpace",
    )
