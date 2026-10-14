# Installation and sharing

This is a portable Agent Skill, not an Android app or executable agent service. It consists of `SKILL.md`, eight reference documents, a descriptive YAML template, and an MIT license. It requires no companion local skills, scripts or bundled binaries. Runtime tools are discovered when the workflow runs; installing the skill does not install ADB/scrcpy or authorize a phone.

## Install locally

1. Inspect every bundle file and archive entry first. Reject path traversal, absolute archive paths, unexpected scripts/binaries, secrets, raw captures or private evidence. Resolve existing skill-name conflicts before overwrite.
2. Select the intended Hermes profile. Copy the **whole** `android-phone-control/` directory into that profile's `skills/` directory, preserving relative reference/template paths. For the usual default profile this is `~/.hermes/skills/android-phone-control/`; an explicit `HERMES_HOME` or named profile can have a different location. Use approved file tools or Hermes `skill_manage` creation/supporting-file tools. Do not install into another profile implicitly.
3. Confirm `hermes skills list` includes the skill and load `/android-phone-control` in the intended session, or use `skill_view(name="android-phone-control")` when available. Verify that its content and referenced files match the inspected bundle. If discovery is stale, use a fresh session; follow installed Hermes documentation rather than inventing reload commands.
4. Treat `templates/session-policy.yaml` as a checklist only. It is **not** Hermes `config.yaml`, Android policy, or an executable permission mechanism; do not merge it into configuration.

A direct remote `SKILL.md` install may not include every supporting file. For this offline bundle preserve the complete tree; do not claim `hermes skills install archive.zip` is supported without checking the current CLI help. No hub publication or upload is required.

## Share a downloadable bundle

Package exactly the skill directory with the MIT license and no symlinks/private evidence. Check the archive entry manifest and CRC, then compute SHA-256 for the delivered archive. Deliver the local artifact as a chat attachment through the platform's supported file delivery; an attachment is not a registry publication. Do not publish, push, upload to a public host or create a repository without a separate request.

The public bundle must not contain live serials, account names, user-specific paths, device-specific screenshots/logs, trust keys, tokens, or unredacted test receipts. Keep private verification evidence outside this tree. Check both filenames and content before packaging; generic examples alone do not prove privacy.

## Metadata / compatibility

`SKILL.md` begins with YAML mapping frontmatter containing `name`, `description`, `license`, `compatibility` and simple string-valued `metadata`, including `metadata.version`. Its lowercase-hyphen name matches the folder. The compatibility field describes Linux, macOS, and native Windows host scope, distinguishing tested Linux device behavior from upstream-documented hosts, without relying on consumer-specific platform filters. Relative links support progressive disclosure. The template version describes the checklist format, not a runtime API. See the [Agent Skills specification](https://agentskills.io/specification) for portable format constraints.

Source: [Hermes skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/) for skill format, directories, profiles, discovery and agent-managed skill files. Other Agent Skill consumers may support different discovery/install commands; use their maintained documentation and retain the complete tree.
