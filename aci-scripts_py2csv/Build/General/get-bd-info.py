from aci_helpers import *
from aci_rest import apic_comms
from helpers import *
import json

def main():

    print("\n\n\n\n")

    aci = apic_comms("USERNAME","PASSWORD","10.243.179.1")

    resp = aci.get_request("class/fvBD.json?rsp-subtree=children")

    non_mapped_bd = []

    for bd in resp["data"]["imdata"]:

        bd_temp = bd["fvBD"]["attributes"]["dn"]

        if "children" in bd["fvBD"]:

            fvRtBd_exists = False
            for item in bd["fvBD"]["children"]:  # list items each holding dict

                if "fvRtBd" in item:               # is this dict a ftRtBd
                    fvRtBd_exists = True
                    break

            if not fvRtBd_exists:
                non_mapped_bd.append(bd_temp)

        else:
            non_mapped_bd.append(bd_temp)

    print("\nBridge Domains With No EPG Use\n", "\n".join(non_mapped_bd))

if __name__ == "__main__":
    main()
