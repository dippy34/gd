# UI trigger implementation notes

The UI trigger creates a screen-attached layer at level initialization. Group membership is permanent from the start; visibility is therefore controlled with alpha triggers, not by placing the UI trigger at the intended onset. The reference object remains outside the UI groups. Creator documentation: https://www.gdcreatorschool.com/docs/guides/triggers-1/ui-link-visible/

Property mapping was checked against Geode 2.2081 bindings and the locally installed arm64 executable's UIObjectSettingsPopup and GJBaseGameLayer::positionUIObjects functions. This is static inspection, not a native playtest.

- Object ID 3613: `edit_eUISettingsBtn_001.png`, confirmed by local sprite map and native init.
- 51: objects' group ID; native popup calls value control with 0x33.
- 71: UI target reference group; popup calls value control with 0x47.
- 385: X reference. Auto 0/1, center 2, left 3, right 4.
- 386: Y reference. Auto 0/5, center 6, bottom 7, top 8.
- 387 and 388: X/Y relative positioning booleans.
- Reference coordinates are center ±240 horizontally and ±160 vertically, a 480×320 reference. Native code uses 240.0 and 160.0 constants independently of current window size. Relative positions multiply offsets by window width/480 or height/320. Relative positioning is disabled for this effect; each strip is anchored directly to its corresponding edge, and long top/bottom strips cover the supported aspect ratios.

Native inspection evidence is stored in `ui-popup-disasm.txt` and `ui-position-disasm.txt`. The source binding is https://github.com/geode-sdk/bindings/blob/main/bindings/2.2081/GeometryDash.bro (`UISettingsGameObject`).

No group-parent or rotation pivot is needed for this border: each strip receives its own UI mapping and linear Move trigger. The invisible camera reference is not a member of the UI or fire groups. Fire groups 1200–1235 and channels 760–767 were checked against the existing file before export.
