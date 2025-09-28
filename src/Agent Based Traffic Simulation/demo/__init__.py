from MyModel import MyModel
from ui import run_pygame

if __name__ == "__main__":
    model = MyModel(n_agents=100)  # reduced count so text is readable
    run_pygame(model)