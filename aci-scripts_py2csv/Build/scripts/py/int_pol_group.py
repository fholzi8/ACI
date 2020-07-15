import csv
import datetime
import os

xmlfile = './../xml/int_pol_group.xml'
datafile = './../input/int_pol_group.csv' #int_pol_group tab

def FIELDNO(number):
    return number

# Access : infraAccPortGrp
# vPC/PC : infraAccBndlGrp

# zero based csv col index
policyName = FIELDNO(0)           #
policyType = FIELDNO(1)         # Access | vPC | PC
lldp = FIELDNO(2)               # infraRsLldpIfPol : LLDP_ON
stp = FIELDNO(3)                # infraRsStpIfPol : STP_BPDU_GUARD_FILTER_ON
cdp = FIELDNO(4)                # infraRsCdpIfPol : CDP_ON
aaep = FIELDNO(5)               # infraRsAttEntP : no default
lag = FIELDNO(6)               # infraRsLacpPol : LAG_LACP_ACTIVE
storm = FIELDNO(7)              # infraRsStormctrlIfPol : STORMCONTROL_ALL_TYPES
link = FIELDNO(8)               # infraRsHIfPol : LINK_AUTONEG
monitor = FIELDNO(9)            # infraRsMonIfInfraPol : default
vlanscope = FIELDNO(10)         # infraRsL2IfPol : L2_VLAN_SCOPE_GLOBAL
mcp = FIELDNO(11)               # infraRsMcpIfPol : MCP_ON
                # infraRsL2PortSecurityPol : PORT_SECURITY_DISABLED
                # infraRsQosDppIfPol : DPP_NONE
                # infraRsQosEgressDppIfPol : DPP_NONE
                # infraRsQosIngressDppIfPol : DPP_NONE
                # infraRsFcIfPol : FC_F_PORT
                # infraRsQosPfcIfPol : PFC_AUTO
                # infraRsQosSdIfPol : SLOW_DRAIN_OFF_DISABLED
                # infraRsL2PortAuthPol : 8021X_DISABLED
                # coop
                # dwdm
                # macsec

