# Android host platforms: Linux, macOS, native Windows

Use this reference for host setup, then return to the skill's observation → approved action → readback procedure. It covers **Linux, macOS, and native Windows only**. A documented upstream route is not a device test performed by this project.

Primary sources reviewed on **2026-10-13**. Platform-specific installation routes can change; inspect the linked maintained documentation before approving a download. This document was researched without installing dependencies or accessing a phone.

## 1. Choose the host and transport

| Host | USB prerequisite | Paired Wireless debugging | Evidence status here |
| --- | --- | --- | --- |
| Linux | Existing platform-tools/ADB, data-capable cable, normal-user USB access; distribution-specific udev/group setup may be needed | Android 11+ phone, current ADB, trusted reachable local network; no USB prerequisite for fresh pairing | Exercised on one Android 16 phone with a Linux x86_64 host; see the capability matrix below |
| macOS | Existing platform-tools/ADB and data-capable cable; Android documents no additional USB-driver configuration | Same Android pairing/connection procedure; host shell, executable paths, and network policy differ | Upstream-documented; not device-tested here |
| Native Windows | Native platform-tools/ADB and data-capable cable; appropriate Google/OEM ADB driver if needed | Same Android pairing/connection procedure; use native executables and PowerShell; USB drivers are not needed for wireless-only operation | Upstream-documented; not device-tested here |

Sources: Android [hardware-device setup][device], [ADB][adb], [platform-tools][platform-tools], [OEM drivers][oem], and [Google USB Driver][google-driver].

### Conditions before any commands

1. Identify the actual host with the cable or local-network access, the intended physical phone, allowed app/account, and allowed actions. A remote terminal or container does not automatically share host USB or LAN access.
2. Discover existing tools and their paths first. Obtain explicit approval before SDK/package/driver installation, pip installation, PATH changes, group/rule/permission changes, phone setting changes, firewall changes, or shared ADB-server restarts. Do not install a package manager just to follow an example.
3. The human enables Developer options and the chosen debugging transport and unlocks locally. For USB, the human checks and accepts the intended host's RSA trust prompt. MTP/file transfer is not USB debugging. For wireless, the human handles pairing consent and the pairing code locally. Secrets never go into chat, agent input, command arguments, logs, or screenshots.
4. Require a human-selected exact ADB entry in state `device`. `unauthorized`, `offline`, and `no permissions` are different failures. `device` proves transport authorization, not an unlocked app, readable hierarchy, successful input, or working video.
5. Every device operation must use `adb -s "$SERIAL"`; every mirroring operation must use `scrcpy --serial "$SERIAL"`. Use the equivalent `$Serial` in PowerShell. Never select the first entry, infer identity from model alone, rely on implicit single-device selection, or silently fall back to another transport.

Discovery and host/endpoint operations such as `adb version`, `adb devices -l`, `adb pair`, and `adb connect` are not device-shell operations. Pair/connect select their explicit endpoint, **not** `-s`. Discovery can start the local user-owned ADB server. Keep that server local; do not expose it publicly. Root, bootloader unlocking, private-data extraction, lock bypass, protected-screen bypass, and legacy unpaired TCP ADB are outside scope.

## 2. Discover ADB and prepare USB

Android distributes standalone SDK Platform-Tools for all three hosts; Android Studio is not required for the CLI route. If Studio is already installed, its SDK Manager can manage platform-tools. Use the [official platform-tools page][platform-tools] rather than third-party binary bundles. Do not run ADB as root or assume elevation is a USB repair.

**Linux/macOS — Bash discovery:**

```bash
command -v adb
adb version
adb devices -l
```

**Native Windows — PowerShell discovery:**

```powershell
Get-Command adb -All
adb version
adb devices -l
```

