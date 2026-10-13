# Contributing

Keep this project a portable, documentation-led Agent Skill for authorized USB control on Linux. Read [SKILL.md](SKILL.md) and [safety and verification](references/safety-and-verification.md) before proposing changes.

## Propose a focused change

Use [issues](https://github.com/tylerdotai/android-phone-control/issues) for a reproducible limitation, correction, or proposed capability. Describe the expected result, actual result, relevant Android/tool versions, and host architecture. Distinguish observations from suspected causes. Report a command's exit status separately from proof that the intended UI changed.

Do not put live serials, personal paths/hostnames, account names, screenshots of private content, trust keys, tokens, passwords, or verification codes in issues, commits, or pull requests. Keep raw device evidence outside this repository. Inspect both file names and contents before sharing sanitized findings; a generic filename is not redaction. Do not submit real secrets as validation fixtures.

## Preserve the boundaries

- Keep device operations explicitly bound to the human-selected serial.
- Preserve human unlock and RSA trust; never add lock bypass, root, network ADB, private-data extraction, or persistent control software.
- Keep permission to navigate, draft, replace text, and submit separate. External actions need exact target/payload approval and destination readback.
- Stop when observation, exact text readback, app/account identity, or submission state is uncertain. Never claim a working stream from startup logs alone.
- Keep `templates/session-policy.yaml` descriptive with `enforced: false`. It is not runtime configuration or a sandbox.
- Preserve the eight-file skill payload and relative links; do not add dependencies implicitly or include repository tooling in installed skills.

## Verify the change

From the repository root, with existing Python 3, Bash, and Ruby/YAML/Psych available:

```bash
python3 tools/validate.py
python3 tools/verify_e2e.py --output .artifacts/e2e.json
```

These commands validate documentation/package behavior, not physical-phone capabilities. Include executed commands, results, and a sanitized summary of the repeatable JSON artifact in the pull request. Do not describe skipped checks as passing. For changed command or device guidance, identify what was tested live and what remains untested; device testing always requires separate human consent and a benign task.

For validation-tool behavior changes, enumerate failure modes and define the expected CLI/E2E contract **before implementation**. Demonstrate that the contract fails for the expected reason, then make it pass. Prefer E2E checks at the real boundary with a regenerable artifact. Do not add after-the-fact unit tests to justify an implementation.

Check rendered Markdown, local links, image alt text, and narrow-screen readability when changing presentation. Use original diagrams or consented, sanitized evidence; label illustrations as illustrations rather than device screenshots. Cite maintained primary documentation for compatibility or installation claims.

## Submit a pull request

1. Fork the repository and create a focused branch.
2. Make the change and run the checks above.
3. Review the diff for private information, unsupported claims, and unrelated edits.
4. Commit and push to your fork, then open a pull request.
5. State the problem, changed behavior, evidence, and limitations. Do not publish raw phone logs or captures as artifacts.

Documentation corrections are welcome without new device testing when they make no new device-capability claim. Proposed OEM, Android-version, Unicode, or IME support needs evidence; one successful device does not establish general compatibility.

Contributions to this repository are provided under its [MIT License](LICENSE). Preserve source credits and respect the separate licenses of referenced tools and resources.
