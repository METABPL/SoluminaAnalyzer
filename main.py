import sys
from SoluminaImport.load_solumina import load_process
import fault
from analyzers.resources import ResourceAnalyzer
from analyzers.path import PathAnalyzer
from analyzers.decisions import DecisionAnalyzer

def run():
    analyzers = [ ResourceAnalyzer(), PathAnalyzer(), DecisionAnalyzer() ]
    outfile = "faults.xml"
    fault_list = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--faults":
            outfile = sys.argv[i+1]
            i += 1
        else:
            model = load_process(sys.argv[i])
            for analyzer in analyzers:
                analyzer.analyze(model, fault_list)
        i += 1

    faults = fault.generate_fault_list(fault_list)
    with open(outfile, "w") as f:
        print(faults, file=f)

if __name__ == "__main__":
    run()

