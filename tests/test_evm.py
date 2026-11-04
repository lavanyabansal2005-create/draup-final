"""Acceptance and invariant tests for the Etter Value Model. Run: python3 -m unittest discover tests"""
import json, math, copy, os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import evm, archetype

DATA = json.load(open(os.path.join(HERE, '..', 'data', 'etter_fpa.json')))
PACK = json.load(open(os.path.join(HERE, '..', 'packs', 'base.json')))
ARCH = json.load(open(os.path.join(HERE, '..', 'packs', 'archetypes.json')))
PREP = evm.prepare(DATA, PACK)
GRID = [(s, p) for s in PACK['scenarios'] for p in PACK['policies']]
REF = json.load(open(os.path.join(HERE, 'reference.json')))


class Acceptance(unittest.TestCase):
    """The five acceptance criteria in Chandan's brief."""

    def test_every_currency_line_resolves_to_an_input_row(self):
        for s, p in GRID:
            r = evm.simulate(PREP, evm.scenario(PACK, s), evm.policy(PACK, p))
            self.assertLess(r['check_ledger_gap'], 1e-4, (s, p))
            for e in r['ledger']:
                kind = e['source'].split(':')[0]
                self.assertIn(kind, ('role', 'workload', 'pack'), e)
                if kind == 'role':
                    self.assertIn(e['source'][6:], PREP['roles'])
                if kind == 'workload':
                    self.assertIn(e['source'][10:], PREP['workloads'])

    def test_freed_hours_reconcile_within_one_percent(self):
        for s, p in GRID:
            r = evm.simulate(PREP, evm.scenario(PACK, s), evm.policy(PACK, p))
            self.assertLess(r['check_reconciliation_max_gap'], 0.01, (s, p))
            self.assertLess(r['check_reconciliation_max_gap'], 1e-9, (s, p))   # in fact exact
            self.assertGreaterEqual(r['check_min_capacity_h'], -1e-9)

    def test_zero_headcount_conversion_is_still_meaningful(self):
        r = evm.simulate(PREP, evm.scenario(PACK, 'Moderate'), evm.policy(PACK, 'Capacity only'))
        self.assertEqual(r['positions_end'], 0)
        self.assertGreater(r['pv_capacity'], 0)
        self.assertGreater(r['capacity_hurdle'], 0)
        self.assertLess(r['capacity_hurdle'], 1)

    def test_three_most_sensitive_parameters_are_named(self):
        S = evm.scenario(PACK, 'Moderate'); Q = evm.policy(PACK, 'Attrition only')
        base, rows = evm.sensitivity(PREP, S, Q)
        top3 = [r['param'] for r in rows[:3]]
        self.assertEqual(set(top3), {'harvest_automation', 'takeover', 'review'})

    def test_an_archetype_says_do_not_start(self):
        a = ARCH['insurance_mid']
        d2, p2 = archetype.build(DATA, PACK, a)
        pr = evm.prepare(d2, p2)
        S = evm.scenario(p2, 'Moderate'); Q = evm.policy(p2, a['default_policy'])
        mc = evm.montecarlo(pr, S, Q, n=200)
        p_pos = sum(1 for x in mc if x['headline'] > 0) / len(mc)
        self.assertEqual(evm.decide(p_pos, Q)[0], 'stop')


