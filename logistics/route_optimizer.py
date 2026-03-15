class RouteOptimizer:

    def choose_route(self, cost, time):

        if time < 3:
            return "Air Freight"

        if cost < 5000:
            return "Sea Freight"

        return "Rail Transport"