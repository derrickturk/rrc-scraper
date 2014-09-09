from sys import argv, stderr
import RRCScraper as r

if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: {0} api-nums ...'.format(argv[0]), file=stderr)

    data = []
    for api in argv[1:]:
        fix_api = ''.join(c for c in api if c.isdigit())
        try:
            data.append((fix_api,
                r.production_from_lease(*r.lease_from_API(fix_api))))
        except Exception as e:
            print('"{0}": {1}'.format(api, e), file=stderr)

    if data:
        hdr = sorted(data[0][1][0].keys())
        if 'Month' in hdr:
            hdr.remove('Month')
            hdr.insert(0, 'Month')
        print('API\t' + '\t'.join(hdr))
        for d in data:
            for rec in d[1]:
                print(d[0] + '\t' + '\t'.join(str(rec[k]) for k in hdr))
