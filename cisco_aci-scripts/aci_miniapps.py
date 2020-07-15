#!/usr/bin/env python

import acitoolkit.acitoolkit as ACI
import json
import sys
import getpass

try:
    import credentials
except:
    pass
        

session = ''
connection_status = 'Disconnected'
url = ''
login = ''
password = ''

def error_message(error):
    '''  Calls an error message.  This takes 1 list argument with 3 components.  #1 is the error number, #2 is the error text, 
         #3 is if the application should continue or not.  Use -1 to kill the application.  Any other number
         continues the application.  You must code in a loop and go back to where you want unless you are exiting.
    '''
    
    print '\n================================='
    print   '  ERROR Number: ' + str(error[0])
    print   '  ERROR Text: ' + str(error[1])
    print '=================================\n'
    
    if error[2] == -1:
        print 'Application ended due to error.\n'
        sys.exit()

def collect_login():
    if connected():
        return True

    global url, login, password
    
    print '\n\n'
    print '===================='
    print '==  Login to ACI  =='
    print '====================\n'

    try:
        url = credentials.URL
        login = credentials.LOGIN
        password = credentials.PASSWORD
        print 'Login information created from "credentials.py"'

    except:
        enter_login()
    
    print 'URL: ',url
    print 'User: ', login
    input = raw_input('\nPress Enter to continue or enter "q" to exit: ')
    if input == 'q':    
        return False
    
    print '\n'
    
    if create_login():
        return True
    
def enter_login():
    global url, login, password
    ''' Collect the information that we need to login to the system 
    '''
    url = raw_input('URL of the APIC: ')
    login = raw_input('Administrative Login: ')
    password = getpass.getpass('Administrative Password: ')

def create_login():
    global session, connection_status
    
    session = ACI.Session(url, login, password)
    response = session.login()
 
    if not response.ok:
        error_message ([1,'There was an error with the connection to the APIC.', -1])
        return False

    decoded_response = json.loads(response.text)

    if (response.status_code != 200):
        if (response.status_code == 401):
            connection_status = 'Username/Password incorrect'
            return False
        else:
            error_message ([decoded_response['imdata'][0]['error']['attributes']['code'], decoded_response['imdata'][0]['error']['attributes']['text'], -1])
            return False
    
    elif (response.status_code == 200):
        refresh = decoded_response['imdata'][0]['aaaLogin']['attributes']['refreshTimeoutSeconds']
        cookie = response.cookies['APIC-cookie']

        connection_status = 'Connected'
        return True
    else:
        return False
        
    
    return True

