from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import gd_project as gd


class ProjectToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = json.loads((ROOT/'project-state.json').read_text())
        cls.source = ROOT/cls.state['baseline']['path']

    def test_copy_preserves_gameplay_and_escapes_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'copy.gmd'
            result = gd.clone_level(self.source, out, 'Factory & Steel <copy>')
            self.assertEqual(result['name'], 'Factory & Steel <copy>')
            self.assertEqual(gd.read_level(self.source)[1], gd.read_level(out)[1])
            self.assertEqual(result['parsed_objects'], 57465)
            with self.assertRaises(FileExistsError):
                gd.clone_level(self.source, out, 'overwrite')

    def test_region_includes_following_orb_and_uses_exclusive_end(self):
        result = gd.select_region(self.source, 22065, 22065.01, 5000)
        objs = [x['properties'] for x in result['returned_objects']]
        self.assertTrue(any(o['1']=='84' and '1156' in o.get('57','').split('.') for o in objs))
        self.assertTrue(all(22065 <= float(o['2']) < 22065.01 for o in objs))

    def test_parser_rejects_truncated_object_and_nonfinite_coordinates(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'broken.level'
            for raw in ('kA,1;1,211,2;', 'kA,1;1,211,2,nan,3,0;'):
                path.write_text(raw)
                with self.assertRaises(ValueError): gd.read_level(path)

    def test_index_diff_identifies_metadata_only_copy_as_same_level(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'copy.gmd'
            gd.clone_level(self.source, out, 'Candidate')
            result = gd.compare(self.source, out, 3)
            self.assertTrue(result['equal_raw_level_strings'])
            self.assertEqual(result['changed_common_indices'], 0)


if __name__ == '__main__': unittest.main()