class Invariants(unittest.TestCase):

    def test_deterministic(self):
        S = evm.scenario(PACK, 'Moderate'); Q = evm.policy(PACK, 'Attrition only')
        a = evm.simulate(PREP, S, Q); b = evm.simulate(evm.prepare(DATA, PACK), S, Q)
        self.assertEqual(a['npv_cash'], b['npv_cash'])
        m1 = evm.montecarlo(PREP, S, Q, n=50); m2 = evm.montecarlo(PREP, S, Q, n=50)
        self.assertEqual([x['npv'] for x in m1], [x['npv'] for x in m2])

    def test_rng_reference_vector(self):
        # the browser engine must reproduce these exactly
        g = evm.RNG(20261019)
        u = [g.u() for _ in range(3)]
        self.assertEqual(u, [round(x, 17) for x in u])
        g = evm.RNG(1)
        self.assertAlmostEqual(g.u(), 0.6270739405881613, places=15)

    def test_positions_never_exceed_freed_and_never_come_back(self):
        for s, p in GRID:
            r = evm.simulate(PREP, evm.scenario(PACK, s), evm.policy(PACK, p))
            pos = r['series']['positions']
            self.assertTrue(all(b >= a for a, b in zip(pos, pos[1:])), (s, p))
            for row in r['roles']:
                self.assertLessEqual(row['positions_end'], math.floor(row['freed_fte'] + 1e-9) + 0, row['role'])

    def test_more_takeover_never_lowers_cash(self):
        Q = evm.policy(PACK, 'Active reduction'); S = evm.scenario(PACK, 'Moderate')
        ch, _ = evm.scope(PREP, S)
        vals = [evm.simulate(PREP, dict(S, takeover=t), Q, dict(chosen=ch))['npv_cash'] for t in (0.2, 0.3, 0.4, 0.5, 0.6)]
        self.assertEqual(vals, sorted(vals))

    def test_more_harvest_more_positions(self):
        S = evm.scenario(PACK, 'Moderate')
        pos = [evm.simulate(PREP, S, dict(evm.policy(PACK, 'Attrition only'), harvest_automation=h))['positions_end']
               for h in (0.0, 0.25, 0.5, 0.75, 1.0)]
        self.assertEqual(pos, sorted(pos))

    def test_cash_and_capacity_are_separate(self):
        S = evm.scenario(PACK, 'Moderate')
        a = evm.simulate(PREP, S, evm.policy(PACK, 'Capacity only'))
        b = evm.simulate(PREP, S, evm.policy(PACK, 'Active reduction'))
        self.assertGreater(a['pv_capacity'], b['pv_capacity'])   # hours banked as cash leave capacity
        self.assertEqual(a['pv_savings'], 0.0)

    def test_missing_data_is_flagged_not_fatal(self):
        d = copy.deepcopy(DATA)
        d['roles'][0]['salary'] = None
        d['tasks'].append(dict(role='Nobody', workload='x', task='x', category='Directive', hours_month=5))
        d['tasks'].append(dict(role=d['roles'][1]['role'], workload='x', task='x', category='Mystery', hours_month=1))
        pr = evm.prepare(d, PACK)
        kinds = ' '.join(f[1] for f in pr['flags'])
        self.assertIn('salary missing', kinds)
        self.assertIn('unknown role', kinds)
        self.assertIn('unknown category', kinds)
        r = evm.simulate(pr, evm.scenario(PACK, 'Moderate'), evm.policy(PACK, 'Attrition only'))
        self.assertTrue(math.isfinite(r['npv_cash']))

    def test_no_build_means_no_build_cost(self):
        r = evm.simulate(PREP, evm.scenario(PACK, 'Moderate'), evm.policy(PACK, 'Attrition only'), dict(auto_on=False))
        self.assertEqual(sum(r['series']['build']), 0.0)
        self.assertEqual(sum(r['series']['run']), 0.0)

    def test_reference_numbers(self):
        # final model at the defaults: Moderate, Attrition only, cross-industry, ceilings 90% / 80%
        S = evm.scenario(PACK, 'Moderate'); Q = evm.policy(PACK, 'Attrition only')
        passing, _ = evm.scope(PREP, S)
        chosen, _ = evm.size_to_peak(PREP, S, Q, passing)
        r = evm.simulate(PREP, S, Q, dict(chosen=chosen))
        self.assertEqual(len(passing), 59)
        self.assertEqual(len(chosen), REF['n_built'])
        self.assertEqual(sum(1 for x in chosen if x['option'] == 'buy'), REF['n_buy'])
        self.assertAlmostEqual(r['npv_cash'], REF['npv'], delta=0.5)
        self.assertEqual(r['positions_end'], REF['positions'])
        self.assertEqual(r['payback_month'], REF['payback'])

    def test_earlier_engine_is_reproduced(self):
        # build-only, every cost-effective workload, ceilings 85% / 55%: the v0 engine to the cent
        p = copy.deepcopy(PACK); p['costs']['allow_buy'] = False
        p['categories']['Directive']['ceiling'] = 0.85; p['categories']['Feedback Loop']['ceiling'] = 0.55
        r = evm.simulate(evm.prepare(DATA, p), evm.scenario(p, 'Moderate'), evm.policy(p, 'Attrition only'))
        self.assertAlmostEqual(r['npv_cash'], 3096839.06, delta=0.5)
        self.assertEqual(r['positions_end'], 47)
        self.assertEqual(r['payback_month'], 44)

    def test_build_or_buy_keeps_the_cheaper_option(self):
        S = evm.scenario(PACK, 'Moderate')
        _, ranked = evm.scope(PREP, S)
        p = copy.deepcopy(PACK); p['costs']['allow_buy'] = False
        _, build_only = evm.scope(evm.prepare(DATA, p), S)
        b = {x['name']: x['npv_at_cost'] for x in build_only}
        for x in ranked:
            self.assertGreaterEqual(x['npv_at_cost'], b[x['name']] - 1e-6, x['name'])
            self.assertEqual(x['option'] == 'buy', x['npv_at_cost'] > b[x['name']], x['name'])

    def test_peak_cash_size_beats_every_other_size(self):
        S = evm.scenario(PACK, 'Moderate'); Q = evm.policy(PACK, 'Attrition only')
        passing, _ = evm.scope(PREP, S)
        chosen, sweep = evm.size_to_peak(PREP, S, Q, passing)
        self.assertEqual(max(sweep), sweep[len(chosen) - 1])
        all_in = evm.simulate(PREP, S, Q, dict(chosen=passing))['headline']
        sized = evm.simulate(PREP, S, Q, dict(chosen=chosen))['headline']
        self.assertGreaterEqual(sized, all_in)

    def test_capacity_only_keeps_every_passing_workload(self):
        S = evm.scenario(PACK, 'Moderate'); Q = evm.policy(PACK, 'Capacity only')
        passing, _ = evm.scope(PREP, S)
        chosen, sweep = evm.size_to_peak(PREP, S, Q, passing)
        self.assertEqual(len(chosen), len(passing)); self.assertIsNone(sweep)


if __name__ == '__main__':
    unittest.main()
