"""Read/write GDShare .gmd (plist wrapper around a gzip+base64 level string)."""
import gzip, base64, xml.etree.ElementTree as ET, zlib
from xml.sax.saxutils import escape

def _b64d(s):
    s = s.replace('-', '+').replace('_', '/')
    s += '=' * (-len(s) % 4)
    return base64.b64decode(s)

def decompress(s):
    raw = _b64d(s)
    try:
        return gzip.decompress(raw).decode('utf-8', 'replace')
    except Exception:
        return zlib.decompress(raw, -15).decode('utf-8', 'replace')

def compress(s):
    import io
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', mtime=0) as f:
        f.write(s.encode())
    return base64.urlsafe_b64encode(buf.getvalue()).decode()

def read_gmd(path):
    root = ET.parse(path).getroot()
    d = root[0]
    out = {}
    kids = list(d)
    i = 0
    while i < len(kids) - 1:
        if kids[i].tag == 'k':
            key = kids[i].text
            v = kids[i + 1]
            out[key] = (v.tag, v.text if v.tag != 't' and v.tag != 'f' else (v.tag == 't'))
            i += 2
        else:
            i += 1
    return out

def write_gmd(path, fields, order=None):
    lines = ["<?xml version='1.0' encoding='utf-8'?>", '<plist version="1.0" gjver="2.0"><dict>']
    for k in (order or fields):
        tag, val = fields[k]
        if tag in ('t', 'f'):
            lines.append(f'<k>{k}</k><{"t" if val else "f"} />')
        else:
            lines.append(f'<k>{escape(str(k))}</k><{tag}>{escape(str(val))}</{tag}>')
    lines.append('</dict></plist>')
    with open(path, 'w', encoding='utf-8') as output:
        output.write(''.join(lines))
