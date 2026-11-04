"""Browser engine parity: evm.js must give the same numbers as evm.py on the same inputs."""
import json, os, sys, subprocess, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import evm, archetype
data = json.load(open(os.path.join(ROOT, 'data', 'etter_fpa.json')))
pack = json.load(open(os.path.join(ROOT, 'packs', 'base.json')))
arch = json.load(open(os.path.join(ROOT, 'packs', 'archetypes.json')))
cases = [dict(id='mod_att', s='Moderate', p='Attrition only', n=120),
         dict(id='con_cap', s='Conservative', p='Capacity only', n=60),
         dict(id='agg_act', s='Aggressive', p='Active reduction', n=60),
         dict(id='tech', arch='tech_large', s='Moderate', p='Attrition only', n=60),
         dict(id='hosp', arch='health_large', s='Moderate', p='Capacity only', n=60),
         dict(id='midins', arch='insurance_mid', s='Moderate', p='Attrition only', n=60)]
js = json.loads(subprocess.check_output(['node', os.path.join(HERE, 'parity_run.js'), json.dumps(cases)]))
py = {}
g = evm.RNG(20261019); py['rng'] = [g.u(), g.u(), g.u(), g.z()]
for c in cases:
    d, p = (archetype.build(data, pack, arch[c['arch']]) if c.get('arch') else (data, pack))
    py[c['id']] = evm.report(d, p, c['s'], c['p'], c['n'], 20261019)
worst = [0.0, '']
def cmp(a, b, path):
    if isinstance(a, dict):
        for k in a:
            if k in ('ledger',): continue
            if k not in b: raise AssertionError(f'missing in js: {path}.{k}')
            cmp(a[k], b[k], f'{path}.{k}')
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b), f'length {path}: {len(a)} vs {len(b)}'
        for i, (x, y) in enumerate(zip(a, b)): cmp(x, y, f'{path}[{i}]')
    elif isinstance(a, bool) or a is None or isinstance(a, str):
        assert a == b, f'{path}: {a!r} vs {b!r}'
    else:
        if b is None: raise AssertionError(f'{path}: {a} vs None')
        if '.checks.' in path:
            assert abs(a) < 1e-4 and abs(b) < 1e-4 or abs(a - b) < 1e-6, f'{path}: {a!r} vs {b!r}'; return
        rel = abs(a - b) / max(1.0, abs(a))
        if rel > worst[0]: worst[0], worst[1] = rel, path
        assert rel < 1e-9, f'{path}: {a!r} vs {b!r}'
for k in py:
    cmp(py[k], js[k], k)
    if k != 'rng':
        lp = sorted((e['line'], e['source'], e['pv']) for e in py[k]['ledger'])
        lj = sorted((e['line'], e['source'], e['pv']) for e in js[k]['ledger'])
        assert len(lp) == len(lj), k
        for x, y in zip(lp, lj):
            assert x[:2] == y[:2] and abs(x[2] - y[2]) <= 1e-9 * max(1, abs(x[2])), (x, y)
print(f'parity OK on {len(cases)} cases; worst relative difference {worst[0]:.2e} at {worst[1]}')
