from analyzer import Analyzer
from SoluminaImport.class_model import *
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
                            if target_op != "":
                                requested.add(target_op)
                            if node_next.toNode.bplElementName != "":
                                actual.add(node_next.toNode.bplElementName)

                if len(requested) == 0 and len(actual) == 0:
                    reported.add(id)
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "No work instructions for decision and no destinations for decision"]))
                elif len(requested) == 0 and len(actual) == 1:
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "No work instructions for decision and only destination is {}".format(
                                            actual.pop())]))
                elif len(requested) == 0 and len(actual) == 2:
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "No work instructions for decision that leads to {} or {}".format(
                                            actual.pop(), actual.pop())]))

                elif len(requested) == 1 and len(actual) == 1:
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i+1],
                                    severity="high",
                                    outcomes=["Work instructions tell user to go to {}, but process links to {}".format(
                                        requested.pop(), actual.pop())]))
                elif len(requested) == 1 and len(actual) == 2:
                    reported.add(id)
                    requested_path = requested.pop()
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=["Work instructions tell user to go to {} in both cases, but process links to {} and {}".format(
                                        requested_path, actual.pop(),
                                        actual.pop())]))
                elif len(requested) == 2 and len(actual) == 1:
                    reported.add(id)
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "Work instructions tell user to go to {} and {}, but only destination is {}".format(
                                            requested.pop(), requested.pop(),
                                            actual.pop())]))
                elif len(requested) == 2 and len(actual) == 2 and len(requested.difference(actual)) > 0:
                    fault_list.append(
                        fault.Fault(process=model,
                                    category="Requirements",
                                    fault="Inconsistent work instructions",
                                    activity=curr_path[i].bplElementId,
                                    path=curr_path[:i + 1],
                                    severity="high",
                                    outcomes=[
                                        "Work instructions tell user to go to {} and {}, but destinations are {} and {}".format(
                                            requested.pop(), requested.pop(),
                                            actual.pop(), actual.pop())]))
