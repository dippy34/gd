# KOCMOC Unleashed — measured decoration (not a visual guess)

Source: published copy **125072075** (`KOCMOC UNLEASHED LDM` on GDBrowser).
The listing is labeled LDM; the downloaded string still has **99,854 objects** and **474 IDs**.
That is the object-level source for this rebuild. Geometry was not copied.

Also checked: GDBrowser listings for later leaks (109381612, 100698755),
the 99-object black-hole recreation (111160043), original KOCMOC (87665224),
and [flowvix object names](https://flowvix.github.io/gd-info-explorer/ids).

## Start colors (kS38)

| Channel | RGB | Blend | Role |
|---|---|---|---|
| 1000 / 1001 | 0,0,0 | no | background / ground |
| 1 / 2 | 0,0,0 | no | default object (overridden per-object) |
| 3 | 87,85,85 | no | mid gray |
| 1003 / 1004 | 255,255,255 | no | white structure / line |
| 1005 / 1006 | 255,255,255 | yes | white glow |
| 10 | 255,227,74 | yes | gold flash |
| 11 | 172,168,168 | yes | gray glow |
| 12 | 192,117,69 | yes | warm brown flash |
| 15 / 17 | 255,182,0 | mixed | amber |
| 25 / 37 / 38 | 4,2,7 / 3,2,6 / 24,21,28 | no | near-black depth |
| 44 | 167,154,190 | no | muted mauve (rare) |

6,983 of 7,644 `square_01` (ID 1) use color **1004** — structures read as **white on black**, not dark stone.

Color triggers (1,450): duration median **0.4 s**. Top RGBs are
`(0,0,0)` 482, `(0,62,206)` 210, `(255,255,255)` 134, then brighter blues.
The drop flashes **black / white / blue**, not violet.

## Highest-count decoration IDs

| ID | Count | Name (flowvix / atlas) |
|---|---|---|
| 1 | 7644 | Black Gradient Square |
| 507 | 5513 | 3DL Top Middle |
| 1764 | 5222 | Tiny Circle |
| 1754 | 3764 | Thin Line Glow |
| 211 | 3276 | Colored Inner Square |
| 1888 | 2953 | Large Glow Orb |
| 1006 | 2926 | Pulse |
| 504 | 2733 | Outer Corner Medium Glow |
| 694 | 2546 | Decorative Colored Wide Slope |
| 1608 | 2505 | Group of Dots 1 (noise) |
| 472 | 2279 | Outline Inner Corner |
| 901 | 2009 | Move |
| 1007 | 1995 | Alpha |
| 3625 | 1682 | Star (scale ≈ 0.05) |
| 899 | 1450 | Color |
| 1011 / 1012 | 1252 / 1333 | Straight / corner large glow |
| 468 | 976 | Outline Top |
| 1753 | 823 | Thin Line |
| 216 | 710 | Colored Spike |
| 1887 / 1886 | 228 / 147 | Small / medium glow orb |
| 1346 | 286 | Rotate (black-hole spin) |

V4 used clouds (48/49/131), cogs (85/86), and violet fog. Those IDs are rare or absent here.

## Structure sandwich (same 15-unit cell)

Most common stacks: `(1,211)` 514, `(211,507)` 285, `(1,211,507)` 191, `(1,507)` 183.

## Scales (median scale-x where set)

- 1888 glow orb: 0.80 (p25 0.45, p75 1.69); start-sky cluster median 0.20
- 1764 dust: 1.17
- 3625 stars: **0.051**
- 504 glow corner: **1.70** almost always
- 1754 line glow: 0.97
- 1608 noise: ~1, many rotations
- 507 3DL: 0.76 × 0.38

## Triggers

- Pulse: fade-in **0**, hold **0.05**, fade-out **0.10**. RGB mostly white / near-white / black / gray.
- Color: 0.4 s, black / blue `(0,62,206)` / white on channel 1004 and custom IDs.
- Alpha: duration median 0.07, opacity often 0 (flicker).
- Rotate sample: duration 999, `full` 9999 — continuous spin, no copied geometry.
- Move: small X, duration median 0.30.

## Z-layers used most

1888 / 1754 at **7** (in front of gameplay). 1764 / 1608 / 507 at **1**. Gameplay squares at **0**.

## What this rebuild takes

Recipes only: white-on-black blocks, 1+211+507 sandwich, glow-orb field,
micro starfield, noise dots, thin line glow on corridor edges, gold/blue flashes
with those pulse/color timings, rotating glow discs in the drop.
Our cube/wave route stays original.
