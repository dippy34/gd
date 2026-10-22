"""Check immutable artifacts, current-state docs and the full factory regression."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from gd_project import read_level


def validate_visual_guide():
    """Verify picture provenance and detect stale generated illustrations.

    This checks data/coverage, not whether an annotation makes artistic sense.
    The rendered pictures must also be opened and reviewed by a person/agent.
    """
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path = ROOT/'docs/visual-guide.json'
    manifest = json.loads(manifest_path.read_text())
    rendered = json.loads((ROOT/'docs/images/visual-guide/rendered.json').read_text())
    assert digest(manifest_path) == rendered['manifest_sha256'], 'Regenerate visual guide after manifest edits'
    assert digest(ROOT/rendered['generator']) == rendered['generator_sha256'], 'Regenerate visual guide after renderer edits'

    def png_size(path):
        with path.open('rb') as handle:
            header = handle.read(24)
        assert header[:8] == b'\x89PNG\r\n\x1a\n' and header[12:16] == b'IHDR', path
        return list(struct.unpack('>II', header[16:24]))

    for source in manifest['sources'].values():
        path = ROOT/source['path']
        assert digest(path) == source['sha256'], 'Visual source changed: '+source['path']
        assert png_size(path) == source['size'], source['path']
    ids = [b['id'] for b in manifest['boards']]
    assert len(ids) == len(set(ids)), 'Duplicate visual case IDs'
    assert set(b['category'] for b in manifest['boards']) == set(manifest['categories'])
    assert {b['id'] for b in rendered['boards']} == set(ids)
    guide = (ROOT/'docs/VISUAL_EXAMPLES.md').read_text()
    for board in manifest['boards']:
        assert board['assistant_interpretation'] and board['evidence'], board['id']
        assert not board['whole_scene_approved'], 'Do not imply blanket scene approval'
        if board['category'] == 'Things for later':
            assert board['proposal_status'].startswith('unbuilt')
        for panel in board.get('panels', []):
            width, height = manifest['sources'][panel['source']]['size']
            x, y, w, h = panel.get('crop', [0, 0, width, height])
            assert x >= 0 and y >= 0 and w > 0 and h > 0
            assert x+w <= width and y+h <= height, 'Out-of-bounds crop: '+board['id']
            for marker in panel['marks']:
                mx, my = marker['at']
                assert x <= mx <= x+w and y <= my <= y+h, 'Marker outside crop: '+board['id']
                if 'box' in marker:
                    bx, by, bw, bh = marker['box']
                    assert bw > 0 and bh > 0 and x <= bx and y <= by
                    assert bx+bw <= x+w and by+bh <= y+h, 'Box outside crop: '+board['id']
        for data_source in board.get('data_sources', []):
            assert (ROOT/data_source).is_file(), data_source
    for picture in rendered['boards']:
        path = ROOT/picture['path']
        assert digest(path) == picture['sha256'], picture['path']
        assert png_size(path) == rendered['size'], picture['path']
        assert 'images/visual-guide/'+picture['id']+'.png' in guide, 'Unlinked visual case: '+picture['id']
    return {'sources': len(manifest['sources']), 'pictures': len(ids),
            'categories': len(manifest['categories']), 'provenance_and_generation_hashes': 'passed'}


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
    docs = list((ROOT/'docs').rglob('*.md')) + list((ROOT/'examples').glob('*.md'))
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
    visual_guide = validate_visual_guide()
    report = {'passed': True, 'level_artifacts_hashed_and_parsed': len(catalog['levels']),
              'curated_links_checked': links, 'active_baseline': str(baseline.relative_to(ROOT)),
              'factory_regression': 'passed', 'native_playtest': False,
              'rendering_or_performance_certified': False, 'visual_guide': visual_guide}
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'build/repo-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
