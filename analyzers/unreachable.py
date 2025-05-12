from analyzer import Analyzer
from SoluminaImport.class_model import *
from path_utils import enumerate_paths
import fault

class ReachabilityAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, model, fault_list):
        paths = enumerate_paths(model)

        nodes = set()
        node_map = {}
        work_queue = model.bplElements
        while len(work_queue) > 0:
            work_item = work_queue.pop(0)
            if isinstance(work_item, EndEvent):
                continue
            nodes.add(work_item.bplElementUUID)
            node_map[work_item.bplElementUUID] = work_item
            if hasattr(work_item, "bplElements"):
                for bplElement in work_item.bplElements:
                    if bplElement.bplElementUUID not in node_map and not isinstance(bplElement, EndEvent):
                        work_queue.append(bplElement)

        reached = set()
        for curr_path in paths:
            for item in curr_path:
                reached.add(item.bplElementUUID)

        unreachable = nodes.difference(reached)

        while len(unreachable) > 0:
            longest_path = []

            for node in unreachable:
                node_paths = enumerate_paths(node_map[node])
                for node_path in node_paths:
                    if len(node_path) > len(longest_path):
                        longest_path = node_path

            if len(longest_path) == 0:
                break

            fault_list.append(
                fault.Fault(process=model,
                            category="Execution sequence",
                            fault="No execution",
                            activity=longest_path[0].bplElementId,
                            path=longest_path,
                            severity="medium",
                            outcomes=["Node path is unreachable"]))

            for remove in longest_path:
                if remove.bplElementUUID in unreachable:
                    unreachable.remove(remove.bplElementUUID)