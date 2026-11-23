# Guide for the agent (Claude Code or another)

This repository generates, in code, a tablet stand that hangs on the **Meticulous** espresso machine. Whoever cloned it wants to adapt the stand to **their** measurements and printer. Reply in the person's language. The code comments are in English.

## Before generating, ask and confirm
1. **Side**: left (`left_stand.py`) or right, in front of the screen and the button (`right_stand.py`).
2. **Tablet**: model, width × height × thickness, whether it has a **case** (the thickness with the case is what counts), whether it stands in **portrait or landscape**, and where the USB port is.
3. **Machine**, measured with calipers:
   - depth of the top where the hook grips (`column=`, reference 50.6);
   - on the right side, the button: top and bottom below the top of the machine and how far it protrudes from the face (`BUTTON_TOP/BOTTOM/PROTRUSION` in `right_stand.py`, reference 65.07 / 113.08 / 34.13).
4. **Height**: how far the bottom of the tablet sits below the top of the machine (`base=`; 190 with the tablet in portrait, 142 in landscape). Show how far the top of the tablet rises above the machine.
5. **Printer, material and nozzle**. The clearances below were measured in PETG on an Anycubic Kobra S1 with a 0.4 nozzle. Another printer may need a test coupon first.

## Geometry and conventions (read before changing anything)
- The profile is drawn in the **XY** plane, with **X = depth** (front → machine) and **Y = height**, and extruded along **Z = width**.
- The tablet leans on a line at 10° from vertical: `f(y) = 15.3 + inc*(y-4)`.
- The step gap is the thickness / cos 10° + 0.5 (`gap=`).
- **Two parts**: the **frame** (prints lying flat, with the profile on the bed) and the **ledge** (prints lying on its floor). They are joined by a **20° dovetail**:
  - the tongue is on the frame and the channel in the ledge;
  - the channel is closed at one end, which acts as a **stop**.
- **Right side**:
  - The ledge is the left one **mirrored in Z** (`z → 35 − z`).
  - **On the right side the frame sits next to the group head and the ledge runs OUTWARD, away from the machine.** Old comments in `right_stand.py` and `ledge_landscape.py` have "outward/inward" swapped. `ext_outward` in `ledge_landscape.py` ended up on top of the group head, which is why that ledge did not work.
  - The right frame forms a window around the button. `check_button_clearance()` prints the minimum clearance to the button, which must never be 0.
- **Sag compensation** (the ledge gives way under the weight):
  - `tilt=` bends the floor starting at the joint block;
  - `ledge_straight.py` rotates the whole ledge about a pivot just past the block and keeps the channel and the top of the block where the frame expects them (the ledge looks straight).
- **Outputs**: the functions `G.ledge(..., with_channel=False, cable_hole=False, ext_outward=...)` and `G.ledge_channel()` are reused by the variants.

## Clearances that have been tested (PETG, Kobra S1, 0.4 nozzle)
| Item | Result |
|---|---|
| Dovetail 0.30 per side along the run + 0.15 in the last 8 mm | loose |
| 0.20 / 0.10 | still loose |
| **0.10 along the run / 0.00 in the last 8 mm, 0.08 layer** | **firm** (use this) |
| Hook: measurement + 0.25 per side (`column_clearance=`) | fitted the machine |
| Sag with the tablet in portrait (149 wide, ~470 g), loose fit | 3° without compensation; 2.5° left 1° |
| 3.5° straight ledge with the firm fit | −2° (overshot); the firm fit sags only ~1.5° |

Treat everything that is not in this table as **untested** and tell the person so.

## Tuning the compensation (the usual loop)
The sag depends on the tablet's weight (with case), the dovetail fit and the printer, so the first ledge rarely comes out level. Tell the person up front that they will probably **reprint the ledge** once or twice (only the ledge; the frame is reused).
- Ask them to measure with the **phone's level app** (iPhone: Measure app → Level; Android: any bubble-level app) lying on the **top edge of the mounted tablet**, and to say how many degrees and **which end is lower**: the free end of the ledge or the frame end. Ask for a photo if the answer is unclear.
- Correction: **new `deg` = printed `deg` + droop**, with droop positive when the free end is lower and negative when it is higher. Example from this repository: 3.5° printed, read 2° high at the free end → 1.5°.
- Change only the compensation (`deg=` / `tilt=`) between rounds; keep the clearances and the layer height, or the sag changes too.
- Record each round (printed angle → reading) so the next correction starts from data.

## Scripts
| Script | What it does |
|---|---|
| `left_stand.py` | left side and shared functions: `gap= lip= clearance= tight= column= column_clearance=` |
| `right_stand.py` | right side: `base= hole= bridge= n_holes= tilt= run_clearance= end_clearance=` |
| `marked_ledges.py` | ledges with the angle engraved on the front: `deg=2.5,5` |
| `ledge_landscape.py` | long ledge for the tablet in landscape (see the outward/inward warning above): `outward= tilt= back_wall_ext=` |
| `landscape_v2.py` | taller frame (`base=142`) + ledge; `mark=0`, `only=ledge` |
| `ledge_straight.py` | straight ledge with the angle in the joint: `deg=` |
| `ledge_usbc_tunnel.py` | ledge with a tunnel underneath for the 90° USB-C adapter (earlier, deeper version): `deg= tunnel_w= tunnel_h= roof= slit=` |
| `ledge_cable_back.py` | ledge with a pocket for the 90° USB-C adapter and the cable leaving at the back: `deg= port_range=30,100 front_clearance= top_clearance= collar= plug_offset=` |
| `make_3mf.py` | builds the Kobra S1 3MF with the profile in `slicer/`: `side= ver= only= support=1 x:key=value` |
| `slice_cli.py` | slices with the Anycubic Slicer Next command line (path of the .exe at the top) and summarises time, grams and line types |
| `preview*.py` | check images (`preview.py` compares with the original STL, which is not in the repository: put it in `original/` if you have it) |

## How to work here
- Run with `python -I script.py key=value`. Parameters are passed as `key=value`.
- After generating, **check**:
  - `is_watertight` of the meshes;
  - the interference between frame and ledge, assembled and sliding (`ledge_landscape.assembly_interference`);
  - cross-sections in matplotlib with the tablet drawn on top.
- When exporting a rotated part, clean the mesh in manifold3d (`ledge_usbc_tunnel.clean_mesh`). Written in float32, the STL merged vertices and created zero-area faces.
- Changing only the ledge (the channel) lets the already printed frame be reused. Prefer that when possible.
- For another printer, deliver STLs and state the settings: 0.08 layer for the ledge (the channel comes out more accurate), no brim, supports only where the script says.
