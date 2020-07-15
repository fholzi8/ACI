# aci-multipod
<P>
There are four files here in two logical groups.   The two text files are the running configs of my IPN Nexus 9200 series standlone switches.  Use these as example to build up your own IPN devices.  Key areas to look at are setting up PIM, DHCP-Relay, MTU of 9150, and OSPF.

The two python scripts are those used in my own lab to setup the OSPF adjacency to IPN (<B>mpod-base.py</B>) and the other to setup the physical front-panel ports (i.e complete the MP-BGP control plane) on the ACI fabric used by the spines towards the IPN (<B>mpod-phys.py</B>).  Please note that the scripts use values that are <b>specific to my own setup</b>.  You will need to edit them to match the ports, ip addresses and settings in your own environment.  
<P>
Also, you must have already installed the <a href="https://developer.cisco.com/media/apicDcPythonAPI_v0.1/install.html">ACI COBRA SDK</a> on the system where you will run this. Can be downloaded also from the APIC.
  
The following diagram depicts the design of the IPN connectivity showing only the relevant devices for IPN, all other spine and all leaf switches are not shown for brevity.

<a href="https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD-IPN.png">

In this deployment, POD-1 and POD-2 happen to be in geographically diverse data centers where the four inter-connecting WAN links are 10Gbps Ethernet each although the POD’s could be in different campus locations or on different floors in a data center.
IPN L2
The only IPN requirements at layer 2 are to use VLAN 4 and increase the MTU. The VLAN requirement is for 802.1q between the spine and the IPN devices and to use encapsulation dot1q 4 on these sub-interfaces, additionally the system and L3 interface MTU must be set to 9150 as follows.