def collect_add_server_EPG():
    from acitoolkit.aciphysobject import Node

    if not collect_login():
        return False

    tenants_list = []
    apps_list = []
    epgs_list = []
    
    print '\n\n'
    print '====================================='
    print '==  Add physcial server to an EPG  =='
    print '=====================================\n'

    
    tenants = ACI.Tenant.get(session)
    for tenant in tenants:
        tenants_list.append((tenant.name))
    
    for a in range(len(tenants_list)):
        print str(a) + ': ' + tenants_list[a]

    input = raw_input('\nEnter the Tenant #: ')
    tenant_in = 99
    try:
        tenant_in = int(input)
    except:
        pass
    
    print '\n'
    apps = ACI.AppProfile.get(session, tenants[tenant_in])
    for app in apps:
        apps_list.append((app.name))
    
    if len(apps) <= 0:
        error_message([2,'There are no applications in this Tenant yet', 2])
        return
    for a in range(len(apps_list)):
            print str(a) + ': ' + apps_list[a]

    input = raw_input('\nEnter the Application Profile #: ')
    app_in = 99
    try:
        app_in = int(input)
    except:
        pass

    print '\n'
    
    epgs = ACI.EPG.get(session, apps[app_in], tenants[tenant_in])
    if len(epgs) <= 0:
        error_message([3,'There are no EPGs in this Application yet', 2])
        return
        
    for epg in epgs:
        epgs_list.append((epg.name))
        
    for a in range(len(epgs_list)):
        print str(a) + ': ' + epgs_list[a]

    input = raw_input('\nEnter the End Point Group #: ')
    epg_in = 99
    try:
        epg_in = int(input)
    except:
        pass

    # Select the leaf node
    print '\n'
    leafs = Node.get(session)
    
    if len(leafs) <= 0:
        error_message([3,'You have no Leafs!', 2])
        return

    leafs_list = []
    for leaf in leafs:
        if leaf.model == 'APIC': continue
        if leaf.role == 'spine': continue
        
        leafs_list.append((leaf.node))
    
    for a in range(len(leafs_list)):
        print str(a) + ': ' + leafs_list[a]

    input = raw_input('\nEnter the leaf number where the new server is located #: ')
    leaf_in = 99
    try:
        leaf_in = int(input)
    except:
        pass

    # Enter the interface
    print '\n'

    input = raw_input('\nEnter the interface number the new server is attached too #: ')
    if_in = 999
    try:
        if_in = int(input)
    except:
        pass

    # Enter the interface
    print '\n'

    input = raw_input('\nEnter the VLAN number (this interface will be a tagged interface but can be changed in the APIC GUI later): ')
    vlan_in = 999
    try:
        vlan_in = int(input)
    except:
        pass


    interface = {'type': 'eth',
                 'pod': '1', 
                 'node': str(leafs_list[leaf_in]), 
                 'module': '1', 
                 'port': str(if_in)}
    vlan = {'name': 'vlan' + str(vlan_in),
            'encap_type': 'vlan',
            'encap_id': str(vlan_in)}

    input = raw_input('\nPress Enter to continue.')
    create_add_server_EPG(tenants[tenant_in],apps[app_in],epgs[epg_in],interface,vlan)
    # def create_add_server_EPG(tenant_name, app_name, epg_name, interface, vlan):

def create_add_server_EPG(tenant, app, epg, interface, vlan):

    # Create the Tenant, App Profile, and EPG
    #     tenant = ACI.Tenant(tenant_name)
    #     app = ACI.AppProfile(app_name, tenant_name)
    #     epg = ACI.EPG(epg_name, app_name)

    if not connected():
        if not collect_login():
            return

    # Create the physical interface object
    intf = ACI.Interface(interface['type'],
                        interface['pod'],
                        interface['node'],
                        interface['module'],
                        interface['port'])

    # Create a VLAN interface and attach to the physical interface
    vlan_intf = ACI.L2Interface(vlan['name'], 
                                vlan['encap_type'], 
                                vlan['encap_id'])
    vlan_intf.attach(intf)

    # Attach the EPG to the VLAN interface
    epg.attach(vlan_intf)

    # Push it all to the APIC
    response = session.push_to_apic(tenant.get_url(),
                            tenant.get_json())

    decoded_response = json.loads(response.text)

    if not response.ok:
           print '%% Error: Could not push configuration to APIC'
           error_message ([decoded_response['imdata'][0]['error']['attributes']['code'], decoded_response['imdata'][0]['error']['attributes']['text'], -1])

def show_epgs():
    if not connected():
        if not collect_login():
            return

    ''' Takes no arguments and returns nothing.  Simple here to show you all of the
            Tenants, Application Profiles, and End Point Groups you have.'
    '''

    data = []
    tenants = ACI.Tenant.get(session)
    for tenant in tenants:
        apps = ACI.AppProfile.get(session, tenant)
        for app in apps:
            epgs = ACI.EPG.get(session, app, tenant)
            for epg in epgs:
                data.append((tenant.name, app.name, epg.name))

    # Display the data downloaded
    template = "{0:19} {1:20} {2:15}"
    print template.format("Tenant", "App Profile", "EPG")
    print template.format("------", "-----------", "---")
    for rec in data:
        print template.format(*rec)

    input = raw_input('\nPress Enter to continue')

