'''

'''
import json
import traceback


def is_valid_apic_data_returned(json_response):
    # TODO
    None

def get_card_port(intf_string):
     comp = intf_string.split("/")
     card_port = comp[1] + "/" + comp[2]
     return card_port

def get_node(intf_string):
     comp = intf_string.split("/")
     return str(comp[0])
