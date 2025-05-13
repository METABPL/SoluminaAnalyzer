from fault import generate_fault_list
from analyzers.resources import ResourceAnalyzer
from analyzers.loop import LoopAnalyzer
from analyzers.decisions import DecisionAnalyzer
from analyzers.privs import PrivilegeAnalyzer
from analyzers.unreachable import ReachabilityAnalyzer
from analyzers.limits import LimitsAnalyzer

class AnalysisRunner:
    def __init__(self, analyzers=None, plans=None):
        if analyzers is None:
            self.analyzers = [ResourceAnalyzer(), LoopAnalyzer(), DecisionAnalyzer(),
                PrivilegeAnalyzer(), ReachabilityAnalyzer(),
                LimitsAnalyzer(), ]
        else:
            self.analyzers = analyzers

        if plans is None:
            self.plans = []
        else:
            self.plans = plans

    def run(self):
        fault_list = []

        for model in self.plans:
            for analyzer in self.analyzers:
                analyzer.analyze(model, fault_list)

        return generate_fault_list(fault_list)

