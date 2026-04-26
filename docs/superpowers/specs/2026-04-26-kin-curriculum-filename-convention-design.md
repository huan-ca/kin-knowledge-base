# KIN Curriculum Filename Convention Design

## Purpose

Define a human-browsable filename convention for generated curriculum files under `generated/curriculum/`.

## Naming Pattern

Use:

`week-xx_[cycle]_[theme-slug]_[file-type].md`

## Rules

- `week-xx` is always zero-padded to two digits and remains unbracketed.
- `cycle` is bracketed, lowercase, and treated as a short categorical label.
- `theme-slug` is bracketed, lowercase, and hyphenated internally.
- `file-type` is bracketed and chosen from a fixed vocabulary.
- Underscores separate fields.
- Hyphens separate words inside a field value.
- No spaces.

## File-Type Vocabulary

- `curriculum`
- `quick-outline`
- `coach-guide`
- `scripted-session`

## Examples

- `week-01_[defensive]_[early-escape-frames]_[curriculum].md`
- `week-01_[defensive]_[early-escape-frames]_[coach-guide].md`
- `week-01_[defensive]_[early-escape-frames]_[scripted-session].md`
- `week-01_[defensive]_[early-escape-frames]_[quick-outline].md`
- `week-24_[self-defense]_[ground-self-defense-pins-escapes-and-technical-stand-up]_[scripted-session].md`
- `week-06_[balance]_[balance-posture-and-push-pull-games]_[coach-guide].md`

## Source Of Filename Fields

### Youth And Adult

- `cycle` comes from the existing week `cycle` field in the KB week data.
- `theme-slug` comes from the week `theme`.

### Tots

- `cycle` should be stored explicitly in the KB week data rather than inferred only inside the generator.
- `theme-slug` comes from the week `theme`.

## Rationale

This convention optimizes for human browsing over path stability.

- Brackets make field boundaries visually obvious in file lists.
- Underscores separate major fields more clearly than using only hyphens.
- Keeping `week-xx` plain preserves natural sorting.
- Keeping `theme-slug` in the filename makes week purpose visible without opening the file.

## Tradeoffs

- Filenames will change if cycle labels or theme wording changes.
- Brackets are noisier for shell handling than simpler filenames.
- The generator, tests, and any direct references must be updated together when the convention changes.

## Implementation Notes

- The generator should own filename construction in one place.
- Tests should assert the new naming convention directly.
- The existing generated files should be regenerated rather than manually renamed.
- Tots week data should gain explicit cycle labels before regeneration so filenames stay deterministic.
