#!/usr/bin/env python3
"""Test-first CLI contract: real repository plus bounded filesystem mutants.

Known failures are named in CASES below before validator implementation. No
phone, ADB, network, mocks, or imported validator internals are used. Only the
pure Bash endpoint guard is executed separately; all device snippets stay inert. Captures
include each CLI exit status and JSON result. A missing/incomplete parent README
is a baseline failure, never silently replaced with a passing synthetic repo.
"""
import argparse
import binascii
import struct
import zlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

CASES = [
    ("local-environment-ignored", "allowed", "write", ".venv/LOCAL_ONLY.json", '{"private_path":"/home/' + 'private-person/local-environment"}\n'),
    ("missing-skill", "required", "remove", "SKILL.md", ""),
    ("missing-reference", "required", "remove", "references/setup-linux-usb.md", ""),
    ("missing-wireless-reference", "required", "remove", "references/setup-linux-wireless.md", ""),
    ("missing-host-platform-reference", "required", "remove", "references/android-host-platforms.md", ""),
    ("missing-tailscale-reference", "required", "remove", "references/setup-tailscale-wireless.md", ""),
    ("incomplete-tailscale-contract", "tailscale", "write", "references/setup-tailscale-wireless.md", "# Tailscale\nUse adb connect.\n"),
    ("live-wireless-policy-endpoint", "policy", "write", "templates/session-policy.yaml", 'enforced: false\nsession:\n  wireless_connection_endpoint: "INERT-ENDPOINT"\n'),
    ("live-tailnet-policy-identity", "policy", "write", "templates/session-policy.yaml", 'enforced: false\nsession:\n  tailnet_peer_ip: "INERT-PEER"\n  expected_hardware_identity: "INERT-IDENTITY"\n'),
    ("complete-skill-bundle", "allowed", "bundle", "assets/e2e.zip", ""),
    ("bundle-without-tailscale", "archive", "bundle", "assets/e2e.zip", "references/setup-tailscale-wireless.md"),
    ("malformed-yaml", "yaml", "write", "templates/session-policy.yaml", "broken: [\n"),
    ("bad-name", "skill", "replace", "SKILL.md", "name: android-phone-control|name: Bad_Name"),
    ("long-description", "skill", "replace", "SKILL.md", 'description: "Use when controlling Android over USB or paired Wi-Fi."|description: "' + "x" * 61 + '"'),
    ("numeric-metadata", "skill", "replace", "SKILL.md", 'version: "1.3.0"|version: 1'),
    ("enforced-policy", "policy", "replace", "templates/session-policy.yaml", "enforced: false|enforced: true"),
    ("missing-image", "link", "append", "README.md", "\n![Missing](assets/not-present.png)\n"),
    ("missing-local-link", "link", "append", "README.md", "\n[Missing](references/not-present.md)\n"),
    ("missing-anchor", "anchor", "append", "README.md", "\n[Missing](SKILL.md#not-present-anchor)\n"),
    ("undefined-reference", "reference", "append", "README.md", "\n[Missing][undefined-e2e-ref]\n"),
    ("bad-bash", "bash", "append", "README.md", "\n```bash\nif then\n```\n"),
    ("bad-python", "python", "append", "README.md", "\n```python\ndef broken(\n```\n"),
    ("unclosed-fence", "fence", "append", "README.md", "\n```bash\ntrue\n"),
    ("bad-svg", "svg", "write", "assets/e2e.svg", "<svg>"),
    ("script-svg", "svg", "write", "assets/e2e.svg", '<svg xmlns="http://www.w3.org/2000/svg"><title>Test</title><script/></svg>'),
    ("external-svg", "svg", "write", "assets/e2e.svg", '<svg xmlns="http://www.w3.org/2000/svg"><title>Test</title><image href="https://example.com/image.png"/></svg>'),
    ("bad-png", "png", "write", "assets/e2e.png", "not a PNG"),
    ("private-png-metadata", "privacy", "png", "assets/e2e.png", "/home/" + "private-person/evidence"),
    ("external-svg-paint", "svg", "write", "assets/e2e.svg", '<svg xmlns="http://www.w3.org/2000/svg"><title>Test</title><rect fill="url(https://example.com/paint.svg#x)"/></svg>'),
    ("private-path", "privacy", "append", "README.md", "\n/home/" + "private-person/phone-evidence\n"),
    ("live-serial", "privacy", "append", "README.md", '\nSERIAL="' + "E2E_INERT_SERIAL_123" + '"\n'),
    ("credential-shaped", "privacy", "append", "README.md", "\n" + "gh" + "p_" + "INERT" * 8 + "\n"),
    ("private-file", "tree", "write", ".env", "INERT=1\n"),
    ("symlink", "tree", "symlink", "assets/e2e-link", "SKILL.md"),
    ("private-zip", "archive", "zip", "assets/e2e.zip", ".env"),
    ("traversal-zip", "archive", "zip", "assets/e2e.zip", "../escape.txt"),
    ("malformed-workflow", "yaml", "write", ".github/workflows/validate.yml", "jobs: [\n"),
    ("stale-repo-url", "public-url", "append", "README.md", "\nhttps://github.com/tylerdotai/android-phone-" + "skill\n"),
    ("missing-readme-sections", "readme", "write", "README.md", "# Incomplete\n"),
]


