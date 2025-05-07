from analyzer import Analyzer
from SoluminaImport.class_model import *
from path_utils import enumerate_paths
import fault

class PathAnalyzer(Analyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, model, fault_list):
        paths = enumerate_paths(model)

        for curr_path in paths:
            if not isinstance(curr_path[-1], EndEvent):
                fault_list.append(
                    fault.Fault(process=model,
                                category="Execution sequence",
                                fault="No termination - Live lock",
                                activity=curr_path[-1].bplElementId,
                                path=curr_path,
                                severity="high",
                                outcomes=["Execution sequence has endless loop"]))