import json, os
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(H, '..')
t = open(os.path.join(H, 'template.html')).read()
engine = open(os.path.join(P, 'evm.js')).read()
data = open(os.path.join(H, 'data.min.json')).read()
pack = json.dumps(json.load(open(os.path.join(P, 'packs', 'base.json'))), separators=(',', ':'))
arch = json.dumps(json.load(open(os.path.join(P, 'packs', 'archetypes.json'))), separators=(',', ':'))
app = open(os.path.join(H, 'app.js')).read()
for s in (engine, app): assert '</script' not in s
t = t.replace('/*ENGINE*/', engine).replace('/*DATA*/', f'window.ETTER_DATA={data};window.BASE_PACK={pack};window.ARCHETYPES={arch};').replace('/*APP*/', app)
open(os.path.join(H, 'etter_value_model.html'), 'w').write(t)
print(len(t))
