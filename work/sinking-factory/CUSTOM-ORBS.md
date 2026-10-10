# Factory Orbs

Import **The Sinking Factory - CUSTOM-ORBS.gmd** (in-game name **Factory Orbs**).

Restores Refined's original mode, size and speed portal sprites and their previous metal trim. Keeps Custom's eight pressure-switch orbs and all 84 steel spike replacements. Portal native objects no longer belong to hidden-visual group 1157; only the eight custom orb cores remain hidden. All other decoration and existing layer assignments remain unchanged. The blue-orb follow fix remains group 1156.

Exact-data checks compare restored portal objects and artwork against Refined, custom orb artwork against Custom, and all other decoration against Custom. GMD/source/gameplay/group checks are also included in custom-orbs-validation.json. Native playtesting remains unverified.

Build: work/sinking-factory/build_custom_orbs.py. Validate: work/sinking-factory/validate_custom_orbs.py. All shell invocations use rtk proxy /usr/bin/python3.