def show_endpoints():
    if not connected():
        if not collect_login():
            return


    # Download all of the end points (devices connected to the fabric)
    # and store the data as tuples in a list
    data = []
    endpoints = ACI.Endpoint.get(session)
    for ep in endpoints:
        epg = ep.get_parent()
        app_profile = epg.get_parent()
        tenant = app_profile.get_parent()
        data.append((ep.mac, ep.ip, ep.if_name, ep.encap, tenant.name, app_profile.name, epg.name))
    
    # Display the data downloaded
    template = "{0:19} {1:17} {2:15} {3:10} {4:10} {5:18} {6:18}"
    print template.format("MACADDRESS",        "IPADDRESS",        "INTERFACE",     "ENCAP",      "TENANT", "APP PROFILE", "EPG")
    print template.format("-----------------", "---------------", "--------------", "----------", "------", "-----------", "---")
    for rec in data:
        print template.format(*rec)
        


    input = raw_input('\nPress Enter to continue ')

def find_ip():
    if not connected():
        if not collect_login():
            return

    print 'The following items are searchable:\n'
    print 'MACADDRESS          IPADDRESS         INTERFACE       ENCAP      TENANT     APP PROFILE        EPG'
    print '-----------------   ---------------   --------------  ---------- ------     -----------        ---'
    print '00:50:56:95:4A:38   192.168.77.40     eth 1/101/1/3   vlan-2116  Examples-1 Cool_Web_App       DB'
    print '\n\n\n'

    search_str = raw_input('\nEnter the string you would like to find (partial is ok): ')
    
    # Download all of the end points (devices connected to the fabric)
    # and store the data as tuples in a list
    data = []
    endpoints = ACI.Endpoint.get(session)
    for ep in endpoints:
        epg = ep.get_parent()
        app_profile = epg.get_parent()
        tenant = app_profile.get_parent()
        data.append((ep.mac, ep.ip, ep.if_name, ep.encap, tenant.name, app_profile.name, epg.name))
    
    # Display the data downloaded
    template = "{0:19} {1:17} {2:15} {3:10} {4:10} {5:18} {6:18}"
    print template.format("MACADDRESS",        "IPADDRESS",        "INTERFACE",     "ENCAP",      "TENANT", "APP PROFILE", "EPG")
    print template.format("-----------------", "---------------", "--------------", "----------", "------", "-----------", "---")
    for rec in data:
       if any(search_str.lower() in s.lower() for s in rec):
                print (template.format(*rec))
                
        #if ipaddr in rec[1]:
        #   print template.format(*rec)
        


    input = raw_input('\nPress Enter to continue ')
    
def get_interfaces():
    # Download all of the interfaces
    # and store the data as tuples in a list
    
    if not connected():
        if not collect_login():
            return

    data = []
    interfaces = ACI.Interface.get(session)
    for interface in interfaces:
      data.append((interface.if_name,
                   interface.porttype,
                   interface.adminstatus,
                   interface.speed,
                   interface.mtu))

    return data

def show_interfaces():
    if not connected():
        if not collect_login():
            return
        
    data = get_interfaces()
    
    # Display the data downloaded
    template = "{0:17} {1:6} {2:6} {3:7} {4:6}"
    print template.format("INTERFACE", "TYPE", "ADMIN", "SPEED", "MTU")
    print template.format("---------", "----", "-----", "-----", "___")
    for rec in data:
        print template.format(*rec)
    

    input = raw_input('\nPress Enter to continue ')

def show_basic_node():
    from acitoolkit.aciphysobject import Node
    if not connected():
        if not collect_login():
            return

    data = []

    # Get and print all of the items from the APIC
    items = Node.get(session)
    for item in items:
        if item.role == 'controller':
            item.role = 'APIC'
        data.append((item.serial,
                   item.role,
                   item.node,
                   item.health,
                   item.model,
                   item.oob_mgmt_ip,
                   item.tep_ip))
    
    newdata = sorted(data,key=lambda x: x[1])
    # Display the data downloaded
    template = "{0:15} {1:7} {2:6} {3:8} {4:17} {5:15} {6:15}"
    print template.format("Serial Number", "Role", "Node", "Health", "Model", "OOB Address", "TEP Address")
    print template.format("-------------", "-----", "----", "------", "---------------", "-------------", "---------------")
    for rec in newdata:
    
        print template.format(*rec)
    

