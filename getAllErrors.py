#!/usr/local/bin/python3

# MIT License
# Copyright (c) 2021 HLSAnalyzer.com
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import urllib.request
import json
from urllib.request import Request, HTTPSHandler, build_opener, install_opener
import ssl
import os



def _load_from_uri(uri, timeout=3, headers={}, return_content=False):
    request = Request(uri, headers=headers)
    https_sslv3_handler = HTTPSHandler(context=ssl.SSLContext())
    opener = build_opener(https_sslv3_handler)
    install_opener(opener)
    resource = opener.open(request, timeout=timeout)

    content = _read_python3x(resource)
    return content


def _read_python3x(resource):
    final = None
    while True:
        cur = resource.read(1000)
        if (len(cur) == 0): break
        if final is None:
            final = ""
        final += cur.decode(resource.headers.get_content_charset(failobj="utf-8"))

    return final



def get_all_status(server, key):
    try:
        url = "%s/api/status?apikey=%s" % (server, key)
        response = _load_from_uri(url, timeout=3)
        result_json = json.loads(response)
        return result_json
    except urllib.error.HTTPError as e:
        print("Error in adding link")
        print(e.code)
        print(e.read().decode())
        return None
    except:
        print("Exception in adding link")
        return None


def get_errors_warnings(server, apikey, linkid, start, end, mode):
    if (mode != "errors") and (mode != "warnings"):
        raise("Usage error")

    try:
        url = "%s/api/%s?apikey=%s&start=%d&end=%d&linkid=%s" % (server, mode, apikey, start, end, linkid)
        response = _load_from_uri(url, timeout=3)
        data = json.loads(response)
        print(json.dumps(data, indent=4, sort_keys=True))
        return data

    except urllib.error.HTTPError as e:
        print("Error in checking status")
        print(e.code)
        print(e.read())
        return None
    except:
        print("Exception in adding link")
        return None

def processLinkStatus(link_status):
    error_count = link_status['Errors']
    warning_count = link_status['Warnings']
    timestamp = link_status['Timestamp']
    linkid = link_status['LinkID']

    return (error_count, warning_count, timestamp, linkid)


def getAllErrors():

    #Replace with endpoing and API Key
    server = "https://staging.hlsanalyzer.com"
    key = os.environ.get('APIKEY')

    #Get the status for all the links
    result = get_all_status(server, key)

    if result is not None:
        #Traverse all HLS links being monitored.
        # Each link can be either a master playlist with variants, or a single Media playlist
        for hls_link in result['status'].keys():
            link_status = result['status'][hls_link]
            has_variants = False
            if 'Variants' in link_status:
                print("MASTER [%s]" %(hls_link))
                has_variants = True
            else:
                print("MEDIA [%s]" %(hls_link))

            (error_count, warning_count, timestamp, linkid) = processLinkStatus(link_status)
            if int(float(error_count)) > 0:
                get_errors_warnings(server, key, linkid, 0, timestamp, mode="errors")
            if int(float(warning_count)) > 0:
                get_errors_warnings(server, key, linkid, 0, timestamp, mode="warnings")

            if has_variants:
                variant_status = result['status'][hls_link]['Variants']
                for variant in variant_status.keys():
                    print("|-- Variant [%s] "%(variant))
                    (error_count, warning_count, timestamp, linkid) = processLinkStatus(variant_status[variant])
                    if float(error_count)> 0:
                        get_errors_warnings(server, key, linkid, 0, timestamp, "errors")
                    if float(warning_count) > 0:
                        get_errors_warnings(server, key, linkid, 0, timestamp, "warnings")


if __name__ == '__main__':
    getAllErrors()
