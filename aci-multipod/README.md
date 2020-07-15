# ACI-MultiPod
<P>
There are four files here in two logical groups.   The two text files are the running configs of my IPN Nexus 9200 series standlone switches.  Use these as example to build up your own IPN devices.  Key areas to look at are setting up PIM, DHCP-Relay, MTU of 9150, and OSPF.

The two python scripts are those used in my own lab to setup the OSPF adjacency to IPN (<B>mpod-base.py</B>) and the other to setup the physical front-panel ports (i.e complete the MP-BGP control plane) on the ACI fabric used by the spines towards the IPN (<B>mpod-phys.py</B>).  Please note that the scripts use values that are <b>specific to my own setup</b>.  You will need to edit them to match the ports, ip addresses and settings in your own environment.  
<P>
Also, you must have already installed the <a href="https://developer.cisco.com/media/apicDcPythonAPI_v0.1/install.html">ACI COBRA SDK</a> on the system where you will run this. Can be downloaded also from the APIC.
  
The following diagram depicts the design of the IPN connectivity showing only the relevant devices for IPN, all other spine and all leaf switches are not shown for brevity.

<a href="https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD-IPN.png">
 <img class="aligncenter size-full wp-image-362" src="https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD-IPN.png" alt="" width="1477" height="617" srcset="https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD-IPN.png 1477w, https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD-IPN.png 300w, https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD-IPN.png 768w, https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD-IPN.png 1024w" sizes="(max-width: 1477px) 100vw, 1477px" />
</a>

In this deployment, POD-1 and POD-2 happen to be in geographically diverse data centers where the four inter-connecting WAN links are 10Gbps Ethernet each although the POD’s could be in different campus locations or on different floors in a data center.

<h4>IPN L2</h4>
The only IPN requirements at layer 2 are to use VLAN 4 and increase the MTU. The VLAN requirement is for 802.1q between the spine and the IPN devices and to use encapsulation dot1q 4 on these sub-interfaces, additionally the system and L3 interface MTU must be set to 9150 as follows.


<h4>IPN L2</h4>
The only IPN requirements at layer 2 are to use VLAN 4 and increase the MTU. The VLAN requirement is for 802.1q between the spine and the IPN devices and to use encapsulation dot1q 4 on these sub-interfaces, additionally the system and L3 interface MTU must be set to 9150 as follows.


1	!
2	system jumbomtu 9150
3	!
4	interface Ethernetx...
5	 desc any interface carrying IPN traffic
6	 mtu 9150    
 
<h4>IPN L3
VRF</h4>
We have VRF’s configured on this deployment and this is also a recommended configuration by Cisco though not technically required but is good practice as we want to isolate the IPN traffic from interruption certainly if the IPN devices are used for other services and route table changes could break IPN connectivity. Using VRFs requires all interfaces (or sub-interfaces) including dedicated IPN loopbacks to be in the VRF as well as a separate OSPF process  in that VRF. The PIM RP address will be configured in the VRF too and is discussed in the multicast section in this post. The VRF in this deployment is called ‘fabric-mpod’, this VRF is not configured in the APIC, it only exists on the IPN devices encompassing VLAN 4.


1	vrf context fabric-mpod
2	!
3	interface loopback yy
4	  vrf member fabric-mpod
5	!
6	interface Ethernetx...
7	  vrf member fabric-mpod
8	!
9	router ospf a1
10	  vrf fabric-mpod
 
<h4>Addressing</h4>
IP addressing for the WAN and IPN POD to Spine  has been taken from a RFC 1918 range, the allocated range has been split in to three class C networks (/24), one each for:

	• POD-A IPN [10.96.1.0/24]
	• POD-B IPN [10.96.2.0/24]
	• WAN Interconnects [10.96.255.0/24]

Within the ACI fabric the IPN uses tenant ‘infra’ and VRF ‘overlay-1’ (translates to the VRF on the IPN devices ‘fabric-mpod’ – you could call the IPN devices VRF ‘overlay-1’ to keep it consistent but I don’t think its very descriptive). The address ranges used should not conflict with any other addressing in the ‘overlay-1’ VRF. The IPN devices have loopback created using host addresses from the start of the allocated pool for the POD they are located in. The loopback addresses on the spine switches are configured via the OSPF configuration on the APIC. Interconnects between the IPN devices and IPN & spine switches are allocated /30 addresses starting at the end of the allocated pool and work backwards for each allocation.

