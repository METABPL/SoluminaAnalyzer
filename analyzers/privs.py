from analyzer import Analyzer
from SoluminaImport.class_model import *
from path_utils import enumerate_paths
import fault

privileges = [
    "BUYOFF_CUST",
    "BUYOFF_INSP",
    "BUYOFF_MFG",
    "BUYOFF_MFG2",
    "BUYOFF_OVERRIDE_CUST",
    "BUYOFF_OVERRIDE_DC",
    "BUYOFF_OVERRIDE_INSP",
    "BUYOFF_OVERRIDE_MFG",
    "BUYOFF_OVERRIDE_MFG2",
    "BUYOFF_OVERRIDE_QA",
    "BUYOFF_OVERRIDE_TECH",
    "BUYOFF_OVERRIDE_TECH2",
    "BUYOFF_QA",
    "BUYOFF_TECH",
    "BUYOFF_TECH2",
]

class PrivilegeAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, model, fault_list):
        paths = enumerate_paths(model)

        reported_items = set()

        for curr_path in paths:
            for i in range(0, len(curr_path)):
                node = curr_path[i]
                if isinstance(node, BuyoffTask):
                    id = node.bplElementUUID
                    if id in reported_items:
                        continue

                    if node.buyoffType is None or node.buyoffType == "":
                        reported_items.add(id)
                        fault_list.append(
                            fault.Fault(process=model,
                                        category="Requirements",
                                        fault="Reference to undefined object",
                                        activity=curr_path[-1].bplElementId,
                                        path=curr_path[:i+1],
                                        severity="high",
                                        outcomes=["Buyoff has empty type, so there is no corresponding buyoff privilege"]))
                    elif "BUYOFF_"+node.buyoffType not in privileges:
                        reported_items.add(id)
                        fault_list.append(
                            fault.Fault(process=model,
                                        category="Requirements",
                                        fault="Reference to undefined object",
                                        activity=curr_path[-1].bplElementId,
                                        path=curr_path[:i+1],
                                        severity="high",
                                        outcomes=["BUYOFF_"+node.buyoffType+" is not a valid Solumina privilege"]))