def invoke(validator: Path, root: Path) -> dict:
    run = subprocess.run([sys.executable, str(validator), str(root)], capture_output=True, text=True, timeout=90)
    try:
        report = json.loads(run.stdout)
    except json.JSONDecodeError:
        report = None
    return {"exit_code": run.returncode, "report": report,
            "stderr": run.stderr[:2000], "non_json_stdout": run.stdout[:2000] if report is None else ""}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=".artifacts/e2e.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    validator = root / "tools/validate.py"
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    results = []
    if not validator.is_file():
        results.append({"name": "validator-entrypoint", "passed": False, "reason": "missing-validator", **invoke(validator, root)})
    else:
        baseline = invoke(validator, root)
        results.append({"name": "actual-repository", "passed": baseline["exit_code"] == 0 and isinstance(baseline["report"], dict) and baseline["report"].get("ok") is True, **baseline})
        scratch = Path(os.environ.get("TMPDIR", str(root / ".artifacts/test-runs")))
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="android-docs-e2e-", dir=scratch) as directory:
            for name, code, action, relative, value in CASES:
                tree = Path(directory) / name
                shutil.copytree(root, tree, symlinks=True, ignore=shutil.ignore_patterns(".git", ".artifacts", ".venv", "__pycache__"))
                target = tree / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                if action == "remove":
                    target.unlink(missing_ok=True)
                elif action == "replace":
                    old, new = value.split("|", 1)
                    text = target.read_text()
                    if old not in text:
                        raise RuntimeError(f"Mutation precondition absent: {name}")
                    target.write_text(text.replace(old, new, 1))
                elif action == "append":
                    with target.open("a") as stream:
                        stream.write(value)
                elif action == "write":
                    target.write_text(value)
                elif action == "png":
                    # Inert 1x1 fixture, not a product/device screenshot.
                    def chunk(kind: bytes, body: bytes) -> bytes:
                        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", binascii.crc32(kind + body) & 0xffffffff)
                    target.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)) + chunk(b"tEXt", b"Comment\x00" + value.encode()) + chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00\x00")) + chunk(b"IEND", b""))
                elif action == "symlink":
                    target.symlink_to(tree / value)
                elif action == "bundle":
                    # Independent public payload contract, not validator imports.
                    payload = ["SKILL.md", "LICENSE", "templates/session-policy.yaml"] + [
                        "references/" + part + ".md" for part in (
                            "setup-linux-usb", "setup-linux-wireless", "setup-tailscale-wireless",
                            "android-host-platforms", "navigation-and-text", "safety-and-verification",
                            "troubleshooting", "installation-and-sharing")]
                    with zipfile.ZipFile(target, "w") as archive:
                        for member in payload:
                            if member != value and (tree / member).is_file():
                                archive.write(tree / member, "android-phone-control/" + member)
                elif action == "zip":
                    with zipfile.ZipFile(target, "w") as archive:
                        archive.writestr(value, "INERT")
                result = invoke(validator, tree)
                report = result["report"]
                codes = {item.get("code") for item in report.get("errors", [])} if isinstance(report, dict) else set()
                passed = (result["exit_code"] == 0 and isinstance(report, dict) and report.get("ok") is True) if code == "allowed" else (result["exit_code"] == 1 and code in codes)
                results.append({"name": name, "expected_code": code, "passed": passed, **result})
    # Run only the pure guard fence, never connection or device snippets.
    reference = root / "references/setup-tailscale-wireless.md"
    guard = re.search(r"<!-- endpoint-guard-bash -->\s*```bash\n(.*?)\n```", reference.read_text() if reference.is_file() else "", re.S)
    guard_cases = [
        ("valid-tailnet", "100.64.0.1:1", True),
        ("valid-upper-bound", "100.127.255.255:65535", True),
        ("missing", "", False), ("lan-address", "192.168.1.1:12345", False),
        ("outside-tailnet", "100.128.0.1:12345", False),
        ("invalid-octet", "100.64.256.1:12345", False),
        ("zero-port", "100.64.0.1:0", False),
        ("oversized-port", "100.64.0.1:65536", False),
        ("leading-zero-octet", "100.064.0.1:12345", False),
        ("leading-zero-port", "100.64.0.1:01234", False),
        ("dns-name", "phone.example:12345", False),
        ("wildcard", "100.64.*.1:12345", False),
        ("option", "--help", False),
        ("whitespace", "100.64.0.1:12345 ", False),
        ("shell-metacharacters", "100.64.0.1:12345; true", False),
    ]
    for name, endpoint, allowed in guard_cases:
        if guard:
            code = guard.group(1)
            # Refuse runtime-tool calls in the isolated pure guard fence.
            safe = not re.search(r"\b(?:adb|scrcpy|curl|wget|ssh|eval|source)\b|`|\$\(", code)
            if not safe:
                results.append({"name": "endpoint-guard-" + name, "passed": False, "reason": "guard-not-pure"})
                continue
            run = subprocess.run(["bash", "--noprofile", "--norc", "-c", code],
                                 env={"PATH": "/usr/bin:/bin", "TAILNET_ENDPOINT": endpoint},
                                 capture_output=True, text=True, timeout=10)
            results.append({"name": "endpoint-guard-" + name, "passed": (run.returncode == 0) == allowed,
                            "exit_code": run.returncode, "expected_allowed": allowed})
        else:
            results.append({"name": "endpoint-guard-" + name, "passed": False, "reason": "missing-pure-guard"})
    receipt = {"scope": "Documentation/package validation and pure Bash endpoint guard; no device access verified", "cases": results, "passed": sum(item["passed"] for item in results), "total": len(results), "ok": all(item["passed"] for item in results)}
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"ok": receipt["ok"], "passed": receipt["passed"], "total": receipt["total"], "artifact": str(output)}))
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
