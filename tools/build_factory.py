"""Rebuild Factory Orbs in an isolated temporary tree; never overwrite exports."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'build/factory-rebuild')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Choose a new output directory; existing results are never overwritten')
    for module in ('numpy', 'PIL', 'shapely'):
        try: __import__(module)
        except ImportError: parser.error('Install optional requirements.txt in your Python environment')
    resources = Path(os.environ.get('GD_RESOURCES', str(Path.home()/'Library/Application Support/Steam/steamapps/common/Geometry Dash/Geometry Dash.app/Contents/Resources'))).expanduser()
    if not (resources/'GJ_GameSheet-hd.plist').is_file():
        parser.error('Set GD_RESOURCES to your own Geometry Dash Resources directory')
    with tempfile.TemporaryDirectory(prefix='gd-factory-build-') as td:
        temp = Path(td)
        (temp/'outputs').mkdir(); (temp/'inputs').mkdir()
        shutil.copy2(ROOT/'inputs/The Sinking Factory.gmd', temp/'inputs/The Sinking Factory.gmd')
        shutil.copytree(ROOT/'work/handoff/tools', temp/'work/handoff/tools', ignore=shutil.ignore_patterns('__pycache__'))
        (temp/'work/handoff/research').mkdir()
        shutil.copy2(ROOT/'work/handoff/research/objectids.yml', temp/'work/handoff/research/objectids.yml')
        factory = temp/'work/sinking-factory'; factory.mkdir()
        shutil.copytree(ROOT/'work/sinking-factory/audit', factory/'audit')
        for src in (ROOT/'work/sinking-factory').iterdir():
            if src.is_file() and src.suffix in {'.py', '.json', '.level'}:
                shutil.copy2(src, factory/src.name)
        env = dict(os.environ, GD_RESOURCES=str(resources))
        subprocess.run([sys.executable, str(factory/'build_custom_orbs.py')], cwd=temp, env=env, check=True)
        subprocess.run([sys.executable, str(factory/'validate_custom_orbs.py')], cwd=temp, env=env, check=True)
        args.out.mkdir(parents=True)
        for src in [temp/'outputs/The Sinking Factory - CUSTOM-ORBS.gmd',
                    factory/'custom-orbs.level', factory/'custom-orbs-manifest.json', factory/'custom-orbs-validation.json']:
            shutil.copy2(src, args.out/src.name)
    print('Validated rebuild saved to %s' % args.out.resolve())


if __name__ == '__main__':
    main()
