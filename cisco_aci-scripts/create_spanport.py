#!/usr/bin/env python
################################################################################
#                                                                              #
################################################################################
#                                                                              #                                                      
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
#    This work contains code from: https://github.com/datacenter/acitoolkit    #
#                                                                              #
################################################################################
description = '''
    Use this script to create a SPAN port destination and source.
    Configuration items can be found in dictionaries spanportd and spanports.
    You can also modify the credentials. 
'''

# Cisco ACI Cobra packages
import cobra.mit.access
import cobra.mit.naming
import cobra.mit.request
import cobra.mit.session
import cobra.model.span
from cobra.internal.codec.xmlcodec import toXMLStr

# ACI Toolkit packages
import acitoolkit.acitoolkit as ACI

# All the other stuff we might need.
import sys, json, getpass

credentials = dict(
    accessmethod = 'https',
    ip_addr = '',
    user = 'admin',
    # The password can be entered interactively.  It's ok to make this empty.
    password = ''
    )

spanportd = dict(
    # Destination info
    name = 'Dest-1',
    tenant = 'a1-Tenant',
    appprofile = 'my_three-tier-app',
    epg = 'www-access',
    ipdest = '192.168.10.10',
    rxipPrefix = '10.0.0.0/8'
    )

spanports = dict(
    name = 'Source-1',
    tenant = 'a1-Tenant',
    appprofile = 'my_three-tier-app',
    epg = 'www-access',
    # Possible directions: both, in, out
    trafficdir = 'both',
    # Needs to match the destination name
    dstname = spanportd['name']
    )

def hello_message():
    print "\nPlease be cautious with this application.  The author did very little error checking and can't ensure it will work as expected.\n"
    print description
    junk = raw_input('Press Enter/Return to continue.')
    return

def collect_admin(config):
    if config['accessmethod'] and config['ip_addr']:
        ip_addr = config['accessmethod'] + '://' + config['ip_addr']
    else:
        temp_addr = raw_input('IP Address or DNS name of APIC: ')
        ip_addr = config['accessmethod'] + '://' + temp_addr
        
    if config['user']:
        user = config['user']
    else:
        user = raw_input('Administrative Login: ')

    if config['password']:
        password = config['password']
    else:
        password = getpass.getpass('Administrative Password: ')

    return {'ip_addr':ip_addr, 'user':user, 'password':password}

def cobra_login(admin_info):
    # log into an APIC and create a directory object
    ls = cobra.mit.session.LoginSession(admin_info['ip_addr'], admin_info['user'], admin_info['password'])
    md = cobra.mit.access.MoDirectory(ls)
    md.login()
    return md

def toolkit_login(admin_info):
    session = ACI.Session(admin_info['ip_addr'], admin_info['user'], admin_info['password'])
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
        return session
    else:
        return False

    return False

def create_destination(md):
    # Don't touch this
    destdn = 'uni/tn-{}/ap-{}/epg-{}'.format(spanportd['tenant'], spanportd['appprofile'], spanportd['epg'])

    topDn = cobra.mit.naming.Dn.fromString('uni/tn-{}/destgrp-{}'.format(spanportd['tenant'], spanportd['name']))
    topParentDn = topDn.getParent()
    topMo = md.lookupByDn(topParentDn)

    spanDestGrp = cobra.model.span.DestGrp(topMo, ownerKey=u'', name=spanportd['name'], descr=u'', ownerTag=u'')
    spanDest = cobra.model.span.Dest(spanDestGrp, ownerKey=u'', name=spanportd['name'], descr=u'', ownerTag=u'')
    spanRsDestEpg = cobra.model.span.RsDestEpg(spanDest, tDn=destdn, ip=spanportd['ipdest'], dscp=u'unspecified', mtu=u'1518', flowId=u'1', srcIpPrefix=spanportd['rxipPrefix'], ttl=u'64')

    # commit the generated code to APIC
    c = cobra.mit.request.ConfigRequest()
    c.addMo(topMo)
    md.commit(c)

def create_source(md):
    # Don't touch this
    srcdn = 'uni/tn-{}/ap-{}/epg-{}'.format(spanports['tenant'], spanports['appprofile'], spanports['epg'])

    topDn = cobra.mit.naming.Dn.fromString('uni/tn-{}/destgrp-{}'.format(spanports['tenant'], spanports['name']))
    topParentDn = topDn.getParent()
    topMo = md.lookupByDn(topParentDn)

    spanSrcGrp = cobra.model.span.SrcGrp(topMo, ownerKey=u'', name=spanports['name'], descr=u'', adminSt=u'enabled', ownerTag=u'')
    spanSrc = cobra.model.span.Src(spanSrcGrp, ownerKey=u'', ownerTag=u'', dir=spanports['trafficdir'], descr=u'', name=spanports['name'])
    spanRsSrcToEpg = cobra.model.span.RsSrcToEpg(spanSrc, tDn=srcdn)
    spanSpanLbl = cobra.model.span.SpanLbl(spanSrcGrp, ownerKey=u'', tag=u'yellow-green', name=spanportd['name'], descr=u'', ownerTag=u'')

    # commit the generated code to APIC
    c = cobra.mit.request.ConfigRequest()
    c.addMo(topMo)
    md.commit(c)

def main(argv):
    hello_message()

    # Login and setup sessions  
    # admin_info contains the URL, Username, and Password (in clear text)
    # Use 'cobramd' as our session for Cobra interface 
    # Use 'session' as the session for the ACI Toolkit.
    
    admin_info = collect_admin(credentials)
    cobramd = cobra_login(admin_info)
    session = toolkit_login(admin_info)

    create_destination(cobramd)
    create_source(cobramd)

    print 'Script completed running'


if __name__ == '__main__':
    main(sys.argv)
