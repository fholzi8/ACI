'''

'''
import json
import traceback

#
# Error occurred that stopped processing
#
def error_json(error_text, json_resp={}):
    json_response = {
            "result": "error",
            "error_text": error_text,
            "additonal" : json_resp,   # should be "extra" not additional
            "trace" : traceback.format_stack()
            }
    return json_response

#
# Insufficient data returned or obtained which prevents
# successful return. - Not a system failure, more
# a lack of data or invalid query
#
def failed_json(failure_text, extra=None):
    json_response = {
            "result": "failed",
            "error_text": failure_text,
            "extra": extra
            }
    return json_response

#
# successful processing and valid data returned
#
def success_json(status, data=None, extra={}):
    json_response = {
            "result": "success",
            "status": status,
            "data" : data,
            "extra" : extra
            }
    return json_response

def is_success(json_response):
    try:
        if json_response["result"] == "success":
            return True
    except:
            return False
    return False

def is_failed(json_response):
    try:
        if json_response["result"] == "failed":
            return True
    except:
            return False
    return False

def is_error(json_response):
    try:
        if json_response["result"] == "error":
            return True
    except:
            return False
    return False


def get_returned_data(json_response):
    # TODO
    None

def print_json(jsondata):
    print(json.dumps(jsondata, indent=2))
