# Purpose : To create fabric spine & leaf switch fabric members for pre-provisioning
#
# ** Note: script also creates an xml file which contains the oob and inb ip addresses for
#          oob & inb mgmt to import with mgmt xml
#
import csv
import datetime
import os

xmlfile =  './../xml/node_provisioning.xml'             # fabricNodeIdentPol
datafile = './../input/node_provisioning.csv'
oobfile =  './../xml/node_provisioning_InbOob.xml'      # mgmtMgmtP

def FIELDNO(number):
    return number

# zero based csv col index
name = FIELDNO(0)
serial = FIELDNO(1)
oobIp = FIELDNO(2)
oobGw = FIELDNO(3)
inbIp = FIELDNO(4)
inbGw = FIELDNO(5)
nodeId = FIELDNO(6)
devType = FIELDNO(7)    # device type spine/leaf
podId = FIELDNO(8)
role = FIELDNO(9)    # device type spine/leaf
site = FIELDNO(10)

fabricId = 1

#
# Class fabricNodeIdentPol : for pre/provisioning nodes
#
class cFabricNodeIdentPol:
    def __init__(self):
        self.data = ""
        self.header = """
<polUni>
    <ctrlrInst>
        <fabricNodeIdentPol>
        """

        self.footer = """
        </fabricNodeIdentPol>
    </ctrlrInst>
</polUni>
"""

        self.xmlFabricNode = """<fabricNodeIdentP name="{name}" nodeId="{nodeId}" podId="{podId}" role="{role}" serial="{serial}" fabricId="{fabricId}" />
        """

    def processNode(self, row):
        if len(row[name]) == 0 or len(row[nodeId]) == 0 or len(row[podId]) == 0 or len(row[role]) == 0 or len(row[serial]) == 0:
            return
        self.data += self.xmlFabricNode.format(
                                name=row[name],
                                nodeId=int(float(row[nodeId])),
                                podId=int(float(row[podId])),
                                role=row[role],
                                serial=row[serial],
                                fabricId=fabricId)

    def getXML(self):
        return self.header + self.data + self.footer

#
# Class mgmtInB : for Inband management
#
class cmgmtInB:
    def __init__(self):
        self.data = ""
        self.header = """
        <!-- Inband mgmt ipv4 -->
        <mgmtInB name="EPG_INB_MGMT">

        <!-- ADD APICS -->
        """

        self.footer = """
        </mgmtInB>
        """

        self.xmlNode = """
            <mgmtRsInBStNode addr="{ipv4Prefix}" gw="{ipv4Gw}" tDn="topology/pod-{podId}/node-{nodeId}"/>"""

    def processNode(self, row):
        if( len(row[inbIp]) == 0 or
            len(row[inbGw]) == 0 or
            len(row[podId]) == 0 or
            len(row[serial]) == 0 or
            len(row[nodeId]) == 0 or
            len(row[podId]) == 0 or
            len(row[role]) == 0):
            return

        self.data += self.xmlNode.format(
                                ipv4Prefix=row[inbIp]+'/24',
                                ipv4Gw=row[inbGw],
                                podId=int(float(row[podId])),
                                nodeId=int(float(row[nodeId])))

    def getXML(self):
        return self.header + self.data + self.footer

#
# Class mgmtOoB : for Inband management
#
class cmgmtOoB:
    def __init__(self):
        self.data = ""
        self.header = """
        <!-- OOB mgmt ipv4 -->
        <mgmtOoB name="default">

        <!-- ADD APICS -->
        """

        self.footer = """
        </mgmtOoB>
        """

        self.xmlNode = """
            <mgmtRsOoBStNode addr="{ipv4Prefix}" gw="{ipv4Gw}" tDn="topology/pod-{podId}/node-{nodeId}"/>"""

    def processNode(self, row):
        if( len(row[oobIp]) == 0 or
            len(row[oobGw]) == 0 or
            len(row[podId]) == 0 or
            len(row[serial]) == 0 or
            len(row[nodeId]) == 0 or
            len(row[podId]) == 0 or
            len(row[role]) == 0):
            return

        self.data += self.xmlNode.format(
                                ipv4Prefix=row[oobIp]+'/24',
                                ipv4Gw=row[oobGw],
                                podId=int(float(row[podId])),
                                nodeId=int(float(row[nodeId])))

    def getXML(self):
        return self.header + self.data + self.footer

def main():
    fNode = cFabricNodeIdentPol()
    fInb = cmgmtInB()
    foob = cmgmtOoB()

    with open(datafile) as csvfile:
        cf = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(cf) # header row
        for row in cf:
            fNode.processNode(row)
            fInb.processNode(row)
            foob.processNode(row)

    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    if os.path.exists(oobfile):
        os.remove(oobfile)

    # create output file
    xmlf = open(xmlfile, 'w')
    xmlf.write(fNode.getXML())
    xmlf.close()

    xmlf = open(oobfile, 'w')
    xmlf.write("""
    <polUni>
    <fvTenant name="mgmt">
    <mgmtMgmtP name="default">""")
    xmlf.write(fInb.getXML())
    xmlf.write("\n")
    xmlf.write(foob.getXML())
    xmlf.write("""
    </mgmtMgmtP>
    </fvTenant>
	</polUni>""")
    xmlf.close()

if __name__ == "__main__":
    main()