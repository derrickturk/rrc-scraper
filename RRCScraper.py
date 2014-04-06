import urllib.request
import urllib.parse
import datetime
import re

URL_BASE = 'http://webapps2.rrc.state.tx.us/EWA/'
WELLBORE_SEARCH_URL = URL_BASE + 'wellboreQueryAction.do'
LEASE_PRODUCTION_URL = URL_BASE + 'specificLeaseQueryAction.do'

def production_from_lease(lease, district, well_type):
    query_result = rrc_production_query(lease, district, well_type)

    return query_result

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
    if 'detail_link_rgx' not in extract_well_type.__dict__:
        extract_well_type.detail_link_rgx = re.compile(
                r'href="(leaseDetailAction.do[^"]+)"', re.IGNORECASE)

    match = extract_well_type.detail_link_rgx.search(lease_query_result)
    if not match:
        raise RuntimeError('No detail link found!')
    detail_url = URL_BASE + match.group(1)

    request = urllib.request.urlopen(detail_url)
    if (request.status != 200):
        raise RuntimeError('HTTP request failed.')

    lease_detail = request.read().decode()
    if 'well_type_rgx' not in extract_well_type.__dict__:
        extract_well_type.well_type_rgx = re.compile(
                r'Well Type:\s+<[^>]+>\s+(\w+)', re.IGNORECASE)

    match = extract_well_type.well_type_rgx.search(lease_detail)
    if not match:
        raise RuntimeError('Unable to find well type!')
    return match.group(1)

def rrc_production_query(lease, district, well_type):
    request_params = {
        'actionManager.actionRcrd[0].actionDisplayNmHndlr.inputValue':'Search Criteria',
        'actionManager.actionRcrd[0].actionHndlr.inputValue':'/specificLeaseQueryAction.do',
        'actionManager.actionRcrd[0].actionMethodHndlr.inputValue':'unspecified',
        'actionManager.actionRcrd[0].actionParameterHndlr.inputValue':'methodToCall',
        'actionManager.actionRcrd[0].actionParametersHndlr.inputValue':'',
        'actionManager.actionRcrd[0].contextPathHndlr.inputValue':'/EWA',
        'actionManager.actionRcrd[0].hostHndlr.inputValue':'webapps2.rrc.state.tx.us:80',
        'actionManager.actionRcrd[0].pagerParameterKeyHndlr.inputValue':'',
        'actionManager.actionRcrd[0].returnIndexHndlr.inputValue':'0',
        'actionManager.currentIndexHndlr.inputValue':'0',
        'actionManager.recordCountHndlr.inputValue':'1',
        'methodToCall':'search',
        'searchArgs.activeTabsFlagwordHndlr.inputValue':'0',
        'searchArgs.leaseNumberArg' : lease,
        'searchArgs.districtCodeArg' : district,
        'searchArgs.oilOrGasArg' : 'O' if well_type == 'Oil' else 'G',
        'searchArgs.startMonthArg':'01',
        'searchArgs.startYearArg':'1993',
        'searchArgs.endMonthArg':'12',
        'searchArgs.endYearArg' : datetime.date.today().year,
        'searchArgs.orderByHndlr.inputValue':'',
        'searchArgs.searchType':'specificLease',
        'searchType':'specificLease',
        'submit':'Submit',
        'viewType':'init'
    }

    request = urllib.request.Request(
            LEASE_PRODUCTION_URL, 
            urllib.parse.urlencode(request_params).encode('utf-8'),
            { 'Content-Type' :
                'application/x-www-form-urlencoded;charset=utf-8' },
            method='POST')

    with urllib.request.urlopen(request) as response:
        if response.status != 200:
            raise RuntimeError('HTTP request failed.')
        data = response.read()
        return data.decode()
