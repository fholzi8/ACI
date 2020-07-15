#
# Purpose : Cretes Fabric VLAN Pools
#
import csv
import datetime
import os

xmlfile = './../xml/vlan_pool.xml' # output
datafile = './../input/vlan_pool.csv' # input

def FIELDNO(number):
    return number

# zero based csv col index
poolname = FIELDNO(0)
allocmode = FIELDNO(1)
vlanfrom = FIELDNO(2)
vlanto = FIELDNO(3)

#
# Class fvnsVlanInstP
#
class cfvnsVlanInstP:
    def __init__(self):
        self.data = {}

        # fvnsVlanInstP node
        self.header_ten = """
    <fvnsVlanInstP name="{poolname}" descr="{descr}" allocMode="{allocmode}">"""

        self.footer_ten = """
    </fvnsVlanInstP>
    """

        # encap block node
        self.xml_encapblk = """
            <fvnsEncapBlk name="{encapname}" descr="{descr}" from="vlan-{fromvlan}" to="vlan-{tovlan}" role="external"/>"""

    # process row of data from CSV file
    def processNode(self, row):

        # check if we already have an object for this fvnsVlanInstP,
        # if not create new fvnsVlanInstP
        if row[poolname] not in self.data.keys():
            self.data[row[poolname]] = self.header_ten.format(  poolname = row[poolname],
                                                                descr = "",
                                                                allocmode = row[allocmode])

        # add the encap block (fvnsEncapBlk) to the pool
        self.data[row[poolname]] += self.xml_encapblk.format(   encapname="VLAN_" + str(int(float(row[vlanfrom]))) + "_" + str(int(float(row[vlanto]))),
                                                                descr="",
                                                                fromvlan=int(float(row[vlanfrom])),
                                                                tovlan=int(float(row[vlanto])))

    # return xml data
    def getXML(self):
        self.output = ""
        for vlanp in self.data.keys():
            self.output += self.data[vlanp]
            self.output += self.footer_ten

        return self.output

#
# main
#
def main():
    fNode = cfvnsVlanInstP()

    with open(datafile) as csvfile:
        cf = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(cf) # header row
        for row in cf:
            fNode.processNode(row)

    if os.path.exists(xmlfile):
        os.remove(xmlfile)

    # create output file
    xmlf = open(xmlfile, 'w')
    xmlf.write("<polUni><infraInfra>")
    xmlf.write(fNode.getXML())
    xmlf.write("</infraInfra></polUni>")
    xmlf.close()

if __name__ == "__main__":
    main()