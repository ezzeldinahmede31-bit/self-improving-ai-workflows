---
name: obsidian-second-brain-vault
description: "Routes downloaded media transcripts and extracted knowledge notes into a local Obsidian vault under the three-section structure (01_Raw_Inbox / 02_Structured_Knowledge / 03_Final_Outputs) so nothing is lost and every session's learning lands somewhere persistent. Trigger phrases: 'send to obsidian', 'vault path', 'save to second brain', 'write to my vault', 'obsidian'."
---

# OBSIDIAN SECOND-BRAIN VAULT

## DIRECTIVE
Close the loop between capture and durable knowledge: anything extracted by the
media/whisper pipeline, or by any research/analysis step, must land in an
Obsidian vault in ONE of three staging folders so the knowledge compounds
instead of being dropped into chat history that evaporates.

## ENVIRONMENT
- Read the vault root from `OBSIDIAN_VAULT_PATH` (set once in the shell).
- If unset, default to `$HOME/ObsidianVault`.
- Three sub-folders created on first use:
  `01_Raw_Inbox`, `02_Structured_Knowledge`, `03_Final_Outputs`.

## PIPELINE CONTRACT (used end-to-end)
1. `media-downloader-extractor` → `audio-whisper-transcriber` produces
   `/tmp/transcript_<reel>.txt`.
2. This skill copies that transcript into `01_Raw_Inbox/<timestamp>_<source>.md`
   UNCHANGED, prefixed with a YAML frontmatter block:
   ```
   ---
   source: media-downloader-extractor
   url: https://...
   media_id: <reel id>
   language: ar|en|mixed
   captured_at: 2026-08-13T...
   status: raw
   ---
   ```
3. A synthesis pass (summary + key points + timestamps) is written to
   `02_Structured_Knowledge/<slug>.md` with `status: structured`.
4. Final synthesized note for the user's actual use-case is dropped in
   `03_Final_Outputs/<slug>.md`.

## RULES
- NEVER write secrets, cookies, or credentials into the vault.
- Transcript files in `01_Raw_Inbox` are append-only raw capture; the
  synthesis step never clobbers them.
- Filenames are slugified + timestamped; never overwrite a file that already
  exists.
- Evidence: this skill prints the final vault path written, so the user can
  open it in Obsidian and SEE the file landed.

## Local adaptation
This project just ran `mkdir -p ~/ObsidianVault/01_Raw_Inbox 02_Structured_Knowledge
03_Final_Outputs` and exported `OBSIDIAN_VAULT_PATH='$HOME/ObsidianVault'`.
Pairing: `media-downloader-extractor` downloads the `.m4a` to `/tmp/`,
`audio-whisper-transcriber` writes `/tmp/transcript_reel.txt`, then this
skill moves a copy into `01_Raw_Inbox`. All file ops happen through the
workspace `bash`/`Read`/`Write` tools (never inline secrets in the path).