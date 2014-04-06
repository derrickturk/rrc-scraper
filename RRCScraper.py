import urllib.request
import urllib.parse
import re

WELLBORE_SEARCH_URL = 'http://webapps2.rrc.state.tx.us/EWA/wellboreQueryAction.do'
LEASE_DETAIL_URL = 'http://webapps2.rrc.state.tx.us/EWA/leaseDetailAction.do'

def lease_from_API(api):
    if (len(api) not in (10, 12, 14)):
        raise RuntimeError('Invalid API number.')

    query_result = rrc_lease_query(api)
    return (extract_lease_no(query_result), extract_district(query_result),
            extract_well_type(query_result))

def rrc_lease_query(api):
    (pre, suf) = (api[2:5], api[5:11])

    request_params = {
        'searchArgs.apiNoPrefixArg' : pre,
        'searchArgs.apiNoSuffixArg' : suf,
        'methodToCall' : 'search'
    }

    request = urllib.request.Request(
            WELLBORE_SEARCH_URL, 
            urllib.parse.urlencode(request_params).encode('utf-8'),
            { 'Content-Type' :
                'application/x-www-form-urlencoded;charset=utf-8' },
            method='POST')

    with urllib.request.urlopen(request) as response:
        if response.status != 200:
            raise RuntimeError('HTTP request failed.')
        data = response.read()
        return data.decode()

def extract_lease_no(lease_query_result):
    if 'rgx' not in extract_lease_no.__dict__:
        extract_lease_no.rgx = re.compile(r'leaseno=(\d+)', re.IGNORECASE)
    match = extract_lease_no.rgx.search(lease_query_result)
    if not match:
        raise RuntimeError('Unable to find lease number!')
    return match.group(1)

def extract_district(lease_query_result):
    if 'rgx' not in extract_district.__dict__:
        extract_district.rgx = re.compile(r'district=(\d+)', re.IGNORECASE)
    match = extract_district.rgx.search(lease_query_result)
    if not match:
        raise RuntimeError('Unable to find district!')
    return match.group(1)

def extract_well_type(lease_query_result):
    return 'Oil'
