---
name: readme-conventions
description: >
  Quality conventions for writing developer-focused README files.
  Covers required sections, structure, and quality criteria.
  Load the checklist reference for section-by-section requirements.
---

# README Conventions

## When to Use

Load this skill when generating or improving a README.md file for a code repository.

## Process

1. Read `references/checklist.md` for the full section-by-section quality checklist.
2. Follow the section order defined in the checklist.
3. Write from the perspective of a developer who just discovered this repo
   and wants to clone, install, and use it within 5 minutes.

## Rules

1. Start with the project name as an H1 heading, followed by a one-sentence description.
2. Every section from the checklist must be present. If a section does not apply, include it with a brief note explaining why.
3. Installation instructions must include exact commands (not placeholders).
4. Usage examples must show real code or CLI commands, not abstract descriptions.
5. Keep the total README under 500 lines. Put detailed API docs in separate files if needed.
6. Do not use badges unless the project already has CI/CD configured.
7. Do not include a table of contents for READMEs under 200 lines.