If discovery cannot resolve `adb`, stop and select an approved installation/executable path. In PowerShell, an extracted executable in the current directory normally needs `.\adb.exe`; it is not found merely because the terminal is in its directory. Replace the `adb` command consistently with `& $Adb` if using a human-confirmed full executable path in `$Adb`. Do not assume the bundled ADB in a scrcpy download and a separately installed SDK copy are the same version. Choose one intended toolchain and inspect its paths/version before changing a shared server.

### Linux USB permissions — Linux only

Android's [hardware-device setup][device] specifically documents **Ubuntu**: the user needs `plugdev` membership and udev rules covering the phone. It identifies `android-sdk-platform-tools-common` as containing community-maintained default rules. Group changes take effect after logout/login; inspect membership with `id` afterward. These are approved remediation options, not automatic steps or requirements for every Linux distribution.

For another distribution, use its maintained device-access guidance rather than copying Ubuntu commands. Do not make USB devices world-writable, run a privileged ADB server, or change broad permissions to repair one phone. After an approved targeted change, reconnect and inspect the intended entry again.

### macOS USB requirements

Android's [hardware-device setup][device] says **no additional configuration is required** for macOS; its [Google USB Driver page][google-driver] says macOS does not need that USB driver. This does not remove the need for ADB, a working data cable, phone-side USB debugging, RSA consent, or human unlock. Do not apply Linux udev/`plugdev` instructions or install Windows drivers on macOS.

### Native Windows USB drivers

Android's [hardware-device setup][device] says to install an ADB USB driver **if applicable**. Its [Google USB Driver page][google-driver] provides the Google-device route; other manufacturers supply their own drivers through the [official OEM-driver guide][oem]. The Google driver is not a universal driver for all brands.

Inspect the intended phone's ADB interface in Device Manager before proposing a change. File-transfer visibility does not prove the ADB interface works. If a driver is missing or incorrect, obtain approval and follow the official manufacturer/Google installation route for that device. Do not download generic driver packs, alter driver INF files, or disable signature enforcement. Android's OEM guide includes older Windows UI examples; do not present those as a newly tested Windows-version compatibility matrix. Some devices expose a supported WinUSB descriptor and need no separate driver installation, as noted in [platform-tools release notes][platform-tools]; that is not a universal exemption.

### Bind the explicitly selected USB or wireless entry

The human sets `SERIAL`/`$Serial` to the **exact** selected `adb devices -l` entry locally. Do not include live identifiers in public receipts.

**Bash — Linux/macOS:**

```bash
(
  set -eu
  : "${SERIAL:?Set SERIAL to the exact human-selected adb entry}"
  STATE=$(adb -s "$SERIAL" get-state)
  [ "$STATE" = device ] || { printf '%s\n' 'Stop: selected entry is not device' >&2; exit 1; }
  adb -s "$SERIAL" shell id
)
```

**PowerShell — native Windows:**

```powershell
if ([string]::IsNullOrWhiteSpace($Serial)) { throw 'Set Serial to the exact human-selected adb entry' }
$State = adb -s "$Serial" get-state
if ($LASTEXITCODE -ne 0 -or "$State".Trim() -ne 'device') { throw 'Stop: selected entry is not device' }
adb -s "$Serial" shell id
if ($LASTEXITCODE -ne 0) { throw 'Selected-device shell check failed' }
```

Report the actual shell identity. Unexpected root identity is a blocker to clarify, not permission to expand access. Reconfirm phone identity after a reconnect or transport change; then observe the authorized current UI before input. These snippets check transport/shell only and do not themselves establish all safety conditions.

## 3. Pair securely over Wireless debugging

For this phone workflow, Android documents **Android 11+**, current SDK Platform-Tools, and workstation/phone on the **same wireless network** [ADB][adb]. Fresh pairing does not require a USB connection. A wired host on a reachable local LAN may work, but it is not a substitute for verifying the documented network conditions on an untested setup. Guest isolation, enterprise policy, VPN routing, or host firewalls may block discovery or connection; do not bypass policy or disable security controls implicitly.

