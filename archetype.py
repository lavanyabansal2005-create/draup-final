import json, copy, evm
def build(data, pack, arch):
    d2 = copy.deepcopy(data); p2 = copy.deepcopy(pack)
    for r in d2['roles']:
        r['headcount'] = max(1, round(r['headcount'] * arch['headcount_factor']))
        r['salary'] = r['salary'] * arch['salary_factor']
    p2['economics'].update(arch['economics'])
    p2['meta']['name'] = arch['label']
    return d2, p2
