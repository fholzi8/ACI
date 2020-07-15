import csv
import datetime
import os

xmlfile = './../xml/app_profile.xml'
datafile = './../input/app_profile.csv' 

def FIELDNO(number):
    return number

# zero based csv col index
tenantname = FIELDNO(0)
appname = FIELDNO(1)
        
#
# Class App
#
class cApp:
    def __init__(self):
        self.data = {}
        self.header = """
    <fvTenant name="{tenantname}">"""
        
        self.footer = """
    </fvTenant>
"""
        self.xml = """
        <fvAp name="{appname}"/>"""

    def processNode(self, row):
        
        # check if we already have a object for this tenant, if not create a new tenant block
        if row[tenantname] not in self.data.keys():
            self.data[row[tenantname]] = self.header.format(tenantname=row[tenantname])
            
        # add the context info to the tenant
        self.data[row[tenantname]] += self.xml.format(
                                appname=row[appname]
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
    fNode = cApp()

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