The protocol is the same on the three hosts. Differences are executable paths, shell syntax, installed ADB version, and network permissions—not separate Linux/macOS/Windows phone-pairing procedures.

1. With approval, the human opens Developer options → **Wireless debugging**, authorizes the trusted network, and selects **Pair using pairing code**. Avoid granting persistent trust to an untrusted network.
2. The human reads the temporary **pairing** IP:port into `PAIR_ENDPOINT`/`$PairEndpoint` locally. In a **trusted human-operated terminal outside agent capture**, run the matching block below and type the code only at ADB's interactive prompt. An agent must not run this pairing block or collect its secret-bearing terminal interaction.
3. After pairing, inspect connection discovery. If not connected automatically, read the **connection** IP:port from the main Wireless debugging page, set `CONNECT_ENDPOINT`/`$ConnectEndpoint`, and run the connection block. Pairing and connection ports are different and can change; do not reuse the pairing port or assume a fixed port.
4. Inspect `adb devices -l`. Pairing success is not proof of an authorized connected entry. Set `SERIAL`/`$Serial` to the exact human-verified wireless entry, which may be an IP:port or an mDNS-derived name. Use selected-device checks above and fresh consented UI observation to verify the same physical phone.

**Pairing — human-only Bash:**

```bash
: "${PAIR_ENDPOINT:?Set to the selected phone temporary pairing IP:port}"
adb pair "$PAIR_ENDPOINT"
```

**Pairing — human-only PowerShell:**

```powershell
if ([string]::IsNullOrWhiteSpace($PairEndpoint)) { throw 'Set the selected phone temporary pairing IP:port' }
adb pair "$PairEndpoint"
if ($LASTEXITCODE -ne 0) { throw 'Pairing failed; do not continue' }
```

**Connection — Bash:**

```bash
: "${CONNECT_ENDPOINT:?Set to the selected phone main Wireless debugging IP:port}"
adb connect "$CONNECT_ENDPOINT"
adb devices -l
```

**Connection — PowerShell:**

```powershell
if ([string]::IsNullOrWhiteSpace($ConnectEndpoint)) { throw 'Set the selected phone main Wireless debugging IP:port' }
adb connect "$ConnectEndpoint"
if ($LASTEXITCODE -ne 0) { throw 'Connection failed; do not continue' }
adb devices -l
```

ADB uses mDNS for automatic discovery [ADB][adb]. If supported by the installed version, `adb mdns services` can help inspect discovery; an empty list alone does not establish why it failed. Manual `adb connect` to the exact displayed connection endpoint is still a useful bounded check. Re-read the endpoint after network, reboot, or debugging-toggle changes. Do not assume pairing guarantees future automatic reconnection.

**Version caution:** the reviewed Android ADB guide discusses newer Android 17/ADB 37 Wi-Fi behavior and mDNS backend switches, while the [37.0.1 release notes][platform-tools] say the Openscreen backend and its environment switch were removed. Prefer the installed version/help and matching release notes over a timeless backend recipe. Do not add backend environment changes or server restarts by default. Android 16 testing here does not verify Android 17 features.

For cable-free acceptance, first verify the wireless entry, then have the human physically remove USB. Require the USB entry absent, recheck the selected wireless entry, and repeat fresh observation, one approved benign navigation action, and result readback. If video is requested, verify changing frames on that selected wireless entry. Do not silently use USB fallback.

At closure, with approval use `adb disconnect "$CONNECT_ENDPOINT"` (Bash) or `adb disconnect "$ConnectEndpoint"` (PowerShell) for the exact host connection. This is an endpoint operation, not a `-s` shell operation. It does **not** revoke pairing. The human can forget the selected host under Wireless debugging or disable Wireless debugging. Unplugging USB is not wireless revocation; broad authorization revocation can affect other trusted hosts [ADB][adb].

### Optional Tailscale route

