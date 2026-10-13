# Secure wireless setup on Linux

Use Android's **Wireless debugging** pairing on Android 11 or newer. This is an optional alternative to USB, not internet-wide remote access. Obtain explicit approval to establish wireless trust and connect to the selected phone. Do not use legacy `adb tcpip 5555`, expose the host ADB server, forward router ports, disable firewalls, or install a persistent service.

## Discover and authorize

1. Check existing `adb version` and `adb help` for `pair`, `connect`, `disconnect`, and `mdns`. Do not install or restart services implicitly. Keep an existing USB connection until wireless access is verified; USB is not required for a fresh wireless-only pairing.
2. Confirm the intended physical phone and trusted local network. Android's supported setup places the phone and workstation on the same Wi-Fi network. A wired Linux host on the same reachable LAN can also work; verify reachability instead of assuming it. Guest/client isolation, corporate networks and blocked mDNS can prevent discovery or connection. This procedure does not change network controls.
3. The human unlocks the phone and enables Developer options → **Wireless debugging**, approving only the intended network. Paths vary by manufacturer. Do not select persistent trust options implicitly.
4. Inspect the selected phone's **Paired devices** and main **IP address & Port**. An already trusted host may connect without pairing again. Never infer trust from USB authorization alone: verify the actual wireless connection.
5. If fresh trust is needed, the human chooses **Pair device with pairing code**. Its temporary IP/port is the **pairing endpoint**, not the main connection endpoint. In a trusted local human-operated terminal, run:

   ```bash
   : "${PAIR_ENDPOINT:?Set to the selected phone displayed pairing IP:port}"
   adb pair "$PAIR_ENDPOINT"
   ```

   The human enters the temporary code directly into the terminal prompt, not chat, agent input, command arguments, screenshots or logs. An agent must hand this secret-entry step to the human rather than dump or parse the code. If the available surface cannot protect entry, stop. QR pairing requires a compatible local pairing UI; do not send pairing secrets to third-party QR services or assume a camera scan alone authorizes the host.

6. Read the **connection endpoint** from the main Wireless debugging page. Set `CONNECT_ENDPOINT` locally to that exact IP:port; do not publish it or guess port 5555. Pairing and connection ports differ and may change. Connect only to this selected endpoint:

   ```bash
   : "${CONNECT_ENDPOINT:?Set to the selected phone main Wireless debugging IP:port}"
   adb connect "$CONNECT_ENDPOINT"
   adb devices -l
   ```

`adb pair` and `adb connect` target an endpoint rather than a device serial, so they do not take `-s`. Discovery and connection are not navigation proof. mDNS is optional discovery, not an authorization substitute:

```bash
adb mdns check
adb mdns services
```

`_adb-tls-pairing._tcp` advertises pairing; `_adb-tls-connect._tcp` advertises secure connection. Empty discovery does not prove Wireless debugging is off: manual connection to the verified displayed endpoint can still work. Match discovered services to the intended phone privately; do not scan the subnet or choose the first advertisement.

## Bind and verify before unplugging

Set `SERIAL` to the exact verified wireless entry in `adb devices -l` (often the connection IP:port; an mDNS service name can also appear). Do not reuse the USB serial for wireless commands or silently fall back to USB.

```bash
: "${SERIAL:?Set to the explicitly selected wireless adb entry}"
adb -s "$SERIAL" get-state
adb -s "$SERIAL" shell id
```

Require `device` and report actual shell identity. If both transports are present, privately compare a stable device identifier exposed by both authorized connections and confirm the physical phone; model names alone are insufficient. Do not include this identifier in shared evidence. For wireless-only setup, human identification of the displayed endpoint and physical phone is required.

Verify the unlocked current surface, fresh hierarchy/screenshot and one approved reversible navigation action using **only** the wireless selector. Then have the human unplug USB, re-list devices, confirm that the USB transport is absent, and repeat navigation/readback. A successful explicitly targeted wireless command cannot use USB as fallback; physical removal additionally proves the cable-free scenario. A connection message alone proves neither.

Use the same [navigation and text](navigation-and-text.md), [evidence ladder](safety-and-verification.md), and selected-device scrcpy checks as USB. Network transport adds no root privileges, lock bypass or private-app access. Network delay can affect observation and typing: verify exact drafts again rather than importing USB text-entry results. Bound retries and stop on stale targets.

## Reconnect and close

- Pairing trust can persist, but connectivity does not necessarily persist after reboot, Wi-Fi changes, Wireless debugging toggles, idle behavior or IP/port changes. Read the current endpoint and reconfirm the selected phone before reconnecting. Re-pair only when trust is actually missing.
- Do not promise access from another network or while the phone is locked. This procedure has no VPN, public relay, router forwarding or unattended unlock.
- With approval, disconnect only this endpoint:

  ```bash
  : "${CONNECT_ENDPOINT:?Use the confirmed endpoint for this session}"
  adb disconnect "$CONNECT_ENDPOINT"
  ```

  Re-list and confirm the selected wireless transport is absent. Disconnecting ends this host connection; it does **not** forget pairing or disable the phone's listener, and discovery may reconnect a still-trusted host.
- Offer human-controlled **Wireless debugging → Paired devices → selected host → Forget**, or disabling Wireless debugging. Explain the effect before changing anything. Turning off USB debugging or unplugging USB is not wireless revocation. Do not delete host keys or revoke other computers.

## Primary sources

- [Android ADB: connect over Wi-Fi](https://developer.android.com/tools/adb#wireless): Android 11+ pairing, network requirements, connection and mDNS troubleshooting.
- [ADB command reference](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/master/docs/user/adb.1.md): endpoint-targeted `pair`/`connect`, selected-device commands and targeted disconnect.
- [scrcpy connection guidance](https://github.com/Genymobile/scrcpy/blob/master/doc/connection.md): device selection and TCP/IP transport. Use paired Android Wireless debugging here, not legacy enablement examples.
