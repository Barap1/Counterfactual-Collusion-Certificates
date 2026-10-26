"""Independent provenance checks for the compact explorer review context."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'demo/explorer' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class ExplorerContextTests(unittest.TestCase):
    def test_frozen_review_results_are_represented_exactly(self):
        generated = (ROOT / 'demo/explorer/research-context.js').read_text().split('window.CCC_DATA.review = ', 1)[1].strip().removesuffix(';')
        context = json.loads(generated)
        self.assertEqual(context, module('build_research_context').build())
        self.assertEqual(context['utility']['v1'], {'passed': 2, 'total': 84, 'undefined_gaps': 73})
        self.assertEqual(context['utility']['v0'], {'passed': 5, 'total': 84, 'undefined_gaps': 73})
        self.assertEqual([k for k, v in context['criteria'].items() if v == 'fail'], ['RQ3', 'RQ4', 'RQ4b', 'RQ5'])
        self.assertEqual(context['rq3']['k'], 61)
        self.assertEqual(context['rq3']['n'], 200)
        self.assertEqual([r['over_attribution']['unit_k'] for r in context['baseline']], [200, 200])

    def test_pages_stages_only_the_public_demo_and_preserves_source_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            module('prepare_pages').stage(directory)
            target = Path(directory)
            self.assertFalse((target / '.git').exists())
            self.assertFalse((target / 'ops').exists())
            for path in (ROOT / 'demo/data').rglob('*'):
                if path.is_file() and path.name != '.DS_Store':
                    self.assertEqual(path.read_bytes(), (target / path.relative_to(ROOT)).read_bytes())
            for name in ['index.html', 'app.js', 'style.css', 'theme.js', 'research-context.js', 'data/index.js', 'data/twins.js', 'fonts/fonts.css', 'fonts/OFL.txt']:
                self.assertTrue((target / 'demo/explorer' / name).is_file(), name)
            self.assertFalse((target / 'demo/explorer/qa').exists())


if __name__ == '__main__':
    unittest.main()