Use the [Tailscale endpoint workflow](setup-tailscale-wireless.md) only with already authorized clients/paired host trust, Android Wi-Fi, an explicitly confirmed peer IPv4 and the current TLS connection port. It includes Bash and native PowerShell endpoint guards, exact hardware-identity checks, fresh observation/input/readback, and targeted closure with no silent USB/LAN fallback. On Android 16/Linux, the explicitly selected Tailscale endpoint proved authorized non-root shell, USB-baseline identity, decoded screenshot/hierarchy and reversible Settings navigation/readback while both phones were on home Wi-Fi. This is not an off-LAN/cellular test, nor macOS/Windows runtime evidence. Physical USB removal must be verified separately.

## 4. Optional scrcpy: host routes and conservative launch

[scrcpy upstream][scrcpy] documents Linux, macOS, and Windows, Android 5.0/API 21+ for normal screen mirroring, and Android 11+ for audio forwarding. Secure paired wireless in this reference still requires Android 11+. scrcpy requires no root and no persistent installed phone app; normal operation nevertheless runs a temporary server on the phone. A display-capable host session and working device encoding/host playback are separate prerequisites for visible mirroring.

| Host | Maintained upstream route; approval required before installation |
| --- | --- |
| Linux | [Linux instructions][scrcpy-linux]: official release archive for an available matching architecture, a sufficiently current distribution package, or upstream build/install procedure. The reviewed page marks Debian/Ubuntu and Snap packages obsolete; do not assume a package name guarantees a suitable version. Do not install an x86_64 archive on another architecture. |
| macOS | [macOS instructions][scrcpy-macos]: official release archives for Apple Silicon/aarch64 or Intel/x86_64; Homebrew `brew install scrcpy` plus ADB on PATH (upstream lists `brew install --cask android-platform-tools` if needed); MacPorts is another documented route. |
| Native Windows | [Windows instructions][scrcpy-windows]: official release ZIP matched to the available architecture, or WinGet `winget install --exact Genymobile.scrcpy` (upstream says ADB/dependencies are installed alongside it). Chocolatey/Scoop are alternatives, not additional prerequisites. Use native executables in a terminal so errors remain visible. |

Download only from the official Genymobile repository/release route. Check the **exact asset name, architecture, and matching upstream SHA-256** before executing it; use the [release signature guide][scrcpy-signatures] when available. The reviewed Windows page's ARM64 label links to a win32 asset: do not follow that mismatched link blindly; verify the actual release listing and matching checksum instead. This reference deliberately does not pin a changing release or endorse that link mismatch.

Inspect `scrcpy --version` and `scrcpy --help` first. If the installed version supports these flags, begin with observation-only mirroring [selection][scrcpy-connection], [control/clipboard][scrcpy-control]:

**Bash:**

```bash
: "${SERIAL:?Select and verify the exact intended phone first}"
scrcpy --serial "$SERIAL" --no-control --no-audio --no-clipboard-autosync
```

**PowerShell:**

```powershell
if ([string]::IsNullOrWhiteSpace($Serial)) { throw 'Select and verify the exact intended phone first' }
scrcpy --serial "$Serial" --no-control --no-audio --no-clipboard-autosync
if ($LASTEXITCODE -ne 0) { throw 'Mirroring failed; inspect the visible error' }
```

Recheck selected-device authorization before launch. Verify **visible changing frames**, not merely server startup or a running process. Close only the task-owned scrcpy session. Do not enable control, audio, recording, clipboard synchronization, keep-awake, or screen-off behavior implicitly. Protected/black frames are a limitation to report, not permission to bypass protection. Some OEMs require a separate security setting for input injection; upstream mentions this, but changing it/rebooting needs explicit approval.

Although upstream connection docs also describe legacy automatic TCP setup, **do not use `scrcpy --tcpip` or the legacy `adb tcpip` route** here. Pair/connect using Android Wireless debugging first, then launch scrcpy against the exact verified entry.

