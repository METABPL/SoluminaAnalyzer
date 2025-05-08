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
        max_tool_used = {}
        max_tool_path = {}
        max_item_used = {}
        max_item_path = {}

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
                                                    category="Resource usage",
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
                                                category="Resource usage",
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
                                                category="Resource usage",
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
                                                category="Resource usage",
                                                fault="Resource leakage",
                                                tool=res_req.name,
                                                activity=curr_path[i].bplElementId,
                                                path=curr_path[:i + 1],
                                                severity="medium",
                                                outcomes=["{} {} consumed but are not specified in BOM ".format(
                                                    res_req.quantity, res_req.name)]))
                if found_faults:
                    break
            for (tool, quantity) in used_tools.items():
                if quantity < 0:
                    continue
                if tool not in max_tool_used:
                    max_tool_used[tool] = quantity
                    max_tool_path[tool] = curr_path
                elif quantity > max_tool_used[tool]:
                    max_tool_used[tool] = quantity
                    max_tool_path[tool] = curr_path

            for (item, quantity) in used_items.items():
                if quantity < 0:
                    continue
                if item not in max_item_used:
                    max_item_used[item] = quantity
                    max_item_path[item] = curr_path
                elif quantity > max_item_used[item]:
                    max_item_used[item] = quantity
                    max_item_path[item] = curr_path

        for (tool, quantity) in max_tool_used.items():
            if quantity < 0:
                continue
            if tool not in bom_tools:
                continue
            if quantity < bom_tools[tool]:
                fault_list.append(
                    fault.Fault(process=model,
                                category="Resource usage",
                                fault="Resource leakage",
                                tool=tool,
                                activity=max_tool_path[tool][-1].bplElementId,
                                path=max_tool_path[tool],
                                severity="medium",
                                outcomes=["Only a maximum of {} {} consumed but BOM specifies {}".format(
                                    tool, quantity, bom_tools[tool])]))

        for (item, quantity) in max_item_used.items():
            if quantity < 0:
                continue
            if item not in bom_items:
                continue
            if quantity < bom_items[item]:
                fault_list.append(
                    fault.Fault(process=model,
                                category="Resource usage",
                                fault="Resource leakage",
                                item=item,
                                activity=max_item_path[item][-1].bplElementId,
                                path=max_item_path[item],
                                severity="medium",
                                outcomes=["Only a maximum of {} {} consumed but BOM specifies {}".format(
                                    item, quantity, bom_items[item])]))

