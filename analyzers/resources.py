from analyzer import Analyzer
from SoluminaImport.class_model import *
from path_utils import enumerate_paths
import fault

class ResourceAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, model, fault_list):
        bom_tools = {}
        bom_items = {}

        for res_req in model.resourceRequirements:
            if isinstance(res_req, ToolResource):
                bom_tools[res_req.name] = int(res_req.quantity)
            elif isinstance(res_req, ConsumableResource):
                bom_items[res_req.name] = int(res_req.quantity)

        used_tools = {}
        used_items = {}

        paths = enumerate_paths(model)

        reported_items = set()

        for curr_path in paths:
            for i in range(0, len(curr_path)):
                node = curr_path[i]
                found_faults = False
                if hasattr(node, "resourceRequirements"):
                    for res_req in node.resourceRequirements:
                        if isinstance(res_req, ToolResource):
                            if res_req.bplElementUUID in reported_items:
                                continue

                            if res_req.name in used_tools:
                                used_tools[res_req.name] -= int(res_req.quantity)
                            else:
                                used_tools[res_req.name] = int(res_req.quantity)
                            if res_req.name in bom_tools and used_tools[res_req.name] > bom_tools[res_req.name]:
                                    found_faults = True
                                    reported_items.add(res_req.bplElementUUID)
                                    fault_list.append(
                                        fault.Fault(process=model,
                                                    category="Resource Usage",
                                                    fault="Resource leakage",
                                                    tool=res_req.name,
                                                    activity=curr_path[i].bplElementId,
                                                    path=curr_path[:i+1],
                                                    severity="medium",
                                                    outcomes=["{} {} consumed but BOM only lists {}".format(
                                                    res_req.quantity, res_req.name, bom_tools[res_req.name])]))
                            elif res_req.name not in bom_tools:
                                found_faults = True
                                reported_items.add(res_req.bplElementUUID)
                                fault_list.append(
                                    fault.Fault(process=model,
                                                category="Resource Usage",
                                                fault="Resource leakage",
                                                tool=res_req.name,
                                                activity=curr_path[i].bplElementId,
                                                path=curr_path[:i + 1],
                                                severity="medium",
                                                outcomes=["{} {} consumed but are not specified in BOM ".format(
                                                res_req.quantity, res_req.name)]))
                        elif isinstance(res_req, ConsumableResource):
                            if res_req.bplElementUUID in reported_items:
                                continue
                            if res_req.name in used_items:
                                used_items[res_req.name] -= int(res_req.quantity)
                            else:
                                used_items[res_req.name] = int(res_req.quantity)
                            if res_req.name in bom_items and used_items[res_req.name] > bom_items[res_req.name]:
                                found_faults = True
                                reported_items.add(res_req.bplElementUUID)
                                fault_list.append(
                                    fault.Fault(process=model,
                                                category="Resource Usage",
                                                fault="Resource leakage",
                                                tool=res_req.name,
                                                activity=curr_path[i].bplElementId,
                                                path=curr_path[:i+1],
                                                severity="medium",
                                                outcomes=["{} {} consumed but BOM only lists {}".format(
                                                    res_req.quantity, res_req.name, bom_items[res_req.name])]))
                            elif res_req.name not in bom_items:
                                found_faults = True
                                reported_items.add(res_req.bplElementUUID)
                                fault_list.append(
                                    fault.Fault(process=model,
                                                category="Resource Usage",
                                                fault="Resource leakage",
                                                tool=res_req.name,
                                                activity=curr_path[i].bplElementId,
                                                path=curr_path[:i + 1],
                                                severity="medium",
                                                outcomes=["{} {} consumed but are not specified in BOM ".format(
                                                    res_req.quantity, res_req.name)]))
                if found_faults:
                    break