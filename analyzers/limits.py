from analyzer import Analyzer
from SoluminaImport.class_model import *
from path_utils import enumerate_paths
import fault

class LimitsAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, model, fault_list):
        paths = enumerate_paths(model)

        reported = set()
        for curr_path in paths:
            for i in range(0, len(curr_path)):
                node = curr_path[i]
                if not isinstance(node, DataCollectionTask):
                    continue

                if node.lowerLimit > node.upperLimit:
                    reported.add(node.bplElementId)
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "Lower limit {} is greater than upper limit {}".format(
                                            node.lowerLimit, node.upperLimit)]))
                elif node.lowerLimit > node.targetValue:
                    reported.add(node.bplElementId)
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "Lower limit {} is greater than target value {}".format(
                                            node.lowerLimit, node.targetValue)]))
                elif node.targetValue > node.upperLimit:
                    reported.add(node.bplElementId)
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "Target value {} is greater than upper limit{}".format(
                                            node.targetValue, node.upperLimit)]))
