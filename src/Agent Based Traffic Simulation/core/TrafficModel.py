

from mesa import Model, AgentSet

class TrafficModel(Model):


    def __init__(self, dt, args):
        # Call the parent constructor
        super.__init__(args)

        self.dt = dt
        self.agentSet = AgentSet("""Whatever args go here""")
        