import csv
import datetime
import os

xmlfile = './../xml/bridge_domain.xml' # output
datafile = './../input/bridge_domain.csv' # input

def FIELDNO(number):
    return number

# zero based csv col index
tenantname = FIELDNO(0)
contextname = FIELDNO(1)
bdname = FIELDNO(2)
descr = FIELDNO(3)

# always regular
bdtype = FIELDNO(4)

# Subnet GW IP, required for ARP Gleaning
bdgwip = FIELDNO(5)

# L2 Unknown Unicast: HW Proxy or flood
# For Flooding option - the ARP Flooding feature must be enabled (default Hardware Proxy)
l2unknown = FIELDNO(8)

# L3 Unknown Multicast Flooding: proxy or flood (default )
l3unknown = FIELDNO(9)

# Multi Destination Flooding: Flood in BD, Drop, Flood in Encap (default Flood in BD)
multidestflood  = FIELDNO(10)

# enable/disable : This option transforms broadcast ARP requests into unicast packets.
# For this feature to work, you need to enable IP routing because the mapping database
# must be populated with the IP addresses of the endpoints.
# L2 Unknown Unicast Hardware proxy must be enabled too. (default no)
arpflood = FIELDNO(11)

# enable/disable l3 routing
# Will not learn any IP address as an endpoint, will not be seen in show endpoint ip (default yes)
routing = FIELDNO(12)


#limitIpLearnToSubnets                      #

#ipLearning                                 #

# Its possible to have 'L2 Unknown Unicast' set to 'HW Proxy' with 'IP Routing' disabled if we have a
# subnet address configured. This subnet address will be used for ARP Gleaning and
# for this ARP gleaning to work we need a subnet address to arp from the fabric

#
# Class bd
#
class cBD:
    def __init__(self):
        self.warning = False
        self.subnet = ""
        self.data = {}
        self.header = """
    <fvTenant name="{tenantName}">"""

        self.footer = """
    </fvTenant>
"""
        self.xml_bd = """
        <fvBD
            name="{bdname}"
            descr="{descr}"
            type="regular"
            unkMacUcastAct="{unkMacUcastAct}"
            unkMcastAct="{unkMcastAct}"
            multiDstPktAct="{multiDstPktAct}"
            arpFlood="{arpflood}"
            unicastRoute="{unicastrouting}"
            ipLearning="yes"
            limitIpLearnToSubnets="yes">
                <fvRsCtx tnFvCtxName="{contextname}"/>{subnet}
        </fvBD>
        """

        # if bdtype = "L3"
        self.xml_subnet = """
                <fvSubnet name="" descr="" ctrl="nd" ip="{bdgwip}" preferred="no" scope="private" virtual="no"/>"""


    def processNode(self, row):

        self.subnet = ""
        self._l2unknown = row[l2unknown].strip()
        self._arpflood = row[arpflood].strip()
        self._routing = row[routing].strip()
        self._l3unknown = row[l3unknown].strip()
        self._multidestflood = row[multidestflood].strip()

        if self.warning == False:
            print("\n\n *** WARNING: Overriding Given Values for BD L2 Migration..\n\n")
            self.warning = True

        # override some values for the migration L2 state
        self._l2unknown = "flood"       # flood so we use traditional arp methods
        self._arpflood = "yes"          # must enable arp flooding for flooding above (required)
        self._routing = "no"            # disable routing as legacy routing initally

        #if len(row[contextname]) == 0 or len(row[tenantname]) == 0 or len(row[bdname]) == 0:
        #    return

        # check if we already have a object for this tenant, if not create a new tenant block
        if row[tenantname] not in self.data.keys():
            self.data[row[tenantname]] = self.header.format(tenantName=row[tenantname])


        # subnet L3 gw case check
        if self._routing == "yes" and len(row[bdgwip]) > 0:
            self.subnet = self.xml_subnet.format(bdgwip=row[bdgwip].strip())
        else:
            self.subnet = ""

        # add the context info to the tenant
        #self._arpflood = "no"
        if row[l2unknown].strip() == "flood":
            self._arpflood = "yes"

        self.data[row[tenantname]] += self.xml_bd.format(
                                bdname = row[bdname].strip(),
                                descr = row[descr].strip(),
                                unicastrouting = self._routing,
                                contextname = row[contextname].strip(),
                                unkMacUcastAct = self._l2unknown,
                                arpflood = self._arpflood,
                                unkMcastAct = self._l3unknown,
                                multiDstPktAct = self._multidestflood,
                                subnet = self.subnet,
                                tenantname = row[tenantname].strip()
                                )

    # return xml data
    def getXML(self):
        self.output = ""
        for key in self.data.keys():
            self.output += self.data[key] + self.footer

        return self.output

#
# main
#
def main():
    print("/n/n *** fvSubnet scope & l3out needs adding *** poss during L3 migration instead")
    fNode = cBD()

    with open(datafile) as csvfile:
        cf = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(cf) # header row
        for row in cf:
            fNode.processNode(row)

    if os.path.exists(xmlfile):
        os.remove(xmlfile)

    # create output file
    xmlf = open(xmlfile, 'w')
    xmlf.write("<polUni>")
    xmlf.write(fNode.getXML())
    xmlf.write("</polUni>")
    xmlf.close()

if __name__ == "__main__":
    main()