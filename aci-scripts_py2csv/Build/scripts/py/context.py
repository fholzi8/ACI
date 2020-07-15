
import csv
import datetime
import os

xmlfile = './../xml/context.xml'
datafile = './../input/context.csv' #switch_profile tab

def FIELDNO(number):
    return number

# zero based csv col index
contextname = FIELDNO(0)
tenantname = FIELDNO(1)
descr = FIELDNO(2)
enforcement = FIELDNO(3)

#
# Class Context
#
class cContext:
    def __init__(self):
        self.data = {}
        self.header = """
    <fvTenant name="{tenantName}">"""

        self.footer = """
    </fvTenant>
"""

        self.xml = """
        <fvCtx name="{contextName}" descr="{contextDescr}" pcEnfPref="{enforcePolicy}"/>"""

    def processNode(self, row):
        global enforcement
        if len(row[contextname]) == 0 or len(row[tenantname]) == 0 or len(row[enforcement]) == 0:
            return

        if row[enforcement] != "unenforced" and row[enforcement] != "enforced":
            self.enforce = "enforced"
        else:
            self.enforce = row[enforcement]

        # check if we already have a object for this tenant, if not create a new tenant block
        if row[tenantname] not in self.data.keys():
            self.data[row[tenantname]] = self.header.format(tenantName=row[tenantname])

        # add the context info to the tenant
        self.data[row[tenantname]] += self.xml.format(
                                contextName=row[contextname],
                                contextDescr=row[descr],
                                enforcePolicy=self.enforce
                                )

    def getXML(self):
        self.output = ""
        for key in self.data.keys():
            self.output += self.data[key] + self.footer

        return self.output

#
# main
#
def main():
    fNode = cContext()

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