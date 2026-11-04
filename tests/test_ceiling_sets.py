"""Headline cash NPV under each of the four readings of the Etter category ceilings.

The source workbook states the ceilings more than once and the statements disagree
(see docs/Etter_Value_Model_assumptions.md, "Category ceilings"). The pack uses none of
them exactly. This test prices every reading so the spread is locked in and visible:
if anything moves the price of a reading, it fails here first.

    Tasks column    0.85 / 0.55   $5,800,227.08
    Pack (in use)   0.90 / 0.80   $9,376,169.02   <- tests/reference.json headline
    Read me table   0.90 / 0.85   $9,754,376.86
    Bucket ceiling  1.00 / 1.00  $11,476,088.73

Expected values were reproduced independently in docs/Etter_Value_Model_FPA.xlsx with
programme size re-optimised to peak cash for each reading, and match this engine
to within $0.01. The tolerance below is $0.50, the same as test_reference_numbers.

Do not edit an expected value to make this pass. A change here is a change to the
open ceilings question and needs the same treatment as a headline change.
"""
import copy, json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import evm  # noqa: E402

DATA = json.load(open(os.path.join(HERE, '..', 'data', 'etter_fpa.json')))
BASE = json.load(open(os.path.join(HERE, '..', 'packs', 'base.json')))

# Negligibility is not here: it maps to human in evm.CAT_TYPE, so it has no ceiling in the pack
# (removed 5 Nov 2026). Both Etter tables give it 0.10; that value was never read.
CATS = ('Directive', 'Feedback Loop', 'Task Iteration', 'Learning', 'Validation')

# name: (ceilings in CATS order, expected 5-year cash NPV)
CEILING_SETS = {
    'tasks_column':   ((0.85, 0.55, 0.45, 0.25, 0.50),  5_800_227.08),
    'pack':           ((0.90, 0.80, 0.45, 0.25, 0.50),  9_376_169.02),
    'read_me_table':  ((0.90, 0.85, 0.50, 0.45, 0.40),  9_754_376.86),
    'bucket_ceiling': ((1.00, 1.00, 0.50, 0.50, 0.50), 11_476_088.73),
}

TOLERANCE = 0.50  # dollars, as in test_evm.test_reference_numbers


def headline_npv(pack):
    """5-year cash NPV at the defaults (FP&A, Moderate, attrition only), with the
    programme re-sized to peak cash, exactly as test_evm.test_reference_numbers does."""
    prep = evm.prepare(DATA, pack)
    S = evm.scenario(pack, 'Moderate'); Q = evm.policy(pack, 'Attrition only')
    passing, _ = evm.scope(prep, S)
    chosen, _ = evm.size_to_peak(prep, S, Q, passing)
    return evm.simulate(prep, S, Q, dict(chosen=chosen))['npv_cash']


def with_ceilings(values):
    pack = copy.deepcopy(BASE)
    for cat, v in zip(CATS, values):
        pack['categories'][cat]['ceiling'] = v
    return pack


class CeilingSets(unittest.TestCase):

    def test_pack_set_matches_the_pack(self):
        """Guards the table: the 'pack' row must be what base.json actually holds."""
        held = tuple(BASE['categories'][c]['ceiling'] for c in CATS)
        self.assertEqual(held, CEILING_SETS['pack'][0])
        self.assertEqual(set(BASE['categories']), set(CATS))
        self.assertEqual(evm.CAT_TYPE['Negligibility'], 'human')


def _make(name, values, expected):
    def test(self):
        got = headline_npv(with_ceilings(values))
        self.assertAlmostEqual(
            got, expected, delta=TOLERANCE,
            msg=f'{name}: headline ${got:,.2f}, locked at ${expected:,.2f}')
    test.__doc__ = f'Headline cash NPV under the {name} ceilings.'
    return test


for _name, (_values, _expected) in CEILING_SETS.items():
    setattr(CeilingSets, f'test_headline_{_name}', _make(_name, _values, _expected))


if __name__ == '__main__':
    unittest.main()
