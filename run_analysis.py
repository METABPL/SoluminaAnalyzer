import sys
import re
from SoluminaImport.load_solumina import load_process
import fault
from analyzers.resources import ResourceAnalyzer
from analyzers.loop import LoopAnalyzer
from analyzers.decisions import DecisionAnalyzer
from analyzers.privs import PrivilegeAnalyzer
from analyzers.unreachable import ReachabilityAnalyzer
from analyzers.limits import LimitsAnalyzer

tdp_pattern = re.compile(".*/([Tt][Dd][Pp][0-9]*)/.*")
def run():
    analyzers = [ResourceAnalyzer(), LoopAnalyzer(), DecisionAnalyzer(),
                 PrivilegeAnalyzer(), ReachabilityAnalyzer(),
                 LimitsAnalyzer(),]
    outfile = "faults.xml"
    fault_list = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--faults":
            outfile = sys.argv[i+1]
            i += 1
        else:
            tdp = ""
            matches = tdp_pattern.match(sys.argv[i])
            if matches:
                tdp = matches.group(1)
            model = load_process(sys.argv[i])
            model.tdp = tdp.upper()
            for analyzer in analyzers:
                analyzer.analyze(model, fault_list)
        i += 1

    faults = fault.generate_fault_list(fault_list)
    with open(outfile, "w") as f:
        print(faults, file=f)

if __name__ == "__main__":
    run()

