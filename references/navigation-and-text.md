# Navigation and verified text

All examples assume a locally set, explicitly selected `SERIAL`, approved task scope, an unlocked phone, and no secrets on the observed screen. Use the agent's terminal/file/vision tools; no particular desktop-control integration is required.

## Observe → identify → act → read back

1. Obtain narrowly scoped text/hierarchy and current foreground context. UI Automator is commonly available but can fail on custom-rendered apps, restricted screens, or non-idle UI:
   ```bash
   : "${SERIAL:?Select the intended phone first}"
   adb -s "$SERIAL" exec-out uiautomator dump /dev/tty
   adb -s "$SERIAL" shell wm size
   ```
   The dump can contain status text around XML. Extract the `<hierarchy>…</hierarchy>` document before XML parsing; do not treat the whole output as pure XML. `/dev/tty` output is device-dependent. If unavailable, report it or use an approved unique temporary device file and remove only that artifact afterwards. A hierarchy is a broad capture: avoid dumping secret-bearing screens and retain only task-relevant fields locally.
2. Inspect visible text, resource ID, bounds, package, enabled/focused state, and clickable ancestors. Do not trust text alone: bind a comment/reply button to its current adjacent post/conversation and account. A non-clickable child may label a clickable parent; a nearby sibling can be a different external action.
3. If text is incomplete, use a fresh screenshot. Create a private, unique local destination with an existing writable `TMPDIR`:
   ```bash
   CAPTURE=$(mktemp "${TMPDIR:?Set a private writable TMPDIR}/android-screen.XXXXXX") || { printf '%s\n' 'Stop: private capture destination creation failed' >&2; exit 1; }
   adb -s "$SERIAL" exec-out screencap -p > "$CAPTURE"
   ```
   The template ends in `XXXXXX` for Linux/macOS portability; the file contains PNG data even without a `.png` extension. Open it with the agent's image tool and verify actual decoded content. Do not call a black image proof of locking; secure windows may block captures. `wm size` alone is not screenshot dimensions or rotation proof.
4. Before navigation, note the current app/component and task surface for any agreed restoration. A launch intent succeeding (even `am start -W`) does not prove the new window is focused: transitions can produce stale or null focus. Poll fresh non-sensitive focus/UI observations with a bounded deadline until the expected package and surface appear; stop if they do not. A single Back can expose an older task-stack screen rather than restore the original app. Verify restoration from current UI, not a keypress result.
5. Derive coordinates from the **current** hierarchy/screenshot, not a saved recipe. Set `X` and `Y` to the confirmed target's center on the device display:
   ```bash
   : "${X:?Set X from fresh target bounds}" "${Y:?Set Y from fresh target bounds}"
   adb -s "$SERIAL" shell input tap "$X" "$Y"
   ```
   Only run for an approved benign navigation target. Observe again and verify the expected screen/element. Scroll once if needed; refresh all target evidence after movement. Do not chain blind taps.

## Draft entry

Before typing, confirm the intended editable field is focused and inspect its current contents. Do not erase or overwrite an existing unsent draft without explicit permission. Do not use Enter to dismiss a keyboard: it may send, search, or submit. Draft-only acceptance is **exact text in the correct field, no submission**.

ADB has two quoting boundaries: the host shell and Android's shell. Passing a host-quoted argument can still leave remote metacharacters unprotected. `input text` commonly represents spaces as `%s`; it is not a general Unicode input API. Shell quoting does not prevent IME autocorrect or dropped input.

For an empty, confirmed field, this deliberately small ASCII example uses Python's standard library (discover `python3` first), explicitly remote-quotes each character, substitutes a space, and waits between characters. It creates no helper script or dependency. Do not run it unless this sample text itself is permitted; never append it blindly to an existing draft.

```bash
: "${SERIAL:?Select the intended phone first}"
export SERIAL
python3 -c '
import os, shlex, subprocess, time
serial = os.environ["SERIAL"]
text = "Hello, world!"
assert text.isascii() and all(32 <= ord(c) < 127 for c in text)
assert "%" not in text, "Percent handling needs a separate device test"
for char in text:
    remote = "input text " + shlex.quote("%s" if char == " " else char)
    subprocess.run(["adb", "-s", serial, "shell", remote], check=True, timeout=10)
    time.sleep(0.15)
'
```

The delay is a starting point, not a reliability guarantee. For a real draft in an empty confirmed field, use a short supported prefix of the **approved final text** as the check: enter the prefix, verify it exactly, and append **only the remaining suffix**. Do not enter the complete draft again on top of the prefix. The standalone `Hello, world!` example above belongs only in an agreed benign test field; before reusing that field for a real draft, obtain explicit clearing authorization and verify it is empty. Never silently clear sample text or an older user draft. Compare the final field with the complete approved text, including punctuation, spaces, line breaks and final length. Do not normalize a mismatch away. If the field value is hidden/truncated and no complete readback exists, stop with **unverified**, not success.

If entry drops characters, stop appending. Confirm focus/context, identify IME changes, and obtain permission before replacement. Inspect the selected device's help:

```bash
adb -s "$SERIAL" shell input
```

Some versions advertise `keycombination`. Only when advertised **and** a benign field test proves Ctrl+A selects this field's complete text, an approved replacement may use:

```bash
adb -s "$SERIAL" shell input keycombination 113 29
adb -s "$SERIAL" shell input keyevent 67
```

These mean Ctrl-left + A, then Delete; apps/IME can interpret them differently. Verify the field became empty before retyping slowly. If unsupported, use a verified visible selection control or ask the human to clear the approved field. Never loop Delete over unknown content.

For Unicode, literal percent sequences, multiline text, or unsupported key mappings, test the exact capability in a benign field first. scrcpy keyboard modes/paste have different limitations; do not install an IME, change keyboards, or write/read clipboards implicitly. Prefer human entry when exact safe input cannot be established. Do not inject passwords, card data or verification codes through these examples.

## Mirroring/input caveats and sources

- [scrcpy control](https://github.com/Genymobile/scrcpy/blob/master/doc/control.md): `--no-control`, clipboard synchronization, paste limitations. Clipboard pasting can expose contents to Android apps; avoid sensitive content and disable autosync where supported.
- [scrcpy keyboard](https://github.com/Genymobile/scrcpy/blob/master/doc/keyboard.md): keyboard modes and character restrictions.
- [Android ADB](https://developer.android.com/tools/adb): shell command invocation and `-s` selection.
- The selected device's `input` usage is the authority for optional syntax. No Android version or vendor is assumed to support every command here.
