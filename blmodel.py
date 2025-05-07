"""
Copyright (C) 2024 Peraton Labs - All Rights Reserved.
Proprietary and confidential. Unauthorized copy or use of this file, via
any medium or mechanism is strictly prohibited. The US government (only)
has unlimited rights to this software under contract N6523624C8007.
"""
from enum import Enum
from typing import Optional, Union, List
from pydantic import UUID4, BaseModel

# pylint: disable=too-few-public-methods

class AssigneeTypeEnum(str, Enum):
    """User tasks are assigned to groups or individuals."""
    GROUP      = "group"
    INDIVIDUAL = "individual"

class AssigneeNode(BaseModel):
    """User/group responsible for executing a user task.

    The name of the group or the individual assigned to a task
    is stored in the'name' attribute.
    """
    name: str
    type: str = "assignment"
    role: AssigneeTypeEnum = AssigneeTypeEnum.GROUP

class FlowNodeTypeEnum(str, Enum):
    """Types of activity elements."""
    GATEWAY_EVENT       = "eventBasedGateway"
    GATEWAY_COMPLEX     = "complexGateway"
    GATEWAY_PARALLEL    = "parallelGateway"
    GATEWAY_EXCLUSIVE   = "exclusiveGateway"
    GATEWAY_INCLUSIVE   = "inclusiveGateway"
    SUB_PROCESS         = "adHocSubProcess"
    SUB_PROCESS_ADHOC   = "adHocSubProcess"
    ACTIVITY_CALL       = "callActivity"
    EVENT_END           = "endEvent"
    EVENT_MESSAGE_END   = "messageEndEvent"
    EVENT_START         = "startEvent"
    EVENT_TIMER_START   = "timerStartEvent"
    EVENT_MESSAGE_START = "messageStartEvent"
    EVENT_CATCH         = "catchEvent"
    EVENT_THROW         = "throwEvent"
    EVENT_BOUNDARY      = "boundaryEvent"
    EVENT_CATCH_INTER   = "intermediateCatchEvent"
    EVENT_THROW_INTER   = "intermediateThrowEvent"
    TASK                = "task"
    TASK_SEND           = "sendTask"
    TASK_USER           = "userTask"
    TASK_SCRIPT         = "scriptTask"
    TASK_MANUAL         = "manualTask"
    TASK_SERVICE        = "serviceTask"
    TASK_RECEIVE        = "receiveTask"
    TASK_BUSINESS_RULE  = "businessRuleTask"
    PROCESS             = "process"
    SUBPROCESS          = "subProcess"

class TimerEventTypeEnum(str, Enum):
    """Types of timer events."""
    TIME_DATE     = "timeDate"
    TIME_CYCLE    = "timeCycle"
    TIME_DURATION = "timeDuration"

class BoundaryEventTypeEnum(str, Enum):
    """Types of boundary events."""
    BDE_ERROR       = "error"
    BDE_TIMER       = "timer"
    BDE_MESSAGE     = "message"
    BDE_COMPENSATE  = "compensate"
    BDE_CONDITIONAL = "conditional"

class FlowNodeProperty(BaseModel):
    """Support for typed properties."""
    name : str
    type : str = "str"
    value: str

class FlowNodeInstruction(BaseModel):
    """Operation/step instruction."""
    type     : str = "str"
    value    : Optional[str] = None
    object_id: Optional[str] = None

class FlowNode(BaseModel):
    """Base class for flow objects - events, activities, gateways.

    For script tasks, the 'scriptFormat' and 'script' attributes are used.

    For intermediate event involving time, the 'timerEvent' will indicate
    the specific timer event and the 'expression' will include time data.

    For call activities, the 'calledElement' value references the name of
    the subprocess that will be created when the call activity executes.
    """
    uuid           : Union[UUID4, str]
    id             : str
    name           : str
    type           : FlowNodeTypeEnum
    timerEvent     : Optional[TimerEventTypeEnum] = None
    boundaryEvent  : Optional[BoundaryEventTypeEnum] = None
    scriptFormat   : Optional[str] = None
    script         : Optional[str] = None
    assignments    : Optional[List[str]] = None
    variables      : Optional[List[str]] = None
    calledElement  : Optional[str] = None
    expression     : Optional[str] = None
    annotation     : Optional[str] = None
    documentation  : Optional[Union[str, list[FlowNodeInstruction]]] = None
    processRef     : Optional[str] = None
    messageRef     : Optional[str] = None
    eventRef       : Optional[str] = None
    userFormRef    : Optional[str] = None
    multiInstance  : Optional[bool] = None
    multiExpression: Optional[dict] = None
    properties     : Optional[list[FlowNodeProperty]] = None

class MessageNode(FlowNode):
    """A message node that references a message."""
    message_id : str

class ResourceTypeEnum(str, Enum):
    """Resource type associated with a resource."""
    ITEM      = "item"
    TOOL      = "tool"
    MACHINE   = "machine"
    MATERIAL  = "material"
    SKILL     = "skill"
    BUYOFF    = "buyoff"
    MM_OBJECT = "mmObject"
    DATA_COLL = "dataCollection"

class ResourceParameter(BaseModel):
    """A resource attribute/parameter."""
    name      : str
    type      : str
    value     : Union[str, bool, float, int]
    isRequired: bool = None