#
# Class cinfraNodeP : switch profiles
#
class ipg:

    def __init__(self):
        self.data = ""
        self.header = """
<polUni>
    <infraInfra>
        """

        self.footer = """
     </infraInfra>
</polUni>
"""

        self.xmlFabricNode = """
            <infraNodeP name="{profile_name}" descr="{profile_desc}">
                <infraLeafS name="{selector_name}" descr="{selector_desc}" type="range">
                    <infraNodeBlk name="{range_name}" descr="{range_desc}" from_="{from_}" to_="{to_}"/>
                </infraLeafS>
            </infraNodeP>
            """

    def getXML(self):
        return self.header + self.data + self.footer

    def processNode(self, row):
        #if len(row[0]) == 0 or len(row[1]) == 0 or len(row[2]) == 0 or len(row[3]) == 0 or len(row[4]) == 0:
        #    return

        # interface policy
        self.temp = self.processPolicyType(row[policyType], row[policyName], "Automated")
        self.data += self.temp [0]
        self.policyFooter = self.temp[1]

        # link speed policy
        self.data += self.processLinkPolicy(row[link]) + "\n"

        # cdp policy
        self.data += self.processCDPPolicy(row[cdp]) + "\n"

        # mcp policy
        self.data += self.processMCPPolicy(row[mcp]) + "\n"

        # lldp policy
        self.data += self.processLLDPPolicy(row[lldp]) + "\n"

        # stp policy
        self.data += self.processSTPPolicy(row[stp]) + "\n"

        # storm policy
        self.data += self.processStormPolicy(row[storm]) + "\n"

        # vlan policy
        self.data += self.processVLANPolicy(row[vlanscope]) + "\n"

        # lag policy
        if row[policyType].upper() != "ACCESS":
            self.data += self.processLAGPolicy(row[lag]) + "\n"

        # port security policy
        self.data += self.processPortSecurityPolicy('default') + "\n"

        # DPP policy
        self.data += self.processDPPPolicy('default') + "\n"

        # DPP ingress policy
        self.data += self.processEgressDPPPolicy('default') + "\n"

        # DPP egress policy
        self.data += self.processIngressDPPPolicy('default') + "\n"

        # monitor policy
        self.data += self.processMonitoringPolicy('default') + "\n"

        # fc port policy
        self.data += self.processFcPortPolicy('default') + "\n"

        # pf pfc policy
        self.data += self.processPFCPolicy('default') + "\n"

        # slow drain fc policy
        self.data += self.processSlowDrainPolicy('default') + "\n"

        # dot1x policy
        self.data += self.processDot1xPolicy('default') + "\n"

        # lacp timers policy
        if row[policyType].upper() != "ACCESS":
            self.data += self.processLACPTimersPolicy(row[lag], row[policyName]) + "\n"

        # footers
        self.data += self.policyFooter
        self.data += '\n\n'


    def processPolicyType(self, policyType, name, desc):
        if policyType.upper() == "ACCESS":
            return '<{polType}  name="{polName}" descr="{polDesc}">'.format(polType="infraAccPortGrp", polName=name, polDesc=desc), "</infraAccPortGrp>"
        return '<{polType}  name="{polName}" descr="{polDesc}">'.format(polType="infraAccBndlGrp", polName=name, polDesc=desc), "</infraAccBndlGrp>"

    def processLinkPolicy(self, polName):
        self.temp = '<infraRsHIfPol tnFabricHIfPolName="{polName}"/>'
        if polName == "" or polName.lower() == "default":
            return self.temp.format(polName=LINK_AUTO)
        return self.temp.format(polName=polName)

    def processCDPPolicy(self,policyName):
        self.temp = '<infraRsCdpIfPol tnCdpIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="CDP_ON")
        return self.temp.format(name=policyName)

    def processMCPPolicy(self,policyName):
        self.temp = '<infraRsMcpIfPol tnMcpIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="MCP_ON")
        return self.temp.format(name=policyName)

    def processLLDPPolicy(self,policyName):
        self.temp = '<infraRsLldpIfPol tnLldpIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="LLDP_ON")
        return self.temp.format(name=policyName)

    def processSTPPolicy(self,policyName):
        self.temp = '<infraRsStpIfPol tnStpIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="STP_BPDU_GUARD_FILTER_ON")
        return self.temp.format(name=policyName)

    def processStormPolicy(self,policyName):
        self.temp = '<infraRsStormctrlIfPol tnStormctrlIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="STORMCONTROL_ALL_TYPES")
        return self.temp.format(name=policyName)

    def processVLANPolicy(self,policyName):
        self.temp = '<infraRsL2IfPol tnL2IfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="L2_VLAN_SCOPE_GLOBAL")
        return self.temp.format(name=policyName)

    def processLAGPolicy(self,policyName):
        self.temp = '<infraRsLacpPol tnLacpLagPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="LAG_STATIC_ON")
        return self.temp.format(name=policyName)

    def processPortSecurityPolicy(self,policyName):
        self.temp = '<infraRsL2PortSecurityPol tnL2PortSecurityPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="PORT_SECURITY_DISABLED")
        return self.temp.format(name=policyName)

    def processDPPPolicy(self,policyName):
        self.temp = '<infraRsQosDppIfPol tnQosDppPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="DPP_NONE")
        return self.temp.format(name=policyName)

    def processEgressDPPPolicy(self,policyName):
        self.temp = '<infraRsQosEgressDppIfPol tnQosDppPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="DPP_NONE")
        return self.temp.format(name=policyName)

    def processIngressDPPPolicy(self,policyName):
        self.temp = '<infraRsQosIngressDppIfPol tnQosDppPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="DPP_NONE")
        return self.temp.format(name=policyName)

    def processMonitoringPolicy(self,policyName):
        self.temp = '<infraRsMonIfInfraPol tnMonInfraPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="default")
        return self.temp.format(name=policyName)

    def processFcPortPolicy(self,policyName):
        self.temp = '<infraRsFcIfPol tnFcIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="FC_F_PORT")
        return self.temp.format(name=policyName)

    def processPFCPolicy(self,policyName):
        self.temp = '<infraRsQosPfcIfPol tnQosPfcIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="PFC_AUTO")
        return self.temp.format(name=policyName)

    def processSlowDrainPolicy(self,policyName):
        self.temp = '<infraRsQosSdIfPol tnQosSdIfPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="SLOW_DRAIN_OFF_DISABLED")
        return self.temp.format(name=policyName)

    def processDot1xPolicy(self,policyName):
        self.temp = '<infraRsL2PortAuthPol tnL2PortAuthPolName="{name}"/>'
        if policyName.lower() == "default" or policyType == "":
             return self.temp.format(name="8021X_DISABLED")
        return self.temp.format(name=policyName)

    def processLACPTimersPolicy(self,LACPpolicyName, policyName):
        if LACPpolicyName.find("LACP"):
            return """<infraAccBndlSubgrp descr="" name="OPG_LACP_TIMERS_{polName}">
    <infraRsLacpInterfacePol tnLacpIfPolName="LACP_FAST_32768"/>
	<infraRsLacpIfPol tnLacpIfPolName="LACP_FAST_32768"/>
</infraAccBndlSubgrp>
""".format(polName=policyName)
        return ""

        # coop, dwdm, xxx 3.1.1

#
# main
#
def main():
    cipg = ipg()

    with open(datafile) as csvfile:
        cf = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(cf) # header row
        for row in cf:
            cipg.processNode(row)

    if os.path.exists(xmlfile):
        os.remove(xmlfile)

    # create output file
    xmlf = open(xmlfile, 'w')
    xmlf.write(cipg.getXML())
    xmlf.close()

if __name__ == "__main__":
    main()