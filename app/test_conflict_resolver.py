from conflict_resolver.decision_maker import DecisionMaker


def run():

    decision_maker = DecisionMaker()

    decision_maker.make_decision(
        stock_days=3,
        cost=50000,
        risk_level="HIGH"
    )


if __name__ == "__main__":
    run()