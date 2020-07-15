import csv
import datetime
import os

xmlfile = './../xml/aaep.xml' # output
datafile = './../input/aaep.csv' # input

def FIELDNO(number):
    return number

# zero based csv col index
aepname = FIELDNO(0)
infravlan = FIELDNO(1)
physdomain = FIELDNO(2)
l3domain = FIELDNO(3)
vmmdomain = FIELDNO(4)
#
# Class domain
#
# <infraRsDomP tDn="uni/l3dom-{domainname}"/>
# <infraRsDomP tDn="uni/phys-{domainname}"/>
# <infraRsDomP tDn="uni/vmmp-VMware/dom-{domainname}"/>
#
# infraVLAN ??
#
class cAEP:
    def __init__(self):
        self.data = {}
        self.header = """
    <infraInfra>"""        
        self.footer = """
    </infraInfra>"""
    
        self.xml_aep_header = """
        <infraAttEntityP name="{aepname}">"""
        
        self.xml_dom = """
            <infraRsDomP tDn="{tDn}"/>"""
        
        self.xml_aep_footer = """
        </infraAttEntityP>
        """
        
    # process row data
    def processNode(self, row):

        if len(row[aepname]) == 0:
            return
               
        if len(row[l3domain]) > 0:
            self.tDn = "uni/l3dom-{domainname}".format(domainname=row[l3domain])            
        elif len(row[physdomain]) > 0:
            self.tDn = "uni/phys-{domainname}".format(domainname=row[physdomain])            
        elif len(row[vmmdomain]) > 0:
            self.tDn = "uni/vmmp-VMware/dom-{domainname}".format(domainname=row[vmmdomain])            
        else:
            self.tDn = ""            
            
        # check if we already have a object for this infraAttEntityP, if not create a new infraAttEntityP block
        if row[aepname] not in self.data.keys():
            self.data[row[aepname]] = self.xml_aep_header.format(aepname=row[aepname])
        
        # add the child nodes
        self.data[row[aepname]] += self.xml_dom.format(tDn=self.tDn)    
        
    # return xml data
    def getXML(self):
        self.output = ""
        
        for key in self.data.keys():
            self.output += self.data[key] + self.xml_aep_footer        
    
        return self.header + self.output + self.footer
        
# 
# main
# 
def main():
    fNode = cAEP()

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