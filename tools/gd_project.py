"""Small, portable, read-first CLI for this GDShare project (standard library)."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'work/handoff/tools'))
import gmd
import gdparse


def read_level(path):
    path = Path(path)
    fields = gmd.read_gmd(path) if path.suffix.lower() == '.gmd' else None
    raw = gmd.decompress(fields['k4'][1]) if fields else path.read_text(encoding='utf-8')
    chunks = raw.split(';')
    objects = []
    for index, chunk in enumerate(chunks[1:]):
        if not chunk.strip():
            continue
        tokens = chunk.split(',')
        if len(tokens) % 2:
            raise ValueError('Odd property count at object chunk %d' % index)
        obj = dict(zip(tokens[::2], tokens[1::2]))
        if '1' not in obj:
            raise ValueError('Missing object ID at chunk %d' % index)
        for key in ('1', '2', '3'):
            if key in obj and not math.isfinite(float(obj[key])):
                raise ValueError('Non-finite property at chunk %d' % index)
        objects.append(obj)
    return fields, raw, gdparse.parse_header(chunks[0]), objects


def summary(path):
    fields, raw, header, objects = read_level(path)
    bounds = {key: [min(float(o.get(key, 0)) for o in objects),
                    max(float(o.get(key, 0)) for o in objects)] for key in ('2', '3')} if objects else {}
    membership = {int(v) for o in objects for v in o.get('57', '').split('.') if v}
    return {
        'path': str(path), 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        'name': fields.get('k2', ('s', None))[1] if fields else None,
        'song_id': fields.get('k45', ('i', None))[1] if fields else None,
        'parsed_objects': len(objects),
        'stored_object_count': fields.get('k48', ('i', None))[1] if fields else None,
        'bounds_including_editor_only_objects': bounds,
        'object_ids': dict(Counter(o['1'] for o in objects).most_common(25)),
        'primary_layers': dict(Counter(o.get('20', '0') for o in objects)),
        'secondary_layers': dict(Counter(o.get('61', '0') for o in objects)),
        'membership_group_range': [min(membership), max(membership)] if membership else [],
        'group_note': 'Range describes field57 only, not an allocator or proof of free IDs.',
        'color_channels': len(gdparse.parse_ks38(header.get('kS38', ''))),
        'native_playtest': False,
    }


def select_region(path, x0, x1, limit):
    objects = read_level(path)[3]
    selected = [{'index': i, 'properties': o} for i, o in enumerate(objects)
                if x0 <= float(o.get('2', 0)) < x1]
    return {'selection': 'Object centers in [x0,x1); not an animation/collision extent test.',
            'x0': x0, 'x1': x1, 'matching_objects': len(selected),
            'returned_objects': selected[:limit], 'truncated': len(selected) > limit}


def compare(a, b, limit):
    fa, ra, ha, aa = read_level(a)
    fb, rb, hb, bb = read_level(b)
    changed = []
    for i, (x, y) in enumerate(zip(aa, bb)):
        if x != y:
            changed.append({'index': i, 'keys': sorted(k for k in x.keys() | y.keys() if x.get(k) != y.get(k))})
    return {'comparison': 'Index-aligned; meaningful for preserved-source/prefix workflows, not reordered levels.',
            'objects_before': len(aa), 'objects_after': len(bb),
            'equal_raw_level_strings': ra == rb,
            'common_prefix_objects': next((i for i, (x, y) in enumerate(zip(aa, bb)) if x != y), min(len(aa), len(bb))),
            'changed_common_indices': len(changed), 'sample_changes': changed[:limit],
            'header_changed_keys': sorted(k for k in ha.keys() | hb.keys() if ha.get(k) != hb.get(k)),
            'truncated': len(changed) > limit}


def clone_level(source, destination, name):
    destination = Path(destination)
    if destination.suffix.lower() != '.gmd':
        raise ValueError('Copy output must end in .gmd')
    if destination.exists():
        raise FileExistsError('Refusing to overwrite: %s' % destination)
    fields, raw, _, objects = read_level(source)
    if fields is None:
        raise ValueError('Copy requires a .gmd source to preserve its metadata')
    original_fields = dict(fields)
    fields['k2'] = ('s', name)
    fields['k1'] = ('i', '0')
    fields['k16'] = ('i', '0')
    fields['k48'] = ('i', str(len(objects)))
    destination.parent.mkdir(parents=True, exist_ok=True)
    gmd.write_gmd(destination, fields)
    result = read_level(destination)
    assert result[1] == raw, 'Cloning must not change the level string'
    assert {k:v for k,v in fields.items() if k not in {'k2','k1','k16','k48'}} == {
        k:v for k,v in original_fields.items() if k not in {'k2','k1','k16','k48'}}
    return summary(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('inspect'); p.add_argument('file')
    p = sub.add_parser('region'); p.add_argument('file')
    p.add_argument('--x0', type=float, required=True); p.add_argument('--x1', type=float, required=True)
    p.add_argument('--limit', type=int, default=20)
    p = sub.add_parser('diff'); p.add_argument('before'); p.add_argument('after'); p.add_argument('--limit', type=int, default=20)
    p = sub.add_parser('copy'); p.add_argument('source'); p.add_argument('destination'); p.add_argument('--name', required=True)
    args = parser.parse_args()
    if args.command == 'inspect': result = summary(args.file)
    elif args.command == 'region':
        if args.x1 <= args.x0 or args.limit < 0: parser.error('Use x1>x0 and a nonnegative limit')
        result = select_region(args.file, args.x0, args.x1, args.limit)
    elif args.command == 'diff':
        if args.limit < 0: parser.error('Use a nonnegative limit')
        result = compare(args.before, args.after, args.limit)
    else: result = clone_level(args.source, args.destination, args.name)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
