from conflict_resolver.rule_engine import RuleEngine


class DecisionMaker:

    def make_decision(self, stock_days, cost, risk_level):

        engine = RuleEngine()

        decision = engine.evaluate(stock_days, cost, risk_level)

        print("Decision Maker → Decision:", decision)

        return decision