## 5. Honest tested-capability matrix

These are the project's reported existing device results, from its acceptance record and README—not new tests performed while researching this reference. No raw serials, account names, codes, captures, or private receipts belong in a public skill bundle.

| Capability | Linux USB, one Android 16 phone | Linux paired wireless, same phone | macOS | Native Windows |
| --- | --- | --- | --- | --- |
| Authorized transport and non-root shell | Exercised | Exercised | Upstream-documented; not tested here | Upstream-documented; not tested here |
| Hierarchy, screenshot, benign navigation/readback | Exercised | Exercised with cable physically removed | Not tested here | Not tested here |
| Visible changing scrcpy frames | Exercised | Exercised | Upstream-documented; not tested here | Upstream-documented; not tested here |
| Exact approved ASCII draft, no submission | Exercised over USB | Not separately tested | Not tested here | Not tested here |
| Reboot/network-change reconnection | No general coverage claimed | Not tested | Not tested here | Not tested here |

Repository validator/CLI E2E results prove documentation/package checks, **not** phone behavior or another host's compatibility. There is no OEM-wide, all-Android-version, Unicode/IME, protected-screen, root, or unattended-unlock guarantee. Windows/macOS documentation does not prove that a chosen Agent Skill consumer, repository Makefile, Bash/Ruby validator, or every existing shell example runs natively there. Translate/test host-shell and binary-file handling separately before claiming portable execution.

## Primary sources

All sources below are Android Developers or maintained Genymobile scrcpy documentation, reviewed 2026-10-13. Host/device prerequisites and driver statements come from Android; scrcpy routes/flags come from Genymobile. Project test claims come only from the local acceptance record and README.

- [Android Developers — Run apps on a hardware device][device]: host USB setup, Ubuntu permissions, macOS configuration, RSA authorization.
- [Android Developers — Android Debug Bridge][adb]: CLI availability, paired wireless prerequisites/pairing, discovery and selection, revocation.
- [Android Developers — SDK Platform Tools release notes/downloads][platform-tools]: standalone host downloads, version-sensitive backend behavior, WinUSB notes.
- [Android Developers — Install OEM USB drivers][oem]: manufacturer-specific Windows driver installation.
- [Android Developers — Get the Google USB Driver][google-driver]: Google-device Windows route; no such driver required on macOS/Linux.
- [Genymobile — scrcpy README][scrcpy]: documented host support and device prerequisites.
- [Genymobile — Linux installation][scrcpy-linux], [macOS installation][scrcpy-macos], [Windows installation][scrcpy-windows]: host-specific releases/package routes.
- [Genymobile — Connection][scrcpy-connection]: exact serial selection and ADB transport.
- [Genymobile — Control][scrcpy-control]: read-only and clipboard flags.
- [Genymobile — Verify release signatures][scrcpy-signatures]: signed checksum verification.

[device]: https://developer.android.com/studio/run/device
[adb]: https://developer.android.com/tools/adb
[platform-tools]: https://developer.android.com/tools/releases/platform-tools
[oem]: https://developer.android.com/studio/run/oem-usb
[google-driver]: https://developer.android.com/studio/run/win-usb
[scrcpy]: https://github.com/Genymobile/scrcpy
[scrcpy-linux]: https://github.com/Genymobile/scrcpy/blob/master/doc/linux.md
[scrcpy-macos]: https://github.com/Genymobile/scrcpy/blob/master/doc/macos.md
[scrcpy-windows]: https://github.com/Genymobile/scrcpy/blob/master/doc/windows.md
[scrcpy-connection]: https://github.com/Genymobile/scrcpy/blob/master/doc/connection.md
[scrcpy-control]: https://github.com/Genymobile/scrcpy/blob/master/doc/control.md
[scrcpy-signatures]: https://github.com/Genymobile/scrcpy/blob/master/doc/verify-release.md
