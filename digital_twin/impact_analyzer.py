class ImpactAnalyzer:

    def analyze_delay(self, current_stock, daily_usage, delay_days):

        if daily_usage == 0:
            return "No consumption"

        remaining_days = current_stock / daily_usage

        if delay_days > remaining_days:
            return "Production Risk"

        return "No Risk"