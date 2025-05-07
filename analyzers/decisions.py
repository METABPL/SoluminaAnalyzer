from analyzer import Analyzer
from importer.class_model import *
from path_utils import enumerate_paths
import fault

class DecisionAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, model, fault_list):
        paths = enumerate_paths(model)

        reported = set()
        for curr_path in paths:
            for i in range(0, len(curr_path)):
                node = curr_path[i]
                if not isinstance(node, Exclusive):
                    continue

                id = node.bplElementUUID

                if id in reported:
                    continue

                requested = set()
                actual = set()

                for node_next in node.nexts:
                    if isinstance(node_next, Gateway2Activity):
                        target_op = node_next.conditionTarget
                        if target_op != node_next.toNode.bplElementName:
                            requested.add(target_op)
                            actual.add(node_next.toNode.bplElementName)

                if len(requested) == 1:
                    fault_list.append(
                        fault.Fault(process=model,
                                category="Requirements",
                                fault="Inconsistent work instructions",
                                activity=curr_path[i].bplElementId,
                                path=curr_path[:i+1],
                                severity="high",
                                outcomes=["Work instructions tell user to go to {}, but process links to {}".format(
                                    requested.pop(), actual.pop())]))
                elif len(requested) == 2:
                    fault_list.append(
                        fault.Fault(process=model,
                                category="Requirements",
                                fault="Inconsistent work instructions",
                                activity=curr_path[i].bplElementId,
                                path=curr_path[:i + 1],
                                severity="high",
                                outcomes=["Work instructions tell user to go to {} and {}, but process links to {} and {}".format(
                                    requested.pop(), requested.pop(), actual.pop(),
                                    actual.pop())]))