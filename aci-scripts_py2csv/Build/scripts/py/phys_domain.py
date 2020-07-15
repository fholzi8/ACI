#
# Purpose: Creates the fabric physical domains (L3 or Physical), L2 External not currently coded.
#
import csv
import datetime
import os

xmlfile = './../xml/phys_domain.xml' # output
datafile = './../input/phys_domain.csv' # input

def FIELDNO(number):
    return number

# zero based csv col index
domainname = FIELDNO(0)
domaintype = FIELDNO(1)
vlanpoolname = FIELDNO(2)

#
# Class domain
#
# l3extDomP
# physDomP
#
class cDomain:
    def __init__(self):
        self.data = ""
        self.header = """"""
        self.footer = """"""
        self.xml_dom = """
    <{nodename} name="{domainname}">
            <infraRsVlanNs tDn="uni/infra/vlanns-[{vlanpoolname}]-static"/>
    </{nodename}>
"""

    # process row data
    def processNode(self, row):

        if len(row[domainname]) == 0 or len(row[domaintype]) == 0 or len(row[domaintype]) == 0:
            return

        # add the context info to the tenant
        self.nodetype = "physDomP"
        if row[domaintype].strip() == "external_l3":
            self.nodetype = "l3extDomP"

        self.data += self.xml_dom.format(
                                nodename = self.nodetype,
                                domainname = row[domainname].strip(),
                                vlanpoolname = row[vlanpoolname].strip()
                                )

    # return xml data
    def getXML(self):
        return self.data

#
# main
#
def main():
    fNode = cDomain()

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