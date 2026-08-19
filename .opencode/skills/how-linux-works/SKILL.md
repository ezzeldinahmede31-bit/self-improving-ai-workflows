---
name: how-linux-works
description: Applies How Linux Works (Brian Ward) to hands-on Linux administration and automation: a superuser's mental model of the boot process, kernel, devices, filesystems, networking, processes, and the shell, enough to find and fix real problems. Covers systemd units, the boot sequence, device handling, file permissions, processes and signals, and the core diagnostic toolchain. Use when the user says 'why does my system boot slowly', 'systemd unit', 'is that process normal', 'check my disk layout', or 'how do I debug this Linux box'.
---
# how-linux-works

Brian Ward gives the working superuser the structural map of Linux: what runs, in what order, and where to look when something breaks.
Use this skill for any administration, triage, or automation task that needs to understand the host it runs on.
It turns a Linux box from a black box into a readable stack.

## Core principles
- Linux is a stack: hardware, kernel, init, services, then your work; diagnose from the bottom up.
- The boot process has a fixed spine, and modern init (systemd) drives services with units and dependencies.
- Everything is a file: devices, process info, and kernel state all surface through the filesystem.
- Processes are owned and scoped by user, group, and limits; privileges shape what automation can do.
- Filesystems carry permissions, ownership, and attributes that silently change script behavior.
- Small, standard tools compose into powerful diagnosis when you know what each one reads.

## Key patterns
- Following the boot chain to find where startup stalls.
- Reading systemd unit files and journal output for service diagnosis.
- Using the process table and signal tools to manage running work.
- Tracing mounted filesystems and disk usage before acting on storage.
- Checking kernel messages for hardware and driver events.
- Inspecting limits and cgroups that scope what a service may consume.

## Applying this to scripting/automation/code
- Model long-running jobs as systemd services with proper restart and logging.
- Debug a failing cron or scheduler job by walking the process table and journal first.
- Set ownership and permissions explicitly in provisioning scripts.
- Probe device and disk state through /dev and /sys before risky operations.
- Trap signals in wrapper scripts so service restarts are clean.
- Read the exact unit, log, and limits before changing anything on a host.

## Hard rules
- Never kill a process without confirming its identity and parent.
- Never guess a unit name; read the unit file.
- Never change permissions without knowing the current owner and mode.
- Never reboot a production host to fix what a log line can reveal.
- Never treat a service as down until the journal and process table agree.
- Never edit system files without a backup and a revert plan.

## Pairs with
practice-of-cloud-system-administration, devops-automation, infrastructure-as-code, n8n-code-nodes-official, evidence-over-memory
