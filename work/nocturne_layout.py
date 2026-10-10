"""Preserve v8's score, ease wave geometry, and use a near-black palette."""
import base64
import json
import branching_layout as B
from gmd import read_gmd, write_gmd, compress
from gdparse import load, parse_header, parse_ks38

ROOT = B.ROOT


class NocturneLevel(B.BranchLevel):
    def envelope(self, s, a, b, pad=0):
        # Add measured clearance around the unchanged wave trajectory. Every
        # corridor, knife gate, floating gate and phrase boundary uses this.
        return super().envelope(s, a, b, pad + (5.5 if s['mode'] == 'wave' else 0))


def main():
    B.BranchLevel = NocturneLevel
    level = B.build()
    head, _ = load(str(ROOT / 'work/v8-branching.level'))
    header = parse_header(head)
    colors = {
        1000: (0, 0, 0), 1001: (0, 0, 0), 1002: (8, 9, 7),
        1: (5, 6, 5), 2: (12, 14, 10), 3: (14, 16, 11),
        4: (22, 25, 17), 5: (0, 0, 0), 6: (8, 10, 7),
        7: (19, 22, 14), 13: (26, 29, 20),
    }
    channels = {int(c['6']): c for c in parse_ks38(header['kS38'])}
    for channel, rgb in colors.items():
        channels[channel] = {'1': str(rgb[0]), '2': str(rgb[1]), '3': str(rgb[2]),
                             '4': '-1', '5': '0', '6': str(channel), '7': '1',
                             '15': '1', '18': '0', '8': '1'}
    header['kS38'] = '|'.join('_'.join(f'{k}_{v}' for k, v in c.items()) for c in channels.values()) + '|'
    for obj in level.objects:
        if obj['1'] == '1594':
            # Keep the native input object and its trigger logic. Replacement
            # artwork is added after the structural skin pass.
            obj.update({'135': '1', '96': '1', '507': '1', '372': '1',
                        '21': '13', '22': '13'})
    serialize = lambda obj: ','.join(f'{k},{v}' for k, v in obj.items())
    raw = ';'.join([serialize(header)] + [serialize(o) for o in level.objects]) + ';'
    fields = read_gmd(ROOT / 'outputs/v8-1573528-branching.gmd')
    fields['k4'] = ('s', compress(raw))
    fields['k48'] = ('i', str(len(level.objects)))
    fields['k14'] = ('f', False)
    write_gmd(ROOT / 'work/nocturne-base.gmd', fields)
    (ROOT / 'work/v8-nocturne-base.level').write_text(raw)
    plan = dict(sections=level.sections, controls=sorted(level.controls, key=lambda e: e['time']),
                paths=level.paths, rectangles=level.rects, spikes=level.spikes,
                orbs=level.orbs, memories=level.memories, gates=level.gates,
                moves=level.moves, timing_features=level.timing_features, fakeouts=[],
                random_locks=level.random_locks, phrases=level.phrases,
                speed_schedule=[[s['t0'], s['speed']] for s in level.sections],
                end_time=B.M.END, end_x=B.M.xt(B.M.END), bpm=131, song=1573528,
                phase=B.M.PHASE, objects=len(level.objects),
                slow_percent=100 * sum(s['t1'] - s['t0'] for s in level.sections if not s['speed_index']) / B.M.END,
                wave_extra_clearance_each_side=5.5,
                validation_limit='Approximate route model; native completion unverified.')
    old = json.loads((ROOT / 'work/branching-plan.json').read_text())
    assert old['controls'] == plan['controls']
    assert old['paths'] == plan['paths']
    assert old['random_locks'] == plan['random_locks']
    (ROOT / 'work/nocturne-plan.json').write_text(json.dumps(plan, separators=(',', ':')))
    print(json.dumps(dict(base_objects=len(level.objects), inputs=len(level.controls),
                          unchanged_inputs=True, wave_extra_clearance_per_side=5.5)))


if __name__ == '__main__':
    main()
