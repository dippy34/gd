"""Minimal, dependency-free GD level-string parser."""
import re, json, gzip, base64
from collections import Counter, defaultdict

def load(path):
    s = open(path, 'r', encoding='utf-8', errors='replace').read()
    head, _, body = s.partition(';')
    objs = []
    for chunk in body.split(';'):
        if not chunk.strip():
            continue
        f = chunk.split(',')
        d = {}
        for i in range(0, len(f) - 1, 2):
            d[f[i]] = f[i + 1]
        if '1' in d:
            objs.append(d)
    return head, objs

def parse_header(head):
    out = {}
    f = head.split(',')
    for i in range(0, len(f) - 1, 2):
        out[f[i]] = f[i + 1]
    return out

def parse_ks38(v):
    chans = []
    for entry in v.split('|'):
        if not entry.strip():
            continue
        p = entry.split('_')
        d = {}
        for i in range(0, len(p) - 1, 2):
            d[p[i]] = p[i + 1]
        chans.append(d)
    return chans

def fnum(d, k, default=0.0):
    try:
        return float(d.get(k, default))
    except Exception:
        return default
