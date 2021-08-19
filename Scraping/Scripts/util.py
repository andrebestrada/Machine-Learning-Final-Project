"""
Auxiliary functions to handle url requests. Obtained from utility
functions of PA4.
"""
# pylint: disable-msg=invalid-name, broad-except, unused-variable
# pylint: disable-msg=len-as-condition, no-else-return, undefined-variable
# pylint: disable-msg=too-many-return-statements, superfluous-parens
# pylint: disable=R1714
import requests

def get_request(url):
    '''
    Open a connection to the specified URL and if successful
    read the data.

    Inputs:
        url: must be an absolute URL

    Outputs:
        request object or None

    Examples:
        get_request("http://www.cs.uchicago.edu")
    '''


    try:
        r = requests.get(url)
        if r.status_code == 404 or r.status_code == 403:
            r = None
            print("Error 404 or 403 whith url {}".format(url))

    except Exception:
        print("Connection failed with url {}".format(url))
        # fail on any kind of error
        r = None

    return r


def read_request(request):
    '''
    Return data from request object.  Returns result or "" if the read
    fails..
    '''

    try:
        return request.text
    except Exception:
        print("read failed: " + request.url)
        return ""


def get_request_url(request):
    '''
    Extract true URL from the request
    '''
    return request.url
