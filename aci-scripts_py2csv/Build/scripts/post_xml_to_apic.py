import sys
import os
#import xml.dom.minidom
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

try:
    hostname = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
except:
    print("Invalid Args (hostname username password)")
    sys.exit()

# apic 1 div
hostname = sys.argv[1] #"10.243.69.1"
print ("Controller %s, username is %s" % (hostname,username))

# Authenticate
def authentication(username,password):
    auth_XML = '<aaaUser name="{0}" pwd="{1}" />'.format(username,password)
    r = requests.post('https://{0}/api/aaaLogin.xml'.format(hostname), data=auth_XML, verify=False)
    if r.status_code != 200:
       print("authentication error {0}".format(r.content))
       sys.exit()
    dict_cookie = {'APIC-cookie':r.cookies['APIC-cookie']}
    return(dict_cookie)

# post XML
def postXMLData(xmlData, cookie):
    r = requests.post("https://{0}/api/mo/uni.xml".format(hostname), data=xmlData, cookies=cookie, verify=False)
    if r.status_code != 200:
       print("REST Post Failed With Status {0}".format(r.content))
    else:
       print("REST Post Successful")
    return

# main
def main():

    files = os.listdir("./xml/")
    files.sort(key=lambda x: x.lower())
    listing = []
    index = 1
    for f in files:
        s = f.split(".")
        if len(s) > 1 and s[1] == "xml":
                listing.append(f)
                print(str(index) +".",  f)
                index = index + 1

    print("\nSelect XML to POST to APIC...")
    opt = input("> ")
    if int(opt) in range(index):
        xmlfilename = listing[int(opt)-1]
        print(xmlfilename)
        cookie = authentication(username,password)
        with open("./xml/"+xmlfilename, 'r') as xml_file:
            content = xml_file.read()
            postXMLData(content, cookie)

if __name__ == "__main__":
    main()