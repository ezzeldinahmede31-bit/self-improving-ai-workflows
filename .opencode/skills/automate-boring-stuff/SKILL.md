---
name: automate-boring-stuff
description: Applies Al Sweigart's Automate the Boring Stuff with Python to eliminate repetitive computer work: batch file operations, spreadsheet and CSV processing, PDF handling, web data collection, GUI automation, and scheduled jobs that run on their own. Covers the practical toolkit (pathlib, csv, openpyxl, PyPDF2, requests, BeautifulSoup, pyautogui) and the discipline of turning a repeated manual chore into a safe, rerunnable script. Use when the user says 'automate this boring task', 'rename and organize my files', 'process this spreadsheet', 'scrape data from a page', or 'run this job on a schedule'.
---

# automate-boring-stuff

Most productivity is not clever algorithms; it is a person clicking the same buttons daily. This skill encodes the book's core move: recognize a chore that repeats, break it into steps a computer can do, and wrap those steps in a script that runs safely and on schedule.

## Core principles

- If you have done the same chore twice, it is a candidate for automation.
- Prefer batch operations on files and data over clicking through a UI.
- String handling and path handling are the backbone of boring-task scripts.
- A scheduled script must be safe to run unattended.
- Test every automation on a copy of the real data first.
- Keep credentials and personal data out of the script source.

## Key patterns

- Walk directories with pathlib and act on files by pattern.
- Read and write CSV and spreadsheet rows without reformatting by hand.
- Extract text from PDFs and documents for search and re-use.
- Collect web data with requests plus a parser, honoring the site's rules.
- Drive the desktop GUI only when no API exists.
- Schedule the finished script with cron or a task runner.

## Applying this to scripting/automation/code

- Turn a nightly file cleanup or report build into a scheduled n8n or cron job.
- Build Code nodes that batch-rename, re-encode, or reorganize incoming files.
- Convert messy exports into clean, consistent rows automatically.
- Fetch and store web data on a timer instead of by hand.
- Replace a manual cut-and-paste pipeline with one transform script.

## Hard rules

- Never automate a destructive step without a dry-run mode.
- Back up before any batch operation that moves or renames files.
- Respect the site's terms and robots rules when collecting data.
- Read secrets from environment variables, never from the script body.
- Test the script against a small copy before pointing it at production data.
- Make every automation idempotent so an extra run does no harm.

## Pairs with

code-linter-python-js, code-execution-guided-swemaster, security-and-hardening, practice-of-cloud-system-administration, evidence-over-memory