class ResourceNode(BaseModel):
    """A resource used by an activity/operation/step."""
    uuid              : Union[UUID4, str]
    name              : str
    type              : ResourceTypeEnum
    resourceParameters: list[ResourceParameter]

class DataSourceTypeEnum(str, Enum):
    """Types of data sources."""
    DATABASE  = "database"
    DOCUMENT  = "document"
    USER_FORM = "userForm"

class DataSourceNode(BaseModel):
    """The data source of an input/output element."""
    id           : str
    uuid         : Union[UUID4, str]
    name         : str
    type         : DataSourceTypeEnum
    field_id     : str
    field_name   : Optional[str] = None
    data_type    : Optional[str] = "string"
    expression   : Optional[str] = None
    documentation: Optional[str] = None

class DataNode(BaseModel):
    """Data nodes correspond to data input/output.

    The 'name' corresponds to the data item (attribute) name, while
    'expression' can be used for enforcing restrictions on the value.

    Data nodes may have scripts associated with them that set values
    or create new variables.

    For call activities, input/output mappings are used for values
    passed to/returned from them. The 'mappedTo' is used for the name
    of the corresponding called activity input/output variable.
    """
    id           : str
    uuid         : Union[UUID4, str]
    name         : str
    type         : str = "InputOutputBinding"
    sub_type     : str
    expression   : Optional[str] = None
    script       : Optional[str] = None
    scriptFormat : Optional[str] = None
    assignments  : Optional[List[Union[str, dict]]] = None
    mappedTo     : Optional[str] = None
    sourceRef    : Optional[Union[UUID4, str]] = None
    data_type    : Optional[str] = "string"
    properties   : Optional[list[FlowNodeProperty]] = None

# --------------------------------- Faults -------------------------------- #

class FaultCategoryEnum(str, Enum):
    """Fault categories."""
    DATA      = "Data management"
    TIME      = "Timing constraints"
    CONTROL   = "Execution sequence"
    RESOURCE  = "Resource usage"
    SECURITY  = "Security violation"
    ASSURANCE = "Information assurance"

class FaultTypeEnum(str, Enum):
    """Types of flaws."""
    CNTL_ONE_WAY        = "One-way function"
    CNTL_DEAD_END       = "Dead end"
    CNTL_NO_EXECUTION   = "No execution"
    CNTL_NO_TERMINATION = "No termination"
    CNTL_NON_REVERSIBLE = "Non-reversible action"
    CNTL_INCOMPLETE     = "Incomplete workflow"
    DATA_PROVENANCE     = "Loss of provenance"
    DATA_VALIDATION     = "No data validation"
    DATA_CONSISTENCY    = "Loss of data consistency"
    TIME_DEADLINE       = "Deadline violation"
    TIME_DURATION       = "Execution duration"
    RESOURCE_NO_ROLE    = "No resource assignment role"
    RESOURCE_DEPLETION  = "Resource depletion"
    RESOURCE_WRONG_ROLE = "Wrong resource assignment role"

class FaultNode(BaseModel):
    """BL flaw."""
    uuid          : Union[UUID4, str]
    type          : str = 'blFault'
    fault_type    : FaultTypeEnum
    fault_category: FaultCategoryEnum
    artifacts     : Optional[list[str]]	   # Documents, files, scripts, ...
    severity      : Optional[Union[float, str]] = 'low'
    processRef    : Optional[str] = None
    expressions   : Optional[list[str]] = None
    variables     : Optional[list[str]] = None
    execution_path: Optional[list[str]] = None
    fault_examples: Optional[List[str]] = None
    description   : Optional[str]

# --------------------------------- Edges --------------------------------- #

class FlowEdgeTypeEnum(str, Enum):
    """Types of activity elements."""
    ASSOCIATION          = "association"
    SEQUENCE_FLOW        = "sequenceFlow"
    MESSAGE_FLOW         = "messageFlow"
    RESOURCE_ROLE        = "resourceRole"
    SERVICE_FLOW         = "serviceFlow"      # serviceTask calling service
    PROCESS_FLOW         = "processFlow"      # callActivity calling subprocess
    BOUNDARY_FLOW        = "boundaryFlow"
    EVENT_FLOW           = "eventFlow"        # catch/throw event associations
    INPUT_PARAMETER      = "inputParameter"
    OUTPUT_PARAMETER     = "outputParameter"
    DATA_SOURCE          = "dataSource"
    USER_TASK_ASSIGNMENT = "assignment"       # userTask assignment
    FAULT_FLOW           = "faultFlow"

class FlowEdge(BaseModel):
    """An edge connecting nodes."""
    id                 : str
    name               : Optional[str] = None
    type               : FlowEdgeTypeEnum
    sourceRef          : Union[UUID4, str]
    targetRef          : Union[UUID4, str]
    conditionExpression: Optional[str] = None
    annotation         : Optional[str] = None
    properties         : Optional[list[FlowNodeProperty]] = None

# -------------------------------- BLModel -------------------------------- #

class BLModel(BaseModel):
    """The BL Model is an attributed graph."""
    version: str = "0.8.5"
    process: str = ""
    tdp: str = ""
    nodes: List[Union[FlowNode, DataNode, DataSourceNode,
                      ResourceNode, AssigneeNode, FaultNode]]
    edges: List[FlowEdge]
