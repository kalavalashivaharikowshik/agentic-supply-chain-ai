class KPIMonitor:

    def resilience_score(self, disruptions):

        score = max(0,100 - disruptions*5)
        return score


    def supplier_score(self,reliability):

        return reliability*100


    def shipping_delay_avg(self,delays):

        return sum(delays)/len(delays)