import sys
from pathlib import Path

print(str(Path(__file__).absolute().parent.parent))
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

from SoluminaImport.load_solumina import load_process
from SoluminaImport.class_model import *


"""
This is where the implementation of the plugin code goes.
The ExportIR-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
import json
import uuid
from blmodel import *

# Setup a logger
logger = logging.getLogger('ExportIR')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

attr_map = {
    "bplElementId": "id",
    "name": "name",
    "bplElementUUID": "uuid",
    "bplProcessId": "id",
    "script": "script",
    "scriptFormat": "scriptFormat",
    "type": "data_type",
}

data_attr_map = {
    "paramName": "name",
    "paramType": "dataType",
    "paramValue": "expression",
    "script": "script",
    "scriptFormat": "scriptFormat",
}

type_name_map = {
    "Process": FlowNodeTypeEnum.PROCESS,
    "BusinessRuleTask": FlowNodeTypeEnum.TASK_BUSINESS_RULE,
    "SendTask": FlowNodeTypeEnum.TASK_SEND,
    "ReceiveTask": FlowNodeTypeEnum.TASK_RECEIVE,
    "ScriptTask": FlowNodeTypeEnum.TASK_SCRIPT,
    "UserTask": FlowNodeTypeEnum.TASK_USER,
    "BuyoffTask": FlowNodeTypeEnum.TASK_USER,
    "Header": FlowNodeTypeEnum.TASK_USER,
    "Footer": FlowNodeTypeEnum.TASK_USER,
    "DataCollection": FlowNodeTypeEnum.SUBPROCESS,
    "DataCollectionTask": FlowNodeTypeEnum.TASK_USER,
    "ServiceTask": FlowNodeTypeEnum.TASK_SERVICE,
    "CallActivity": FlowNodeTypeEnum.ACTIVITY_CALL,
    "SubProcess": FlowNodeTypeEnum.SUBPROCESS,
    "Exclusive": FlowNodeTypeEnum.GATEWAY_EXCLUSIVE,
    "Inclusive": FlowNodeTypeEnum.GATEWAY_INCLUSIVE,
    "ParallelEventBased": FlowNodeTypeEnum.GATEWAY_PARALLEL,
    "Parallel": FlowNodeTypeEnum.GATEWAY_PARALLEL,
    "Complex": FlowNodeTypeEnum.GATEWAY_COMPLEX,
    "EventBased": FlowNodeTypeEnum.GATEWAY_EVENT,
    "StartEvent": FlowNodeTypeEnum.EVENT_START,
    "EndEvent": FlowNodeTypeEnum.EVENT_END,
    "ErrorEvent": FlowNodeTypeEnum.EVENT_THROW,
    "BoundaryEvent": FlowNodeTypeEnum.EVENT_BOUNDARY,
    "IntermediateCatchEvent": FlowNodeTypeEnum.EVENT_CATCH_INTER,
    "IntermediateThrowEvent": FlowNodeTypeEnum.EVENT_THROW_INTER,
}

property_map = {
    "Exclusive":
        {
            "decision": "decision",
            "decisionType": "decisionType",
        },
    "Gateway2Activity":
        {
            "conditionTarget": "conditionTarget",
        }
}
resource_type_map = {
    "ConsumableResource": ResourceTypeEnum.ITEM,
    "ToolResource": ResourceTypeEnum.TOOL,
    "HumanResource": ResourceTypeEnum.SKILL,
}

connection_map = {
    "Activity2Activity": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Gateway2Activity": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Gateway2Gateway": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Activity2Gateway": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Event2Gateway": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Gateway2Event": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Event2Activity": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Activity2Event": FlowEdgeTypeEnum.SEQUENCE_FLOW,
    "Event2Event": FlowEdgeTypeEnum.SEQUENCE_FLOW,
}

class ExportIR:
    def __init__(self):
        self.converted = set()

    def is_process(self, node):
        return isinstance(node, Process) or isinstance(node, SubProcess)

    def assign_uuids(self, node, assigned):
        node_uuid = node.bplElementUUID
        if node_uuid is None or node_uuid == "":
            node_uuid = str(uuid.uuid4())
            assigned.append(node_uuid)
            print("Setting UUID of node")
            node.bplElementUUID = node_uuid = node_uuid

        if hasattr(node, "bplElements"):
            for child in node.bplElements:
                self.assign_uuids(child, assigned)

    def all_children(self, node):
        children = []
        for value in node.__dict__.values():
            if isinstance(value, list):
                children = children + value
        return children

    def convert_node(self, node, nodes, parent, node_map):
        type_name = type(node).__name__

        node_uuid = node.bplElementUUID
        if node_uuid in self.converted:
            return

        properties = []

        if type_name in type_name_map:
            self.converted.add(node_uuid)
            ir_type_name = type_name_map[type_name]

            args = {"type": ir_type_name, "uuid": node_uuid}
            node_name = node.name
            if hasattr(node, "bplElementName"):
                bpl_node_name = node.bplElementName
            else:
                bpl_node_name = None
            for webgme_attr, ir_attr in attr_map.items():
                if hasattr(node, webgme_attr):
                    attr = getattr(node, webgme_attr)
                    if attr is not None:
                        if webgme_attr == "script":
                            args[ir_attr] = attr["#text"]
                        elif ir_attr not in args or args[ir_attr] is None or args[ir_attr] == "":
                            args[ir_attr] = attr
                    else:
                        if webgme_attr == "bplElementId":
                            if bpl_node_name is not None:
                                args[ir_attr] = bpl_node_name
                            else:
                                args[ir_attr] = node_name
                        elif webgme_attr == "bplElementName":
                            args[ir_attr] = node_name
                        else:
                            #                        print("In node type {} can't find attr {}".format(type_name, webgme_attr))
                            pass

            if type_name == "UserTask":
                instructions = []
                for child in node.stepInstructions:
                    object_id = getattr(child, "objectID")
                    inst_type = getattr(child, "type")
                    optional_val = getattr(child, "value")
                    instructions.append(FlowNodeInstruction(type=inst_type, value=optional_val,
                                                            object_id=object_id))
                if len(instructions) > 0:
                    args["documentation"] = instructions

            if hasattr(node, "textAnnotation"):
                textAnnotation = node.textAnnotation
                if textAnnotation is not None and textAnnotation != "":
                    args["documentation"] = textAnnotation

            isData = False
            if type_name == "DataCollectionTask":
                args["type"] = "InputOutputBinding"
                args["name"] = getattr(node, "description")
                args["sub_type"] = "Data Collection"
                args["data_type"] = "str"
                lower_limit = getattr(node, "lowerLimit")
                exprs = []
                if lower_limit is not None and str(lower_limit) != "":
                    lower_limit_expr = "VALUE >= {}".format(lower_limit)
                    exprs.append(lower_limit_expr)
                    properties.append(FlowNodeProperty(name="lowerLimit", value=lower_limit, type="str"))

                upper_limit = getattr(node, "upperLimit")
                if upper_limit is not None and str(upper_limit) != "":
                    upper_limit_expr = "VALUE <= {}".format(upper_limit)
                    exprs.append(upper_limit_expr)
                    properties.append(FlowNodeProperty(name="upperLimit", value=upper_limit, type="str"))

                uom = getattr(node, "unitOfMeasure")
                if uom is not None and len(uom) > 0:
                    uom_expr = "UOM == \"{}\"".format(uom)
                    exprs.append(uom_expr)
                    properties.append(FlowNodeProperty(name="unitOfMeasure", value=uom, type="str"))

                if len(exprs) > 0:
                    expr = exprs[0]
                    for next_expr in exprs[1:]:
                        expr = "And({}, {})".format(expr, next_expr)
                    args["expression"] = expr
                isData = True
            elif type_name == "BuyoffTask":
                args["type"] = "InputOutputBinding"
                args["name"] = getattr(node, "name")
                args["sub_type"] = "Buyoff"
                args["data_type"] = "bool"
                buyoffType = getattr(node, "buyoffType")
                exprs = []
                if buyoffType is not None and len(buyoffType) > 0:
                    buyoffTypeExpr = "buyoff_type == \"{}\"".format(buyoffType)
                    exprs.append(buyoffTypeExpr)
                    properties.append(FlowNodeProperty(name="buyoff_type", value=buyoffType, type="str"))

                buyoffCert = getattr(node, "cert")
                if buyoffCert is not None and len(buyoffCert) > 0:
                    buyoffCertExpr = "buyoff_cert == \"{}\"".format(buyoffCert)
                    exprs.append(buyoffCertExpr)
                    properties.append(FlowNodeProperty(name="buyoff_cert", value=buyoffCert, type="str"))

                if len(exprs) > 0:
                    expr = exprs[0]
                    for next_expr in exprs[1:]:
                        expr = "And({}, {})".format(expr, next_expr)
                    args["expression"] = expr
                isData = True

            if type_name in property_map:
                for (webgme_attr, ir_name) in property_map[type_name].items():
                    if hasattr(node, webgme_attr):
                        attr_value = getattr(node, webgme_attr)
                        if attr_value is not None:
                            if isinstance(attr_value, str):
                                properties.append(FlowNodeProperty(name=ir_name, value=attr_value, type="str"))
                            elif isinstance(attr_value, bool):
                                properties.append(FlowNodeProperty(name=ir_name, value=attr_value, type="bool"))
                            elif isinstance(attr_value, int):
                                properties.append(FlowNodeProperty(name=ir_name, value=attr_value, type="int"))
                            elif isinstance(attr_value, float):
                                properties.append(FlowNodeProperty(name=ir_name, value=attr_value, type="float"))

            if parent is not None:
                args["processRef"] = parent["id"]

            if len(properties) > 0:
                args["properties"] = properties

            print("Creating node with args {}".format(args))
            if not isData:
                new_node = FlowNode(**args)
            else:
                new_node = DataNode(**args)

            nodes.append(new_node)
            if hasattr(node, "id"):
                node_id = node.id
                if node_id is None:
                    node_id = node_uuid
                node_map[node_id] = new_node
            else:
                node_map[node_uuid] = new_node

            if parent is None and isinstance(node, Process):
                parent = { "uuid": getattr(node, "bplElementUUID"),
                           "id": getattr(node, "bplProcessId") }

            if isinstance(node, SubProcess):
                parent = { "uuid": getattr(node, "bplElementUUID"),
                           "id": getattr(node, "bplElementId") }

            for child in self.all_children(node):
                self.convert_node(child, nodes, parent, node_map)
        else:
            if type_name not in connection_map:
                print("Unable to convert type: {}".format(type_name))

            if parent is None and isinstance(node, Process):
                parent = {"uuid": self.core.get_attribute(node, "bplElementUUID"),
                          "id": self.core.get_attribute(node, "bplProcessId")}
            if isinstance(node, SubProcess):
                parent = {"uuid": self.core.get_attribute(node, "bplElementUUID"),
                          "id": self.core.get_attribute(node, "bplElementId")}

            for child in self.all_children(node):
                self.convert_node(child, nodes, parent, node_map)

    def convert_input_output(self, parent, node, nodes, edges, connect_with_id):
        node_uuid = node.bplElementUUID
        if node_uuid in self.converted:
            return
        self.converted.add(node_uuid)

        type_name = type(node).__name__
        node_name = getattr(node, "name")

        print("Looking for input output in {} {}".format(type_name, node_name))

        if type_name == "InputParameter" or type_name == "OutputParameter":
            param_id = getattr(node, "bplElementId")
            param_uuid = getattr(node, "bplElementUUID")
            if param_id is None:
                param_id = param_uuid
            args = {"uuid": param_uuid, "type": "InputOutputBinding", "name": node_name, "id": node_name }
            for webgme_attr, ir_attr in data_attr_map.items():
                if hasattr(node, webgme_attr):
                    attr = getattr(node, webgme_attr)
                    if attr is not None:
                        if webgme_attr == "script":
                            if isinstance(attr, dict):
                                args[ir_attr] = attr["#text"]
                            else:
                                args[ir_attr] = attr
                        else:
                            args[ir_attr] = attr
                    else:
                        print("In node type {} can't find attr {}".format(type_name, webgme_attr))
            if args["name"] is None or args["name"] == "":
                args["name"] = node_name
            elif args["id"] is None or args["id"] == "":
                args["id"] = node_name

            print("Creating data node with {}".format(args))
            nodes.append(DataNode(**args))

            node_id = getattr(parent, "bplElementId")
            node_uuid = getattr(parent, "bplElementUUID")
            if node_id is None:
                node_id = node_uuid

            if type_name == "InputParameter":
                edge_type = FlowEdgeTypeEnum.INPUT_PARAMETER
            else:
                edge_type = FlowEdgeTypeEnum.OUTPUT_PARAMETER

            if connect_with_id:
                edges.append(FlowEdge(id=str(uuid.uuid4()), type=edge_type,
                                      sourceRef=node_id, targetRef=param_id))
            else:
                edges.append(FlowEdge(id=str(uuid.uuid4()), type=edge_type,
                                      sourceRef=node_uuid, targetRef=param_uuid))

        for child in self.all_children(node):
                self.convert_input_output(node, child, nodes, edges, connect_with_id)

    def convert_edges(self, node, edges, edge_map, connect_with_id):
        node_uuid = node.bplElementUUID
        if node_uuid in self.converted:
            return
        self.converted.add(node_uuid)

        if self.is_process(node):
            for child in node.bplElements:
                if type(child).__name__ == "StartEvent":
                    if hasattr(node, "bplElementId"):
                        from_id = getattr(node, "bplElementId")
                    else:
                        from_id = None
                    from_uuid = getattr(node, "bplElementUUID")
                    if from_id is None:
                        from_id = from_uuid
                    if hasattr(child, "bplElementId"):
                        to_id = getattr(child, "bplElementId")
                    else:
                        to_id = None
                    to_uuid = getattr(child, "bplElementUUID")
                    if to_id is None:
                        to_id = to_uuid

                    if connect_with_id:
                        edges.append(FlowEdge(id=str(uuid.uuid4()), type=FlowEdgeTypeEnum.PROCESS_FLOW,
                                              sourceRef=from_id, targetRef=to_id))
                    else:
                        edges.append(FlowEdge(id=str(uuid.uuid4()), type=FlowEdgeTypeEnum.PROCESS_FLOW,
                                              sourceRef=from_uuid, targetRef=to_uuid))

                    for grandchild in child.nexts:
                        self.convert_edges(grandchild, edges, edge_map, connect_with_id)
            return

        type_name = type(node).__name__

        if type_name in connection_map:
            from_node = getattr(node, "fromNode")
            to_node = getattr(node, "toNode")

            if hasattr(from_node, "bplElementId"):
                from_id = getattr(from_node, "bplElementId")
            else:
                from_id = None
            from_uuid = getattr(from_node, "bplElementUUID")
            if from_id is None:
                from_id = from_uuid
            if hasattr(to_node, "bplElementId"):
                to_id = getattr(to_node, "bplElementId")
            else:
                to_id = None
            to_uuid = getattr(to_node, "bplElementUUID")
            if to_id is None:
                to_id = to_uuid

            edge_uuid = getattr(node, "bplElementUUID")

            attrs = { "id": edge_uuid, "type": connection_map[type_name] }
            if connect_with_id:
                attrs["sourceRef"] = from_id
                attrs["targetRef"] = to_id
            else:
                attrs["sourceRef"] = from_uuid
                attrs["targetRef"] = to_uuid

            if hasattr(node, "conditionExpression"):
                conditionExpression = getattr(node, "conditionExpression")
            else:
                conditionExpression = None
            if conditionExpression is not None and conditionExpression != "":
                attrs["conditionExpression"] = conditionExpression

            properties = []

            if hasattr(node, "conditionTarget"):
                conditionTarget = getattr(node, "conditionTarget")
            else:
                conditionTarget = None
            if conditionTarget is not None and conditionTarget != "":
                properties.append(FlowNodeProperty(name="conditionTarget", value=conditionTarget, type="str"))

            if len(properties) > 0:
                attrs["properties"] = properties

            print("Creating {}".format(type_name))
            edges.append(FlowEdge(**attrs))
            edge_map[from_id] = from_node
            edge_map[to_id] = to_node

            self.convert_edges(to_node, edges, edge_map, connect_with_id)
            for child in to_node.nexts:
                self.convert_edges(child, edges, edge_map, connect_with_id)

        else:
            if isinstance(node, ConnectionBase):
                print("{} missing from connection map".format(type_name))

    def connect_resources(self, node, nodes, edges, connect_with_id):
        node_uuid = node.bplElementUUID
        if node_uuid in self.converted:
            return
        self.converted.add(node_uuid)

        if hasattr(node, "bplElementId"):
            from_id = getattr(node, "bplElementId")
        else:
            from_id = None
        from_uuid = getattr(node, "bplElementUUID")
        if from_id is None:
            from_id = from_uuid

        for child in self.all_children(node):
            child_type = type(child).__name__

            #            if child_type == "ResourceRequirement":
            #                for grandchild in self.core.load_children(child):
            #                    grandchild_type = self.core.get_attribute(self.core.get_meta_type(grandchild), "name")
            #                    to_uuid = self.core.get_attribute(grandchild, "bplElementUUID")
            #                    if grandchild_type == "ResourceRequirement":
            #                        edges.append(FlowEdge(id=str(uuid.uuid4()), type=FlowEdgeTypeEnum.RESOURCE_ROLE,
            #                                              sourceRef=from_uuid, targetRef=to_uuid))
            if isinstance(child, ResourceBase):
                    if child_type not in resource_type_map:
                        print("Unknown child type: {}".format(child_type))
                        continue
                    if hasattr(child, "bplElementName"):
                        child_name = getattr(child, "bplElementName")
                    else:
                        child_name = None
                    if child_name is None:
                        child_name = getattr(child, "name")

                    to_uuid = getattr(child, "bplElementUUID")
                    args = { "uuid": to_uuid, "type": resource_type_map[child_type], "name": child_name }

                    keyvalues = []
                    for kvp in self.all_children(child):
                        kvp_name = getattr(kvp, "name")
                        kvp_value = getattr(kvp, "value")
                        keyvalues.append(ResourceParameter(name=kvp_name, type="str", value=kvp_value))

                    keyvalues.append(ResourceParameter(name="description", type="str",
                                                       value=getattr(child, "name")))
                    keyvalues.append(ResourceParameter(name="quantity", type="float",
                                                       value=float(getattr(child, "quantity"))))
                    args["resourceParameters"] = keyvalues
                    print("Creating resource of type: ",args)
                    nodes.append(ResourceNode(**args))

                    if connect_with_id:
                        edges.append(FlowEdge(id=str(uuid.uuid4()), type=FlowEdgeTypeEnum.RESOURCE_ROLE,
                                              sourceRef=from_id, targetRef=to_uuid))
                    else:
                        edges.append(FlowEdge(id=str(uuid.uuid4()), type=FlowEdgeTypeEnum.RESOURCE_ROLE,
                                              sourceRef=from_uuid, targetRef=to_uuid))

            self.connect_resources(child, nodes, edges, connect_with_id)

    def main(self):
        for filename in sys.argv[1:]:
            self.generate_ir(filename)

    def generate_ir(self, filename):
        process = load_process(filename)

        if process is None or process.bplProcessName == "":
            filename = "model.json"
        else:
            filename = "model_"+process.bplProcessName+".json"

        connect_with_id = False

        nodes = []
        edges = []
        edge_map = {}
        node_map = {}
        self.convert_node(process, nodes, None, node_map)
        self.converted = set()
        self.convert_edges(process, edges, edge_map, connect_with_id)
        self.converted = set()
        self.connect_resources(process, nodes, edges, connect_with_id)
        self.converted = set()
        self.convert_input_output(process, process, nodes, edges, connect_with_id)

        processed_edges = set()
        roots = set()
        for node_uuid in node_map.keys():
            node = node_map[node_uuid]
            if hasattr(node, "processRef") and node.processRef is not None and node.processRef != "":
                continue
            print("Adding potential root {}".format(node))
            roots.add(node_uuid)

        for edge in edges:
            key = (edge.sourceRef, edge.targetRef)
            if key in processed_edges:
                print("Found duplicate edge {}".format(key))
                continue
            else:
                processed_edges.add(key)

            if edge.targetRef in roots:
                roots.remove(edge.targetRef)
            found_from = False
            found_to = False
            for node in nodes:
                if node.uuid == edge.sourceRef or (hasattr(node, "id") and node.id == edge.sourceRef):
                    found_from = True
                if node.uuid == edge.targetRef or (hasattr(node, "id") and node.id == edge.targetRef):
                    found_to = True
            if not found_from:
                print("Couldn't find source node {} for {} edge".format(edge.sourceRef, edge.type))
                print("Original node was type {}".format( type(edge_map[edge.sourceRef]).__name__))
            if not found_to:
                print("Couldn't find target node {} for {} edge".format(edge.targetRef, edge.type))
                print("Original node was type {}".format( type(edge_map[edge.targetRef]).__name__))

        print("There are {} roots".format(len(roots)))
        for root in roots:
            print("Root node {}".format(root))
        model = BLModel(nodes=nodes, edges=edges, process=process.bplProcessName, tdp=process.tdp)

        out_file = open(filename, "w")
        json.dump(model.model_dump(exclude_none=True), out_file, indent=2)
        out_file.close()

if __name__ == "__main__":
    obj = ExportIR()
    obj.main()

