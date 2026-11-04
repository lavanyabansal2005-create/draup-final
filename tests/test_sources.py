"""Every parameter in packs/base.json must have an entry in packs/sources.json.

This is what makes parameter growth self-policing: adding a key to the pack without
deciding where its default comes from fails the suite. Run with the rest:
    python3 -m unittest discover tests
"""
import json, os, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = json.load(open(os.path.join(HERE, '..', 'packs', 'base.json')))
SRC = json.load(open(os.path.join(HERE, '..', 'packs', 'sources.json')))

# Branches whose leaves are scenario/policy choices, not sourced parameters.
EXEMPT_ROOTS = {'meta', 'scenarios', 'policies'}

VALID_STATUS = set(SRC['meta']['status_values'])


def leaf_keys(node, prefix=''):
    """Dotted paths to every leaf in the pack, with '*' for per-item dicts."""
    out = []
    for k, v in node.items():
        path = f'{prefix}.{k}' if prefix else k
        if isinstance(v, dict):
            out.extend(leaf_keys(v, path))
        else:
            out.append(path)
    return out


def covered(path, entries):
    """A path is covered by an exact entry or by a wildcard entry one level up."""
    if path in entries:
        return True
    parts = path.split('.')
    for i in range(len(parts)):
        wild = '.'.join(parts[:i] + ['*'] + parts[i + 1:])
        if wild in entries:
            return True
        # also allow a group entry covering its children, e.g. 'turnover_by_band'
        if '.'.join(parts[:i + 1]) in entries:
            return True
    return False


class SourceCoverage(unittest.TestCase):

    def setUp(self):
        self.entries = {k for k in SRC if not k.startswith('_') and k != 'meta'}
        self.entries |= set(SRC.get('_unsourced_by_design', []))
        self.entries |= set(SRC.get('_policy_not_empirical', []))

    def test_every_pack_key_has_a_source_entry(self):
        missing = [p for p in leaf_keys(PACK)
                   if p.split('.')[0] not in EXEMPT_ROOTS and not covered(p, self.entries)]
        self.assertEqual(missing, [], f'No sources.json entry for: {missing}')

    def test_every_status_is_valid(self):
        for key, e in SRC.items():
            if key.startswith('_') or key == 'meta' or not isinstance(e, dict):
                continue
            self.assertIn(e.get('status'), VALID_STATUS, key)

    def test_sourced_entries_carry_a_citation(self):
        """status 'sourced' means someone can go and check. No citation, no claim."""
        for key, e in SRC.items():
            if key.startswith('_') or key == 'meta' or not isinstance(e, dict):
                continue
            if e.get('status') != 'sourced':
                continue
            has = e.get('source') or e.get('sources') or e.get('citation')
            self.assertTrue(has, f'{key}: status=sourced but no source/sources/citation')

    def test_unsourced_keys_are_declared_not_dressed_up(self):
        """A judgment parameter must not quietly carry a citation as if it were measured."""
        for key in SRC.get('_unsourced_by_design', []):
            e = SRC.get(key)
            if isinstance(e, dict):
                self.assertNotEqual(e.get('status'), 'sourced', key)


if __name__ == '__main__':
    unittest.main()
