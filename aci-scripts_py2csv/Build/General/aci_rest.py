"""

"""

from aci_rest import *
from aci_helpers import *



import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import json
import _thread
import time

#
# apic_comms class
#
# TODO UPDATE TO HELPER CLASSES
class apic_comms:

    def __init__(self, username, password, hostname):
        self.login_data = {"result": "none"}
        self.base_url = "https://{0}/api/".format(hostname)
        self.username = username
        self.password = password
        self.hostname = hostname
        self.authenticate()

    def __del__(self):
        self.logout()

    #   Authenticate
    def authenticate(self):

        auth = {"aaaUser": {"attributes": {"name": "{0}".format(self.username),"pwd" : "{0}".format(self.password)}}}
        r = requests.post('{0}aaaLogin.json'.format(self.base_url), data=json.dumps(auth), verify=False, timeout=15)
        #print(json.dumps(json.loads(r.content), indent=2))

        json_response = {}
        if r.status_code < 200 or r.status_code > 299:
            json_response = {
                "result": "failed",
                "APIC-cookie":"",
                "error_text": "{0}".format( r.content )
                }
            # save
            self.login_data = json_response
            init_refresh()
        else:
            data = json.loads(r.content)
            json_response = {
                "result": "success",
                "APIC-cookie":r.cookies["APIC-cookie"]
                }
            try:
                json_response["data"] = data["imdata"][0]["aaaLogin"]["attributes"]
            except:
                return error_json("key Error In Autentication")
            # save
            self.login_data = json_response

        #print(json.dumps(self.login_data, indent=2))
        return json_response

    def logout(self):
        requests.get('{0}aaaLogout.json'.format(self.base_url), cookies={ "APIC-cookie" : self.login_data["APIC-cookie"] },verify=False)


    def init_refresh(self):
        #print(json.dumps(self.login_data, indent=2))
        _thread.start_new_thread( self.refresh_login, (self.login_data["data"]["restTimeoutSeconds"], ) )
        #_thread.start_new_thread( self.refresh_login, (1, ) )


    def refresh_login(self, refreshTimeoutSeconds):

        #print(json.dumps(self.login_data, indent=2))
        while True:
            time.sleep(int(refreshTimeoutSeconds))
            r = requests.get('{0}aaaRefresh.json'.format(self.base_url), cookies={ "APIC-cookie" : self.login_data["APIC-cookie"] }, verify=False)

            json_response = {}
            if r.status_code != 200:
                #print("NOT ok")
                json_response = {
                    "result": "failed",
                    "APIC-cookie":"",
                    "error_text": "{0}".format( r.content )
                    }
            else:
                #print("ok")
                data = json.loads(r.content)
                json_response = {
                    "result": "success",
                    "APIC-cookie":r.cookies["APIC-cookie"]
                    }
                json_response["data"] = data["imdata"][0]["aaaLogin"]["attributes"]
                # save
                self.login_data = json_response

        return json_response


    # get request
    def get_request(self, url):

        if self.login_data["result"] != "success":
            return {
                "result": "failed",
                "error_text": "Not logged into APIC"
                }
        # send request
        r = requests.get(self.base_url + url, cookies={ "APIC-cookie" : self.login_data["APIC-cookie"] }, verify=False, timeout=15)
        content = json.loads(r.content)
        json_response = {}
        if r.status_code < 200 or r.status_code > 299:
            json_response = {
                "result": "failed",
                "error_text": "REST Get Failed With Status {0} {1}".format( r.status_code, content )
                }

        elif "error" in content["imdata"]:
                json_response = failed_json(content)

        else:
            json_response["data"] = json.loads(r.content)
            json_response["result"] = "success"
            json_response["status_code"] = "{0}".format(r.status_code)

        return json_response

    # post request
    def post_request(self, url, post_data):
        raise
        return #SAFE

        if self.login_data["result"] != "success":
            return {
                "result": "failed",
                "error_text": "Not logged into APIC"
                }

        r = requests.post(url, data=post_data, cookies={ "APIC-cookie" : self.login_data["APIC-cookie"] }, verify=False, timeout=15)

        json_response = {}
        if r.status_code < 200 or r.status_code > 299:
            json_response = {
                "result": "failed",
                "error_text": "REST Post Failed With Status {0} {1}".format( r.status_code, r.content )
                }
        else:
            json_response["data"] = json.loads(r.content)
            json_response["result"] = "success"
            json_response["status_code"] = "{0}".format(r.status_code)

        return json_response

    # del request
    def delete_request(self, url):
        raise
        return #SAFE

        if self.login_data["result"] != "success":
            return {
                "result": "failed",
                "error_text": "Not logged into APIC"
            }

        r = requests.delete(url, cookies={ "APIC-cookie" : self.login_data["APIC-cookie"] }, verify=False, timeout=15)

        json_response = {}
        if r.status_code < 200 or r.status_code > 299:
            json_response = {
                "result": "failed",
                "error_text": "REST Delete Failed With Status {0} {1}".format( r.status_code, r.content )
                }
        else:
            json_response["data"] = json.loads(r.content)
            json_response["result"] = "success"
            json_response["status_code"] = "{0}".format(r.status_code)

        return json_response
#
# End apic_comms class
#
