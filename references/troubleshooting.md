# Bounded troubleshooting

Collect the exact symptom, selected transport state, installed versions and current non-sensitive UI context. Retry once after a targeted, approved correction and fresh observation; stop on repeated failure or ambiguity. Separate observation from suspected cause.

| Symptom | Next check / boundary |
| --- | --- |
| No `adb` | Propose maintained platform-tools source; obtain install approval. Do not claim phone capability. |
| USB visible but no ADB entry | Data cable/port, human-enabled USB debugging, manufacturer USB mode. MTP is not debugging. |
| `unauthorized` | Human unlock and RSA acceptance on intended phone. Re-list; never bypass or delete trust keys automatically. |
| `offline` | Check cable and selected connection. Obtain approval before reconnect/server restart; do not treat as authorized. |
| `no permissions` | Distro rules/group membership and current login session. Ubuntu `plugdev`/rules guidance is not universal. After approved correction, selected-device reconnect and possibly user-server restart can clear stale access. |
| Wireless enabled but no connection | Verify the selected phone's current connection endpoint and existing pairing. A toggle alone is insufficient; pairing and connection ports differ. See [secure wireless setup](setup-linux-wireless.md). |
| Empty mDNS discovery | Does not prove wireless is disabled. Try the verified displayed connection endpoint; do not scan the LAN or restart shared services blindly. |
| Paired but connect fails after network/reboot/toggle | Re-read the current endpoint; ports and addresses may change. Check trusted LAN reachability/client isolation without changing network controls. |
| Cable unplugged, selected entry unavailable | Stop; verify a wireless entry explicitly before claiming cable-free control. Never silently fall back to USB. |
| More than one entry | Stop and have intended entry identified; bind all commands to exact `SERIAL`. |
| Reconnected phone / changed transport | Reconfirm selection and authorization. Never silently fall back to another entry. |
| `device`, but lock screen | Human unlock required. Authorized shell does not imply unlocked UI. No PIN capture or automated bypass. |
| Hierarchy timeout / missing text | Confirm app and idle UI, retry once, then fresh screenshot if approved. Custom views may omit nodes. Do not invent IDs/text. |
| Black screenshot | Check decoded file and non-sensitive UI/human report. Secure content may block images while text remains readable. Do not bypass protections. |
| Tap hits wrong object | Stop. Refresh geometry, rotation, account and adjacent content; inspect clickable parent. Do not keep tapping stale coordinates. |
| Launch succeeded but focus stale/null | Transition may still be running, including after `am start -W`. Bound fresh focus/UI checks until the expected package and surface appear; no blind fixed sleep or launch-success claim. |
| Back returns an older screen | Existing task stack can expose an older subscreen. Compare current UI with recorded initial app/component and verify any approved restoration; one Back is not proof. |
| Unexpected dialog/account/app | Stop and report. Do not accept permission dialogs or switch accounts without specific approval. |
| Input drops/changes characters | Exact field readback, focus and IME check. Approved clear/replacement followed by slow ASCII entry; no blind append/retry. |
| Ctrl+A unsupported/ineffective | Check live `input` usage and benign field behavior. Use confirmed UI selection/human assistance, not guessed keycodes. |
| Unicode/percent/multiline mismatch | ADB text is not arbitrary text transport. Test safe alternatives with consent or request human entry; do not replace content with ASCII silently. |
| scrcpy starts then crashes | Check installed version and error, particularly Android API/encoder mismatches. Consult upstream compatible release and checksum; no blind downgrade or old distro install. |
| scrcpy logs server start but no frames | Inspect actual display/decoded stream. GUI/display or codec failures differ from ADB authorization. Do not report streaming success from process exit/start alone. |
| Image/recording file exists but unusable | Decode/play it and verify frames. Empty/corrupt files and black frames are not proof of usable observation. Avoid recording unless explicitly needed and authorized. |
| Potential submit occurred | Do not retry send/post. Inspect exact destination once if safe, report uncertain state, and obtain direction. Absence from current screen is not proof of failure. |

ADB server restarts can disrupt unrelated sessions. Never use blanket privileged repairs, root ADB, global USB re-triggers, unapproved network-debug enablement or legacy TCP ADB, clipboard extraction, app database pulls, or lock/security bypasses to rescue this workflow. Capture only narrowly relevant diagnostics; raw logs can include personal data.

Sources: [Android ADB](https://developer.android.com/tools/adb), [hardware setup](https://developer.android.com/studio/run/device), [scrcpy Linux](https://github.com/Genymobile/scrcpy/blob/master/doc/linux.md), [scrcpy control](https://github.com/Genymobile/scrcpy/blob/master/doc/control.md).
