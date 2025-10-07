

from mesa import Model, AgentSet


class TrafficModel(Model):

    dt: float
    def __init__(self, dt ):
        # Call the parent constructor
        # # super.__init__(args)

        self.dt = dt
        self.agentSet = AgentSet("""Whatever args go here""")
        