"""Check immutable artifacts, current-state docs and the full factory regression."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from gd_project import read_level


def main():
    state = json.loads((ROOT/'project-state.json').read_text())
    catalog = json.loads((ROOT/'catalog/artifacts.json').read_text())
    for record in catalog['levels']:
        path = ROOT/record['path']
        assert path.is_file(), record['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], 'Artifact changed: '+record['path']
        fields, raw, _, objects = read_level(path)
        assert len(objects) == record['parsed_objects'], record['path']
    baseline = ROOT/state['baseline']['path']
    assert hashlib.sha256(baseline.read_bytes()).hexdigest() == state['baseline']['sha256']
    assert read_level(baseline)[1] == (ROOT/state['baseline']['raw_level']).read_text()
    assert not list((ROOT/'outputs').glob('*CUSTOM-FIRE*')), 'Disregarded experiment must not be selected or bundled'
    assert not (ROOT/'work/sinking-factory/custom-fire-art').exists()
    # Check local links in the curated entrypoints. Historical notes intentionally
    # keep their old relative references and are not treated as current manuals.
    docs = list((ROOT/'docs').glob('*.md')) + list((ROOT/'examples').glob('*.md'))
    docs += [ROOT/'README.md', ROOT/'AGENTS.md', ROOT/'CLAUDE.md']
    links = 0
    for doc in docs:
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', doc.read_text()):
            if target.startswith(('http:', 'https:', '#', 'mailto:')): continue
            target = unquote(target.split('#')[0].strip('<>'))
            if not target: continue
            assert (doc.parent/target).exists(), 'Broken link in %s: %s' % (doc.name, target)
            links += 1
    # Full project-specific checker verifies source collision properties, exact
    # portal rollback, custom orb retention, scope, ash, layers and group24 fix.
    subprocess.run([sys.executable, str(ROOT/'work/sinking-factory/validate_custom_orbs.py')], cwd=ROOT, check=True)
    report = {'passed': True, 'level_artifacts_hashed_and_parsed': len(catalog['levels']),
              'curated_links_checked': links, 'active_baseline': str(baseline.relative_to(ROOT)),
              'factory_regression': 'passed', 'native_playtest': False,
              'rendering_or_performance_certified': False}
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'build/repo-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
