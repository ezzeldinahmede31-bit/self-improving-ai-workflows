---
name: professional-linux-programming
description: Applies Professional Linux Programming (Jon Hall, Marcelo Tosatti & Robert W. Weaver) to shipping real software on Linux: a tour of the platform as a professional developer sees it, including administration for programmers, C and GUI toolkits, scripting languages, web integration, and packaging for distribution. Covers the development environment, project structure, and the lifecycle from source tree to installed product. Use when the user says 'develop on Linux', 'package my tool', 'GUI application on Linux', 'set up a Linux dev environment', or 'ship a Linux program'.
---
# professional-linux-programming

Hall, Tosatti, and Weaver treat Linux as a complete professional development platform, from a developer's system administration duties to the GUI, scripting, and packaging layers.
Use this skill when building software that must be developed, built, and delivered on Linux properly.
It spans the full lifecycle from source tree to an installed, working product.

## Core principles
- A Linux developer must also administer the platform; toolchains, libraries, and package management shape the workflow.
- The development environment, including compilers, linkers, make, and version control, is part of the product.
- GUI and scripting layers let one solution serve interactive and automated consumers.
- Web integration and network services connect desktop tools to the wider system.
- Packaging and distribution turn a source tree into software other people can install.
- A professional build is reproducible and clean from a fresh checkout.

## Key patterns
- Setting up a reproducible toolchain and build environment.
- Structuring projects so make and package managers can drive them.
- Choosing the right layer, compiled or scripting, for each component.
- Integrating web and service interfaces with local tools.
- Building distribution packages that install and uninstall cleanly.
- Verifying a clean build before any release is declared.

## Applying this to scripting/automation/code
- Structure automation projects as installable packages with dependencies declared.
- Use the platform toolchain to lint, test, and build before delivery.
- Expose internal tools through small web or CLI interfaces for reuse.
- Version and document every script as professional software, not scratch work.
- Reuse system packaging so deployments are repeatable across hosts.
- Make every deliverable reproducible from a fresh environment.

## Hard rules
- Never ship an unbuildable tree; verify a clean build first.
- Never mix system package state with project-local dependencies silently.
- Never release without uninstall and upgrade paths.
- Never assume another host has the same development packages.
- Never commit build artifacts that only your environment produces.
- Never ship a GUI or service that has not run in a clean environment once.

## Pairs with
pragmatic-programmer, infrastructure-as-code, devops-automation, n8n-code-nodes-official, code-linter-python-js
