import os
import sys
from config import Config
from urllib.request import Request, urlopen
from urllib.error import URLError
import json


def check_contracts(host):

    first_line = True
    host_contracts = os.popen(Config.base_cmd + ' ' + host + ' spc host contracts').readlines()

    print(f'There are {len(host_contracts) - 1} contracts')
    print(f'Unresolved and found in the blockchain >>')
    succeded = 0
    failed = 0
    unresolved = 0
    locked = 0
    not_found = 0
    for e in host_contracts:
        if first_line:
            first_line = False
            continue
        e = e.split()
        if e[1] == 'Succeeded':
            succeded += 1
            continue
        if e[1] == 'Failed':
            failed += 1
            continue
        if e[1] == 'Unresolved':
            unresolved += 1
            SCP = 0
            url = 'https://scprime.info/navigator-api/hash/' + e[0]
            req = Request(url)
            try:
                response = urlopen(req)
            except URLError as e:
                if hasattr(e, 'reason'):
                    print('We failed to reach a server.')
                    print('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', e.code)
                sys.exit()

            data = response.read()
            data = data.decode("utf-8")
            data = json.loads(data)
            if len(data) < 3:
                not_found += 1
                continue

            if e[5] == 'SCP':
                SCP = float(e[4])
            if e[5] == 'mS':
                SCP = float(e[4]) / 1000
            if e[5] == 'uS':
                SCP == float(e[4]) / 1000000
            print(f'{e[0]}: {SCP} SCP - Status: {data[1]["Status"]}')
            if data[1]['Status'] == 'ongoing':
                locked += SCP

    print(f'Succeded: {succeded}')
    print(f'Failed: {failed}')
    print(f'Unresolved: {unresolved}')
    print(f'Not found: {not_found}')
    print(f'Ongoing: {unresolved - not_found}')
    print(f'Locked: {locked} SCP')
    wallet = os.popen(Config.base_cmd + ' ' + host + ' spc wallet').readlines()
    exact = wallet[5]
    exact = exact.split()
    exact = exact[1]
    print(f'Exact: {exact} H')
    exact = float(exact) / 1E27
    scprimefunds = wallet[6]
    scprimefunds = scprimefunds.split()
    scprimefunds = float(scprimefunds[1])
    scprimefunds_claims = wallet[7]
    scprimefunds_claims = scprimefunds_claims.split()
    scprimefunds_claims = scprimefunds_claims[2]
    if scprimefunds > 0:
        print(f'Scprimefunds: {scprimefunds} SPF')
        print(f'Scprimefunds claims: {scprimefunds_claims} H')
    return(float(locked), exact, scprimefunds, float(scprimefunds_claims) / 1E27)



def main():
    locked_t = 0
    exact_t = 0
    scprimefunds_t = 0
    scprimefunds_claims_t = 0
    for e in Config.hosts:
        print(f'{e}')
        locked, exact, scprimefunds, scprimefunds_claims =  check_contracts(e)
        print('----------------------------------------')
        locked_t += locked
        exact_t += exact
        scprimefunds_t += scprimefunds
        scprimefunds_claims_t += scprimefunds_claims
    print(f'Wallet: {exact_t} SCP')
    print(f'Locked: {locked_t} SCP')
    print(f'Wallet+locked: {exact_t + locked_t} SCP')
    print(f'Scprimefunds: {scprimefunds_t} SPF')
    print(f'Scprimefunds claims: {scprimefunds_claims_t} SCP')

if __name__ == "__main__":
    main()
