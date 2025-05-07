import io
from datetime import datetime, timezone
from hashlib import sha256
from SoluminaImport.class_model import Process

class Fault:
    def __init__(self, process=None, category=None, fault=None, artifacts=[],
                 tool=None, item=None, activity=None,
                 path=[], outcomes=[], severity=None):
        self.category = category
        self.fault = fault
        self.artifacts = artifacts
        self.tool = tool
        self.item = item
        self.process = process
        self.activity = activity
        self.path = path
        self.outcomes = outcomes
        self.severity = severity

def get_id(n):
    if isinstance(n, Process):
        return n.bplProcessId
    else:
        return n.bplElementId

def generate_fault_list(fault_list):
    outfile = io.StringIO()

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    print("<faultList formatVersion=\"1.2\" timestamp=\"{}\">".format(timestamp), file=outfile)

    for fault in fault_list:
        string_out = io.StringIO()
        print("    <teamName>TA1_metaBPL</teamName>", file=string_out)
        print("    <faultCategory>{}</faultCategory>".format(fault.category), file=string_out)
        print("    <faultType>{}</faultType>".format(fault.fault), file=string_out)
        print("    <artifacts>", file=string_out)
        if fault.process is not None and fault.process.source is not None and fault.process.source != "":
            print("      <artifact>{}</artifact>".format(fault.process.source), file=string_out)
        print("    </artifacts>", file=string_out)
        print("    <faultOriginLocation>", file=string_out)
        if fault.tool is not None:
            print("      <tool>{}</tool>".format(fault.tool), file=string_out)
        if fault.item is not None:
            print("      <item>{}</item>".format(fault.item), file=string_out)
        if fault.process is not None:
            print("      <process>{}</process>".format(fault.process.bplProcessName), file=string_out)
        if fault.activity is not None:
            print("      <activity>{}</activity>".format(fault.activity), file=string_out)
        print("    </faultOriginLocation>", file=string_out)
        print("    <faultOutcomes>", file=string_out)
        for outcome in fault.outcomes:
            print("      <faultOutcome>{}</faultOutcome>".format(outcome), file=string_out)
        print("    </faultOutcomes>", file=string_out)
        if len(fault.path) > 0:
            print("    <faultPath>{}</faultPath>".format(",".join([get_id(n) for n in fault.path])), file=string_out)
        print("    <faultSeverity>{}</faultSeverity>".format(fault.severity), file=string_out)
        print("  </fault>", file=string_out)
        string_contents = string_out.getvalue()
        fault_hash = sha256(string_contents.encode("utf-8")).hexdigest()
        print("  <fault id=\"TA1_metaBPL_UC1_{}_{}_Fault_{}\">".format(fault.process.tdp, fault.process.bplProcessName,fault_hash), file=outfile)
        print(string_contents, file=outfile, end="")
    print("</faultList>", file=outfile)

    return outfile.getvalue()