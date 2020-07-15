#
# Purpose: Creates tenants
#
import csv
import datetime
import os

xmlfile = './../xml/tenant.xml' # output
datafile = './../input/tenant.csv' # input

def FIELDNO(number):
    return number

# zero based csv col index
tenantname = FIELDNO(0)
descr = FIELDNO(1)
tags = FIELDNO(2)
mon_policy = FIELDNO(3)
ctrl_mgmt_policy = FIELDNO(4)
security_domain = FIELDNO(5)

#
# Class tenant
#
class cTenant:
    def __init__(self):
        self.data = ""
        self.header = """"""
        self.footer = """"""
        self.xml_dom = """
    <fvTenant name="{tenantname}" descr="{descr}" />"""

    # process row data
    def processNode(self, row):

        if len(row[tenantname]) == 0:
            return

        # create the tenant
        self.data += self.xml_dom.format(
                                tenantname = row[tenantname].strip(),
                                descr = row[descr].strip()
                                )

    # return xml data
    def getXML(self):
        return self.data + "\n"

#
# main
#
def main():
    fNode = cTenant()

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