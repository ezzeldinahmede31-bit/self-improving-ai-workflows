---
name: linux-security-hardening
description: Applies Mastering Linux Security and Hardening (Donald A. Tevault) to securing Linux hosts and the automation that runs on them: a practical guide to account management, permissions, sudo, PAM, SSH hardening, firewalls, SELinux and AppArmor, and service lockdown. Covers audit and monitoring, kernel hardening, and patching discipline. Use when the user says 'harden this server', 'SSH lockdown', 'sudo policy', 'SELinux is blocking', or 'secure my Linux box'.
---
# linux-security-hardening

Tevault's book is a practical hardening playbook: exactly which settings, tools, and policies make a Linux host measurably harder to compromise.
Use this skill before deploying any service or automation to a real host.
It moves security from vague advice to a concrete, checkable configuration.

## Core principles
- Security is layered: accounts, permissions, network policy, and mandatory access control each raise the bar independently.
- Least privilege starts with accounts and sudo; grant exactly what a job needs.
- SSH is the main remote door; key-based auth, restricted config, and login throttling close it.
- Firewalls, from the nftables lineage to classic iptables, define the reachable surface.
- Mandatory access control via SELinux or AppArmor catches the mistakes discretionary permissions miss.
- Patching and auditing are ongoing disciplines, not one-time events.

## Key patterns
- Locked-down user accounts with strong password and lockout policies.
- Sudo rules scoped to commands and hosts, never blanket admin.
- SSH hardening: protocol limits, key-only auth, and disabled root login.
- A default-deny firewall with only needed ports open.
- Log and audit streaming so suspicious activity reaches a watch point.
- SELinux boolean and context checks for services that fail mysteriously.

## Applying this to scripting/automation/code
- Run automation under a dedicated least-privilege service account, never root.
- Restrict workflow webhook endpoints to known networks or tokens.
- Harden the host before n8n or agents are installed.
- Configure sudoers and PAM policies as code so they are reproducible.
- Check SELinux contexts and AppArmor profiles when a service mysteriously fails.
- Verify SSH key-only auth and disabled root login on every managed host.

## Hard rules
- Never disable SELinux or AppArmor to make a problem go away.
- Never expose SSH password auth when keys are an option.
- Never run services as root when a scoped account exists.
- Never ship a firewall change without confirming the management path stays open.
- Never deploy a host that has not been patched and audited.
- Never log secrets, keys, or tokens in audit streams.

## Pairs with
security-and-hardening, practice-of-cloud-system-administration, infrastructure-as-code, devops-automation, evidence-over-memory