def two_ports():
    if not connected():
        if not collect_login():
            return
        
        
    print '\n\n'
    print '========================='
    print '==  Connect Two Ports  =='
    print '=========================\n'


        
    # Basic Connectivity Example
    # Equivalent to connecting to ports to the same VLAN
    
    new_tenant = raw_input('Please enter a Tenant name: ')
    new_app = raw_input('Please enter an Application name: ')
    new_epg = new_app + '_EPG'

    # Create a tenant
    tenant = ACI.Tenant(new_tenant)

    # Create a Context and a BridgeDomain
    context = ACI.Context('VRF-1', tenant)
    context.set_allow_all()
    bd = ACI.BridgeDomain('BD-1', tenant)
    bd.add_context(context)

    # Create an App Profile and an EPG
    app = ACI.AppProfile(new_app, tenant)
    epg = ACI.EPG(new_epg, app)
    
    interfaces = ACI.Interface.get(session)

    for i in xrange(len(interfaces) - 1, -1, -1):
        if interfaces[i].porttype != 'leaf':
            del interfaces[i]
    
    interface1_in = interface2_in = -1
    
    while interface1_in == -1 or interface2_in == -1:
        for a in range(len(interfaces)):
            name = interfaces[a].if_name
            print str(a) + ': ' + name
        
        input1 = raw_input('\nEnter the first interface: ')
        input2 = raw_input('\nEnter the second interface: ')
        
        try:
            interface1_in = int(input1)
            interface2_in = int(input2)
            if (0 > interface1_in >len(interfaces)) or (0 > interface1_in >len(interfaces)):
                interface1_in = interface2_in == -1
        except:
            print '\nError: Please enter a number on the left side of the screen.'
                 
    # Attach the EPG to 2 interfaces using VLAN 5 as the encap
    if1 = interfaces[interface1_in]
    if2 = interfaces[interface2_in]
#     if1 = ACI.Interface('eth','1','101','1','62')
#     if2 = ACI.Interface('eth','1','101','1','63')
    vlan5_on_if1 = ACI.L2Interface('vlan5_on_if1', 'vlan', '5')
    vlan5_on_if2 = ACI.L2Interface('vlan5_on_if2', 'vlan', '5')
    vlan5_on_if1.attach(if1)
    vlan5_on_if2.attach(if2)
    epg.attach(vlan5_on_if1)
    epg.attach(vlan5_on_if2)

    resp = session.push_to_apic(tenant.get_url(), data=tenant.get_json())
    
    if resp.ok:
        print '\nSuccess'

    input = raw_input('\nPress Enter to continue ')

def display_menu(menu):
  while True:
    login = {1:'Login to APIC'}
    main = {2:'Create Application Profile', 3:'Create New Tenant w/ Login', 4:'Add physical server to EPG', 5:'Show all EPG'}

    print '\n\n'
    print '===================='
    print '==  ACI Mini Apps =='
    print '==    Main Menu   =='
    if connected():
        print '==    ' + connection_status + '   =='
    else:
        print '==  ' + connection_status + '  =='
    print '===================='
    print '0 or q:  Exit'
    print '1:  Login to APIC'
    # print '-:  Create Application Profile'
    # print '-:  Create New Tenant w/ Login'
    print '2:  Add physical server to an EPG'
    print '3:  Show all Tenants, App Profiles, and EPGs'
    print '4:  Show all Endpoints'
    print '5:  Show all Interfaces'
    print '6:  Connect two ports at Layer 2'
    print '7:  Find a host'
    print '8:  Show basic Node information'
    print '\n'
    
    

    input = raw_input('Enter Menu Item: ')
    int_in = 99
    try:
        int_in = int(input)
    except:
        pass
    
    if int_in == 0 or input.lower() == 'q' or input.lower() == 'exit' : sys.exit()
    if int_in == 1: collect_login()
    if int_in == 2: collect_add_server_EPG()
    if int_in == 3: show_epgs()
    if int_in == 4: show_endpoints()
    if int_in == 5: show_interfaces()
    if int_in == 6: two_ports()
    if int_in == 7: find_ip()
    if int_in == 8: show_basic_node()
    
def connected():
    if connection_status == 'Connected':
        return True
    else:
        return False

def main(): 
    menu = 'main'
    display_menu(menu)

if __name__ == '__main__':
    main()
