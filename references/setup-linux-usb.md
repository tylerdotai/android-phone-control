# Linux USB setup

For explicitly approved cable-free access, see [secure wireless setup](setup-linux-wireless.md). Do not substitute legacy TCP/IP enablement for paired Wireless debugging.

## Discover first

Run on the Linux host that physically owns the USB connection, not an unrelated container or remote terminal:

```bash
command -v adb
command -v scrcpy
uname -m
adb version
adb devices -l
```

`scrcpy` is optional. ADB commands may start its local user server. If ADB is missing, stop and propose an installation source before installing. USB visibility (`lsusb`, if available) establishes attachment only; charging and MTP do not establish debugging. Use a data-capable cable and direct port if transport is unreliable.

Have the owner select the intended entry from `adb devices -l` and set `SERIAL` locally to that exact serial. Do not expose real serials in shared artifacts. Every subsequent device command uses `adb -s "$SERIAL"`; `scrcpy` uses `--serial "$SERIAL"`. Multiple phones/emulators require explicit selection, not automatic first-device logic.

## Human authorization

1. Have the human enable Developer options and USB debugging using the device manufacturer's UI. Paths vary; do not change security settings on the person's behalf without approval.
2. Connect USB and have the human unlock the phone locally.
3. Have the human inspect and accept the **Allow USB debugging?** RSA prompt for the trusted host. Persistent **Always allow** is a separate choice; do not select it automatically.
4. Re-list devices. `unauthorized` means acceptance is still missing; `offline` is not authorization. Require the selected entry to show `device`.
5. Run `adb -s "$SERIAL" get-state` and `adb -s "$SERIAL" shell id`. These establish transport and shell access, not screen unlock or input/screenshot capability. Confirm an unlocked task screen separately with the human/current UI.

Never automate a lock bypass, collect the unlock credential, or accept a prompt by blindly tapping coordinates.

## Linux permission branch

Read the exact failure before repairing. `no permissions` differs from `unauthorized`. On **Ubuntu**, Android's official guide specifies membership in `plugdev` and udev rules supplied by `android-sdk-platform-tools-common`. Adding group membership requires logging out/in to become effective. Check existing packages, group membership and rules first; explain and get approval for any install, group change, privileged rule reload or selected-device USB re-trigger. Other distributions have different packages/group policies: consult their maintained documentation instead of reusing Ubuntu commands.

After an approved rule change and targeted reconnection, re-list devices as the normal user. Stale ADB permissions may require an approved **user-owned** server restart; `adb kill-server` affects all transports on that server. Do not run ADB as root, grant world-writable USB permissions, trigger every USB device, delete host keys, or restart unrelated services as a blanket fix.

## Optional scrcpy provisioning

Check `scrcpy --version` and `scrcpy --help` first. Consult upstream [Linux installation](https://github.com/Genymobile/scrcpy/blob/master/doc/linux.md) and [releases](https://github.com/Genymobile/scrcpy/releases). Upstream flags Debian/Ubuntu `apt install scrcpy` and Snap builds as obsolete; availability does not establish Android compatibility.

If an upgrade is needed, obtain approval for source/download/destination and dependencies. Select an upstream release asset matching `uname -m`; static Linux assets may not exist for every architecture. Verify its SHA-256 against upstream's checksum for that exact asset before extraction/execution. Never reuse a version/hash from a different architecture or pin this skill to today's latest version. Follow the current upstream build route when no matching binary exists; do not improvise an install script.

Accept mirroring only after real frames display and change. If supported by installed help, begin with:

```bash
: "${SERIAL:?Select the intended phone first}"
scrcpy --serial "$SERIAL" --no-control --no-audio --no-clipboard-autosync
```

This does not enable keep-awake or turn off the phone screen. Do not add those settings implicitly. Stop the test normally; a running process or server message alone is not proof of a working stream.

## Primary sources

- [Android ADB](https://developer.android.com/tools/adb): serial selection, transport states, RSA authorization, shell.
- [Android hardware-device setup](https://developer.android.com/studio/run/device): USB debugging, Ubuntu groups and rules.
- [scrcpy Linux](https://github.com/Genymobile/scrcpy/blob/master/doc/linux.md): maintained install routes and checksum procedure.
