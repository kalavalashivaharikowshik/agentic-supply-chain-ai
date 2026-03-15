from risk_analysis.disruption_detector import DisruptionDetector


def run():

    detector = DisruptionDetector()
    detector.detect_disruptions()


if __name__ == "__main__":
    run()