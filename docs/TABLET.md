# XP-Pen Artist 15.6 Pro V2 on Linux

Checked on 2026-10-20. Linux tablet support changes quickly, so re-check
anything marked "not verified" before relying on it.

## What is known

| Fact | Source |
|---|---|
| The Linux kernel has no dedicated driver entry for this model yet: its USB ID `28bd:096f` is not listed in the kernel's HID ID table (checked against Linux 7.4-rc1, 2026-10-19). The pen may still work through the generic HID driver, but possibly with limits. | [Linux `drivers/hid/hid-ids.h`](https://github.com/torvalds/linux/blob/master/drivers/hid/hid-ids.h) |
| OpenTabletDriver lists the Artist 15.6 Pro V2 as **supported** (16,383 pressure levels, 2 pen buttons, 8 express keys, 1 dial). | [OpenTabletDriver TABLETS.md](https://github.com/OpenTabletDriver/OpenTabletDriver/blob/master/TABLETS.md) |
| XP-Pen offers its own Linux driver for this model (version 4.0.15 from 2026-04-23, as .deb, .rpm and .tar.gz). The download page says nothing about Wayland. | [XP-Pen download page](https://www.xp-pen.com/download/artist-15-6-pro-v2.html) |
| Krita 6 has improved Wayland support compared with Krita 5. | [Phoronix](https://www.phoronix.com/news/Krita-6.0-Released) |

## Recommended order

Try the steps in order and stop as soon as pressure and pen position are right.

### 1. Plug in and test, no driver

1. Connect the display (HDMI or USB-C) and the USB cable.
2. Open Krita: **Settings > Configure Krita > Tablet settings > Open Tablet Tester**.
3. Draw a stroke from light to hard pressure. The pressure value should run smoothly from about 0 to 1.
4. Check that the cursor sits exactly under the pen tip on the pen display, not on the other monitor.

If the pen lands on the wrong screen: on KDE Plasma, map the tablet to the
pen display under **System Settings > Drawing Tablet** (not verified for
this exact model).

### 2. If pressure is missing or wrong: OpenTabletDriver

1. Install OpenTabletDriver from your distribution or from
   [opentabletdriver.net](https://opentabletdriver.net).
2. Start its daemon, open the app, select the Artist 15.6 Pro V2, and map the
   output area to the pen display.
3. Test again with Krita's Tablet Tester.

Do not run the XP-Pen driver and OpenTabletDriver at the same time. In one
forum report, an XP-Pen display only reached half pressure in Krita with the
official driver installed and worked after switching to OpenTabletDriver
([Krita Artists, 2025-06](https://krita-artists.org/t/pressure-problem-linux-mint/126688));
that was a different model, so treat it as a hint, not a rule.

### 3. Last resort: XP-Pen's own driver

Install the .deb or .rpm from the XP-Pen page. Prefer an X11 session if it
misbehaves on Wayland (not verified).

## Making the pen feel like CSP

Pen feel is mostly the **pressure curve** and **stabilization**:

1. In CSP (still on Windows), note her pen pressure settings: in CSP's
   preferences or the pressure adjustment dialog, check the curve shape.
2. In Krita: **Settings > Configure Krita > Tablet settings > Pressure curve**.
   Shape it like the CSP curve. This is global, for all brushes.
3. Stabilization: in the **Tool Options** tab (next to Tool Property), set
   *Brush Smoothing* to *Stabilizer* or *Weighted* and adjust the distance.
   CSP's default stabilization is mild; start low.
4. Per brush: open Krita's brush editor (the brush settings button in the
   top toolbar) and adjust the *Size* and *Opacity* pressure curves.
