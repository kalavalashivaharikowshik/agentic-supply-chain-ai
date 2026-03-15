from digital_twin.disruption_models import DisruptionModels
from digital_twin.impact_analyzer import ImpactAnalyzer


class SimulationEngine:

    def run_delay_simulation(self, delay_days):

        models = DisruptionModels()
        analyzer = ImpactAnalyzer()

        disruption = models.shipment_delay(delay_days)

        result = analyzer.analyze_delay(
            current_stock=1000,
            daily_usage=100,
            delay_days=delay_days
        )

        print("Simulation → Disruption:", disruption["type"])
        print("Simulation → Delay:", delay_days, "days")
        print("Simulation → Impact:", result)

        return result