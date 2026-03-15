from digital_twin.simulation_engine import SimulationEngine


def run():

    engine = SimulationEngine()

    engine.run_delay_simulation(12)


if __name__ == "__main__":
    run()