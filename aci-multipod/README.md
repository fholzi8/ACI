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


	!
	system jumbomtu 9150
	!
	interface Ethernetx...
	 desc any interface carrying IPN traffic
	 mtu 9150    
 
<h4>IPN L3
VRF</h4>
We have VRF’s configured on this deployment and this is also a recommended configuration by Cisco though not technically required but is good practice as we want to isolate the IPN traffic from interruption certainly if the IPN devices are used for other services and route table changes could break IPN connectivity. Using VRFs requires all interfaces (or sub-interfaces) including dedicated IPN loopbacks to be in the VRF as well as a separate OSPF process  in that VRF. The PIM RP address will be configured in the VRF too and is discussed in the multicast section in this post. The VRF in this deployment is called ‘fabric-mpod’, this VRF is not configured in the APIC, it only exists on the IPN devices encompassing VLAN 4.


	vrf context fabric-mpod
	!
	interface loopback yy
	  vrf member fabric-mpod
	!
	interface Ethernetx...
	  vrf member fabric-mpod
	!
	router ospf a1
	  vrf fabric-mpod
 
<h4>Addressing</h4>
IP addressing for the WAN and IPN POD to Spine  has been taken from a RFC 1918 range, the allocated range has been split in to three class C networks (/24), one each for:

	• POD-A IPN [10.96.1.0/24]
	• POD-B IPN [10.96.2.0/24]
	• WAN Interconnects [10.96.255.0/24]

Within the ACI fabric the IPN uses tenant ‘infra’ and VRF ‘overlay-1’ (translates to the VRF on the IPN devices ‘fabric-mpod’ – you could call the IPN devices VRF ‘overlay-1’ to keep it consistent but I don’t think its very descriptive). The address ranges used should not conflict with any other addressing in the ‘overlay-1’ VRF. The IPN devices have loopback created using host addresses from the start of the allocated pool for the POD they are located in. The loopback addresses on the spine switches are configured via the OSPF configuration on the APIC. Interconnects between the IPN devices and IPN & spine switches are allocated /30 addresses starting at the end of the allocated pool and work backwards for each allocation.

<h4>Routing</h4>
OSPF is used on the IPN between the connected spine switches and IPN devices, also between the IPN devices in all pods. The diagram below shows area 0 being used across the IPN and spine devices. Other OSPF areas can be used but they MUST be configured as ‘normal’ areas, in other words do not configure them as stub or NSSA areas for example.  

<a href="https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD_IPN_OSPF.png">
 <img class="aligncenter size-full wp-image-362" src="https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD_IPN_OSPF.png" alt="" width="1477" height="617" srcset="https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD_IPN_OSPF.png 1477w, https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD_IPN_OSPF.png 300w, https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD_IPN_OSPF.png 768w, https://github.com/fholzi8/ACI/blob/master/aci-multipod/ACI_MPOD_IPN_OSPF.png 1024w" sizes="(max-width: 1477px) 100vw, 1477px" />
</a>

The links (interfaces) between the IPN devices and the spine switches must have the following OSPF configuration on the interfaces (as discussed, these are actually the sub-interfaces for VLAN-4).

	ip ospf network point-to-point
	ip ospf mtu-ignore
	ip router ospf a1 area 0.0.0.0      

As shown in the code snippet, the network type between the IPN device and the spin device must be point to point and ignore MTU must be turned on. These settings are important for these links, for the IPN to IPN links, these can be configured with a network type that is relevant to the … network type ! – this is just normal OSPF configuration here with the above caveats with area type. In addition a dedicated loopback is used for the VRF and the PIM RP. Each IPN device must have this dedicated loopback active in the same OSPF area as the links. The following config shows the loopbacks for a IPN device acting as a primary RP.

	interface loopback96
	  vrf member fabric-mpod
	  ip address 10.96.1.1/32
	  ip router ospf a1 area 0.0.0.0
	  ip pim sparse-mode
	 
	interface loopback100
	  desc Dedicated RP Loopback
	  vrf member fabric-mpod
	  ip address 10.96.1.233/32
	  ip router ospf a1 area 0.0.0.0
	  ip pim sparse-mode

<h4>Multicast</h4>
Cisco ACI requires\recommends (works best with) bi-dir multicast as we have many sources and many receivers. Referring to the diagram above, all the links require ‘ip pim sparse-mode‘ configured including the dedicated loopback(s). The VRF itself requires the RP configured for the group 225.0.0/8 which is used by the bridge domains for BUM traffic (discussed in the next section). The 239.255.255.240/28 is used for fabric specific purposes, for example the 239.255.255.240/32 address is used for arp gleaning. The configuration for the RP on a IPN device is shown below, the RP IP address being the IP address on the dedicated loopback in the multi pod VRF.

	ip pim mtu 9000 
	vrf context fabric-mpod 
	    ip pim rp-address 10.96.1.233 group-list 225.0.0.0/8 bidir 
	    ip pim rp-address 10.96.1.233 group-list 239.255.255.240/28 bidir 

What is important to note is that bi-dir has no native solution for redundancy. To implement redundancy we create use the concept of Redundant Phantom Rendezvous Points, we use the single IP address for the RP configuration on each of the IPN devices as shown above. This configuration is discussed later in this post.
Cisco ACI uses a multicast address per bridge domain to encapsulate BUM traffic to be sent to other TEPs (Leaf Switches) across the fabric. This concept is extended over the IPN for multi pod deployments. If we take a look at an example bridge domain on the APIC which is active in both pods, we see on the “Advanced/Troubleshooting” tab that we have a system assigned multicast address of 225.0.13.224/32 which is unique to this bridge domain.


