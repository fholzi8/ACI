# Purpose : Create Leaf Switch Profiles. Usuallzy one per switch and one per vpc switch pair, also has RS to a dedicated
#           Leaf Interface Profile for both single and switch pair profiles
#           Create Leaf Interface Profiles, no interface selectors created of course
#
import csv
import datetime
import os

xmlfile  = './../xml/switch_profile.xml'
intpfile = './../xml/leaf_interface_profile.xml'
datafile = './../input/switch_profile.csv' #switch_profile tab


def FIELDNO(number):
    return number

# zero based csv col index
profileName = FIELDNO(0)
selectorName = FIELDNO(1)
from_ = FIELDNO(2)
to_ = FIELDNO(3)
policyGroup = FIELDNO(4)

#
# Class cinfraNodeP : switch profiles
#
class cinfraNodeP:
    def __init__(self):
        self.data = ""
        self.header = """
<polUni>
    <infraInfra>
        """

        self.footer = """
     </infraInfra>
</polUni>
"""
        self.xmlFabricNode = """
            <infraNodeP name="{profile_name}" descr="{profile_desc}">
                <infraRsAccPortP  tDn="uni/infra/accportprof-INTP_{int_selector_name}" />
                <infraLeafS name="{selector_name}" descr="{selector_desc}" type="range">
                    <infraNodeBlk name="{range_name}" descr="{range_desc}" from_="{from_}" to_="{to_}"/>
                </infraLeafS>
            </infraNodeP>
            """

    def processNode(self, row):
        if len(row[0]) == 0 or len(row[1]) == 0 or len(row[2]) == 0 or len(row[3]) == 0 or len(row[4]) == 0:
            return
        self.data += self.xmlFabricNode.format(
                                profile_name=row[profileName],
                                profile_desc=row[profileName],
                                selector_name=row[selectorName],
                                selector_desc=row[selectorName],
                                range_name=row[selectorName],
                                range_desc=row[selectorName],
                                from_=int(float(row[from_])),
                                to_=int(float(row[to_])),
                                int_selector_name=row[selectorName])

    def getXML(self):
        return self.header + self.data + self.footer
#
#
#
class cinfraAccPortP:
    def __init__(self):
        self.data = ""
        self.header = """
<polUni>
    <infraInfra>
        """

        self.footer = """
     </infraInfra>
</polUni>
"""
        self.xmlFabricNode = """
            <infraAccPortP descr="" name="INTP_{int_selector_name}"/>
            """

    def processNode(self, row):
        if len(row[selectorName]) == 0:
            return

        self.data += self.xmlFabricNode.format(
                                int_selector_name=row[selectorName])

    def getXML(self):
        return self.header + self.data + self.footer


#
#
#
def main():
    fNode = cinfraNodeP()
    fIntSelProf = cinfraAccPortP()

    with open(datafile) as csvfile:
        cf = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(cf) # header row
        for row in cf:
            fNode.processNode(row)
            fIntSelProf.processNode(row)

    if os.path.exists(xmlfile):
        os.remove(xmlfile)

    if os.path.exists(intpfile):
        os.remove(intpfile)

    # create output file
    xmlf = open(xmlfile, 'w')
    xmlf.write(fNode.getXML())
    xmlf.close()


    # create output file for interface selector profile
    xmlf = open(intpfile, 'w')
    xmlf.write(fIntSelProf.getXML())
    xmlf.close()

if __name__ == "__main__":
    main()