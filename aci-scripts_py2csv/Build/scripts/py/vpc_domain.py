# purpose: to create VPC Domains

import csv
import datetime
import os

xmlfile = './../xml/vpc_domain.xml'
datafile = './../input/vpc_domain.csv' #vpc_domain tab

def FIELDNO(number):
    return number

# zero based csv col index
vpcname = FIELDNO(0)
domainpolicy = FIELDNO(1)
nodeidleft = FIELDNO(2)
nodeidright = FIELDNO(3)
pairid = FIELDNO(4)

#
# Class Context
#
class cVPC:
    def __init__(self):
        self.data = ""
        self.header = """
    <fabricExplicitGEp name="{vpcname}" id="{pairid}">"""

        self.footer = """
    </fabricExplicitGEp>
"""
        self.xml = """
        <fabricNodePEp id="{nodeid}" name="{nodeid}" descr=""/>"""

    def processNode(self, row):

        if (len(row[vpcname]) == 0 or
            len(str(int(float(row[nodeidleft])))) == 0 or
            len(str(int(float(row[nodeidright])))) == 0 or
            len(str(int(float(row[pairid])))) == 0):
            return

        # start/open the fabricExplicitGEp
        self.data += self.header.format(vpcname=row[vpcname],pairid=(str(int(float(row[pairid])))))
        # add the policy
        self.data += """
        <fabricRsVpcInstPol tnVpcInstPolName="default"/>"""
        # add the vpc leaf pairs
        self.data += self.xml.format(nodeid=str(int(float(row[nodeidleft]))))
        self.data += self.xml.format(nodeid=str(int(float(row[nodeidright]))))
        # close fabricExplicitGEp
        self.data += self.footer

    def getXML(self):
        self.protPolHeader = '<fabricProtPol descr="" name="default" pairT="explicit">'
        self.protPolFooter = '</fabricProtPol>'
        return "<fabricInst>" + self.protPolHeader + self.data + self.protPolFooter + "</fabricInst>"

#
# main
#
def main():
    fNode = cVPC()

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