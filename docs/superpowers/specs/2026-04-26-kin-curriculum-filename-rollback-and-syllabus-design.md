# KIN Curriculum Filename Rollback And Syllabus Design

## Purpose

Revert the curriculum filename convention back to simple week-plus-document-type names and move cycle/theme visibility into file content plus per-program syllabus files.

## Weekly Filename Pattern

Use:

- `week-xx-curriculum.md`
- `week-xx-coach-guide.md`
- `week-xx-quick-outline.md`
- `week-xx-fully-scripted-session.md`

Rules:

- `week-xx` remains zero-padded to two digits.
- The filename contains only week number and document type.
- The same pattern is used for tots, youth, and adult.

## Weekly File Header Requirements

Every generated weekly file should include a short metadata block near the top.

### Youth And Adult

Include:

- week
- cycle
- theme
- teaching goal
- class length

### Tots

Include:

- week
- cycle
- theme
- movement theme
- class length

## Program Syllabus Files

Each program directory should contain:

- `generated/curriculum/tots/program-syllabus.md`
- `generated/curriculum/youth/program-syllabus.md`
- `generated/curriculum/adult/program-syllabus.md`

## Program Syllabus Contents

Each syllabus file should include:

- a short program introduction
- a week-by-week map

Each week entry should contain:

- week number
- cycle
- theme
- short description
- main goal

## Generation Rules

- Keep the output generator as the single source of file creation.
- Do not manually rename generated files.
- Generate syllabus files from the same KB week data as the weekly lesson files.
- Keep tots `cycle` values in the KB even though cycle no longer appears in filenames.

## Rationale

- Simple filenames are easier to browse once the folder is already scoped to a program.
- Cycle and theme remain visible immediately after opening the file.
- Program syllabus files provide the higher-level map that the longer filenames were trying to encode.
- The generator remains reproducible and the KB remains the single source of truth.

## Implementation Notes

- Remove the bracketed filename builder logic from the generator.
- Add one syllabus render path per program.
- Update generator tests to assert the simple filenames plus the new syllabus files.
- Regenerate all curriculum outputs after the generator changes.
