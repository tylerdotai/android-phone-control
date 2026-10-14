# Paired Wireless debugging through Tailscale

Use this optional route when the human has already authorized Tailscale and Android Wireless debugging on the intended host and phone. Tailscale carries the existing paired ADB TLS connection; it does not replace Android pairing, unlock the phone, or add root privileges. Ordinary [USB](setup-linux-usb.md) and [paired LAN Wi-Fi](setup-linux-wireless.md) remain separate supported routes.

## Conditions

1. The Android 11+ phone is connected to **Wi-Fi**, with Wireless debugging enabled. Android requires Wi-Fi for this workflow even when ADB traffic uses Tailscale. Do not treat cellular-only service as a supported substitute.
2. Existing Tailscale clients on host and phone are connected to the same authorized tailnet. The human confirms the intended phone's peer identity and literal Tailscale IPv4 address, and that incoming connections to it are allowed by client settings and tailnet policy. Do not install clients, change access rules, disable firewalls, or enable incoming access without separate approval.
3. Use an existing, inspected SDK Platform-Tools ADB toolchain with secure pairing support. Inspect its path and version; do not silently switch copies or restart a shared server. The selected host must already appear in the phone's **Paired devices**. USB trust alone is not wireless pairing trust.
4. If pairing is missing, follow [human-operated secure pairing](setup-linux-wireless.md#discover-and-authorize) first. The human handles the temporary pairing code locally, outside agent capture; no codes in chat, command arguments, screenshots or logs. A pairing port is never the connection port.
5. Confirm the exact physical phone. Privately record a stable hardware identifier from its previously authorized selected transport, or obtain a human-verified equivalent. The examples use `getprop ro.serialno`; an absent identifier is a stop condition, not permission to match only the model. Keep all identifiers and endpoints private.

No legacy `adb tcpip 5555`, root, public ADB, router port forwarding, broad network scanning, unattended unlock, or policy bypass. Tailscale access is not approval for phone input or external actions.

## Current endpoint

Read the **current connection port** from the main Wireless debugging **IP address & Port** row, not the pairing dialog. Keep that port exactly, but use the human-confirmed literal Tailscale peer IPv4 address instead of the LAN address. Set `TAILNET_ENDPOINT` (Bash) or `$TailnetEndpoint` (PowerShell) locally to that peer address and port. Do not guess a fixed port or reuse an old one. This recipe deliberately accepts only canonical IPv4 addresses in Tailscale's `100.64.0.0/10` range and decimal ports 1–65535, not hostnames, IPv6, wildcards or leading-zero forms. The syntax check does **not** prove ownership or reachability.

Tailscale does not bridge Android's local mDNS discovery here. An empty `adb mdns services` result is not a reason to use a LAN or USB fallback. Connect explicitly to the verified peer address and current TLS port.

**Bash — Linux/macOS, pure endpoint guard:** run this in the same shell before the connection block. It performs no network or phone operation.

<!-- endpoint-guard-bash -->
```bash
validate_tailnet_endpoint() {
  if [[ ! ${TAILNET_ENDPOINT:-} =~ ^100\.([1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2}):([1-9][0-9]{0,4})$ ]]; then
    printf '%s\n' 'Stop: require a canonical Tailscale IPv4:current-port endpoint' >&2
    return 1
  fi
  if (( BASH_REMATCH[1] < 64 || BASH_REMATCH[1] > 127 || BASH_REMATCH[2] > 255 || BASH_REMATCH[3] > 255 || BASH_REMATCH[4] > 65535 )); then
    printf '%s\n' 'Stop: endpoint address or port outside allowed range' >&2
    return 1
  fi
}
validate_tailnet_endpoint
```

**Native Windows — PowerShell, pure endpoint guard:** use native ADB, not WSL. This block is documented/static-reviewed; the Linux lane does not execute or parse PowerShell.

<!-- endpoint-guard-powershell -->
```powershell
function Assert-TailnetEndpoint {
    if ($TailnetEndpoint -cnotmatch '\A100\.([1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2}):([1-9][0-9]{0,4})\z') {
        throw 'Require a canonical Tailscale IPv4:current-port endpoint'
    }
    if ([int]$Matches[1] -lt 64 -or [int]$Matches[1] -gt 127 -or
        [int]$Matches[2] -gt 255 -or [int]$Matches[3] -gt 255 -or [int]$Matches[4] -gt 65535) {
        throw 'Endpoint address or port outside allowed range'
    }
}
Assert-TailnetEndpoint
```

## Bind and read back

Obtain task/capture consent first. Set `EXPECTED_HARDWARE_ID` or `$ExpectedHardwareId` privately to the exact previously verified hardware value, never an example or model name. Run the matching guarded connection block. **No silent USB or LAN fallback:** every shell, hierarchy, screenshot and input operation for this route uses the exact Tailscale endpoint, even if USB is attached.

**Bash — Linux/macOS:**

```bash
(
  set -eu
  validate_tailnet_endpoint
  : "${EXPECTED_HARDWARE_ID:?Set the exact privately verified hardware identity}"
  adb connect "$TAILNET_ENDPOINT"
  STATE=$(adb -s "$TAILNET_ENDPOINT" get-state)
  [ "$STATE" = device ] || { printf '%s\n' 'Stop: selected endpoint is not device' >&2; exit 1; }
  ACTUAL_ID=$(adb -s "$TAILNET_ENDPOINT" shell getprop ro.serialno)
  ACTUAL_ID=${ACTUAL_ID%$'\r'}
  [ -n "$ACTUAL_ID" ] && [ "$ACTUAL_ID" = "$EXPECTED_HARDWARE_ID" ] || { printf '%s\n' 'Stop: hardware identity mismatch or unavailable' >&2; exit 1; }
  SHELL_ID=$(adb -s "$TAILNET_ENDPOINT" shell id)
  case "$SHELL_ID" in
    uid=2000\(shell\)*) ;;
    *) printf '%s\n' 'Stop: unexpected shell identity' >&2; exit 1 ;;
  esac
  adb -s "$TAILNET_ENDPOINT" exec-out uiautomator dump /dev/tty
)
```

**Native Windows — PowerShell:**

```powershell
Assert-TailnetEndpoint
if ([string]::IsNullOrWhiteSpace($ExpectedHardwareId)) { throw 'Set the exact privately verified hardware identity' }
adb connect "$TailnetEndpoint"
if ($LASTEXITCODE -ne 0) { throw 'Connection failed; stop' }
$State = adb -s "$TailnetEndpoint" get-state
if ($LASTEXITCODE -ne 0 -or "$State".Trim() -cne 'device') { throw 'Selected endpoint is not device' }
$ActualId = adb -s "$TailnetEndpoint" shell getprop ro.serialno
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ActualId) -or "$ActualId".TrimEnd([char[]]"`r`n") -cne $ExpectedHardwareId) { throw 'Hardware identity mismatch or unavailable' }
$ShellId = adb -s "$TailnetEndpoint" shell id
if ($LASTEXITCODE -ne 0 -or "$ShellId" -cnotmatch '^uid=2000\(shell\)') { throw 'Unexpected shell identity' }
adb -s "$TailnetEndpoint" exec-out uiautomator dump /dev/tty
if ($LASTEXITCODE -ne 0) { throw 'Hierarchy capture failed' }
```

The dump may contain status text; extract and inspect the current hierarchy as described in [navigation and text](navigation-and-text.md). Require the intended unlocked app/account and current target. With capture consent, capture a screenshot using `adb -s "$TAILNET_ENDPOINT" exec-out screencap -p` (PowerShell selector: `$TailnetEndpoint`). Store it outside the public tree and **decode/view it**, not just check exit status. On native Windows use a binary-safe subprocess/file API; older PowerShell native-output redirection can corrupt PNG bytes. See [host platforms](android-host-platforms.md) for host evidence limits.

Choose one approved reversible action from fresh hierarchy/image geometry. For example, if Back is appropriate to the current screen, use `adb -s "$TAILNET_ENDPOINT" shell input keyevent KEYCODE_BACK` (PowerShell: `$TailnetEndpoint`), then immediately obtain fresh hierarchy and screenshot over the **same endpoint** and confirm the expected screen. Reidentify a row before an approved tap; read back the destination and any required restoration. Command exit, a saved PNG, or pairing success is not navigation proof.

If cable-free acceptance is requested, have the human remove USB, verify its entry is absent with `adb devices -l`, then repeat the selected-endpoint identity, fresh observation, benign input and readback. Do not label attached-cable endpoint targeting as physical cable-removal proof. Draft fidelity and visible changing scrcpy frames require their own tests; do not import USB/LAN results. For subsequent reference examples set `SERIAL`/`$Serial` to this exact verified endpoint and keep every operation explicitly selected.

## Reconnect and revoke

- Wireless debugging re-enablement, reboot or network changes can change the TLS connection port. Read the current main-page port again, confirm the same tailnet peer, rerun the guards and exact hardware/transport checks, and establish fresh UI evidence before input. Pairing can persist; do not re-pair unnecessarily or use stale coordinates.
- On failure, stop after one approved targeted correction and fresh readback. Do not substitute USB/LAN, restart shared services, change routes/firewalls, enable legacy TCP, or infer internet/cellular compatibility.
- With approval, rerun the endpoint guard and use `adb disconnect "$TAILNET_ENDPOINT"` or `adb disconnect "$TailnetEndpoint"`. Re-list devices and verify that exact transport is absent. This ends the host connection, not pairing trust or listener availability.
- Offer human-controlled forgetting of the selected paired host or disabling Wireless debugging. Tailscale disconnect and USB unplugging do not revoke Android pairing. Do not remove host keys or revoke unrelated peers.

## Verified scope

On one Pixel running Android 16 and a Linux host, SDK ADB reached the current paired TLS connection port through the phone's literal Tailscale address. The explicitly selected endpoint returned `device`, a non-root shell and hardware identity matching the authorized USB baseline. Fresh hierarchy and a decoded screenshot supported reversible Settings navigation and restoration with readback over that endpoint. USB supplied the initial identity baseline. A separate physical cable-removal check then confirmed no phone USB device was attached; the selected Tailscale endpoint again provided fresh screenshots, Back navigation, a reidentified row tap and restoration with Wireless debugging still enabled.

Both phones were on home Wi-Fi during this acceptance. No off-LAN or cellular-only operation is claimed. macOS/native Windows routes are upstream-documented and static-reviewed, not runtime-tested here. Endpoint-guard and package tests are offline evidence, not phone/network certification. This route adds neither universal away-from-home access nor a guarantee of automatic reconnection.

## Primary sources

- [Android ADB Wireless debugging](https://developer.android.com/tools/adb#wireless): secure pairing, Wi-Fi prerequisites, distinct pairing/connection endpoints and mDNS troubleshooting.
- [ADB command reference](https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/master/docs/user/adb.1.md): explicit `connect`, `disconnect` and selected-device operations.
- [Tailscale IP addresses](https://tailscale.com/kb/1015/100.x-addresses): tailnet IPv4 address range; an address alone is not phone identity.
- [Tailscale access controls](https://tailscale.com/kb/1018/acls) and [incoming-connection controls](https://tailscale.com/kb/1072/client-preferences): authorized reachability remains subject to policy and client settings.

Project device observations above are the local acceptance record, not a general statement that Android/Tailscale upstream certifies this combination on every device.
