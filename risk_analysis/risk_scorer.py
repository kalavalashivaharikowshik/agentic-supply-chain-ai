class RiskScorer:

    def calculate_risk(self, severity):

        if severity >= 80:
            return "CRITICAL"

        if severity >= 50:
            return "HIGH"

        if severity >= 20:
            return "MEDIUM"

        return "LOW"