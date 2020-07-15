import csv
import datetime
import os

xmlfile = './../xml/end_point_group.xml' # output
datafile = './../input/end_point_group.csv' # input

def FIELDNO(number):
    return number

# zero based csv col index
epgname = FIELDNO(0)
descr = FIELDNO(1)
tenant = FIELDNO(2)
app = FIELDNO(3)
bd = FIELDNO(4)
physdom = FIELDNO(5)
vmmdom = FIELDNO(6)

#
# Class AEPg
#
class cAEPg:
    def __init__(self):
        self.subnet = ""
        self.data = {}
        #self.data_app = {}

        # tenant node
        self.header_ten = """
    <fvTenant name="{tenantname}">"""

        self.footer_ten = """
    </fvTenant>
    """

        # application node
        self.header_app = """
        <fvAp name="{appname}">"""

        self.footer_app = """
        </fvAp>"""

        # epg node
        self.xml_epg = """
            <fvAEPg name="{epgname}" descr="{descr}">
                <fvRsBd tnFvBDName="{bdname}"/>
                {physdom}
                {vmmdom}
            </fvAEPg>
        """

        # physical & vmm domain relationships
        self.xml_epg_physdom = """<fvRsDomAtt tDn="uni/phys-{physdom_name}" instrImedcy="immediate" resImedcy="immediate"/>"""
        self.xml_epg_vmmdom  = """<fvRsDomAtt tDn="uni/vmmp-VMware/dom-{vmmdom_name}" instrImedcy="immediate" resImedcy="immediate"/>"""

    # process row of data from CSV file
    def processNode(self, row):

        # check if we already have a object for this fvTenant, if not create new tenant + app node blocks by having value being the <fvTenant name=" <fvAp......">
        if row[tenant] not in self.data.keys():
            self.data[row[tenant]] = dict()
            self.data[row[tenant]][row[app]] = self.header_ten.format(tenantname=row[tenant]) + self.header_app.format(appname=row[app])

        # check if we are adding an App to a previous tenant we have seen
        if row[app] not in self.data[row[tenant]].keys():
            self.data[row[tenant]][row[app]] = self.header_app.format(appname=row[app])

        # create the EPG

        # physical domain RS
        self.pdom = ""
        if len(row[physdom]) > 0:
            self.pdom = self.xml_epg_physdom.format(physdom_name=row[physdom])

        # vmm domain RS
        self.vdom = ""
        if len(row[vmmdom]) > 0:
            self.vdom = self.xml_epg_vmmdom.format(vmmdom_name=row[vmmdom])

        self.data[row[tenant]][row[app]] += self.xml_epg.format(epgname=row[epgname].strip(),
                                                                descr=row[descr],
                                                                tenantname=row[tenant],
                                                                bdname=row[bd],
                                                                physdom=self.pdom,
                                                                vmmdom=self.vdom)

    # return xml data
    def getXML(self):
        self.output = ""
        for tenant in self.data.keys():
            for app in self.data[tenant].keys():
                self.output += self.data[tenant][app]
                self.output.strip()
                self.output += self.footer_app
            self.output.strip()
            self.output += self.footer_ten

        #print(self.output)
        return self.output

#
# main
#
def main():
    fNode = cAEPg()

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