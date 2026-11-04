// Runs the JS engine on the same inputs as tests/parity.py and prints JSON.
const fs = require('fs'), path = require('path');
const EVM = require(path.join(__dirname, '..', 'evm.js'));
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'etter_fpa.json')));
const pack = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'packs', 'base.json')));
const arch = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'packs', 'archetypes.json')));
const cases = JSON.parse(process.argv[2]);
const build = a => { const d = EVM.clone(data), p = EVM.clone(pack);
  for (const r of d.roles) { r.headcount = Math.max(1, Math.round(r.headcount * a.headcount_factor)); r.salary = r.salary * a.salary_factor; }
  Object.assign(p.economics, a.economics); p.meta.name = a.label; return [d, p]; };
const out = {};
const rng = new EVM.RNG(20261019); out.rng = [rng.u(), rng.u(), rng.u(), rng.z()];
for (const c of cases) {
  let d = data, p = pack;
  if (c.arch) [d, p] = build(arch[c.arch]);
  out[c.id] = EVM.report(d, p, c.s, c.p, c.n, 20261019);
}
process.stdout.write(JSON.stringify(out));
