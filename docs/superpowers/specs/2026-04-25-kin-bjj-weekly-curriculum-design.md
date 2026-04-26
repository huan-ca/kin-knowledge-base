# KIN BJJ Weekly Curriculum And Lesson-Plan Generation Design

## Purpose

Define a reproducible KB-first workflow for generating weekly curriculum and lesson-plan artifacts for the KIN BJJ programs. The outputs should serve as internal coach documents, be grounded in repository source material plus approved client guidance, and preserve explicit provenance and confidence handling.

## Scope

This design covers:

- a 12-week tots program
- a 24-week youth program
- a 24-week adult program
- four generated files per week per program:
  - curriculum
  - quick outline
  - coach guide
  - fully scripted session

This design does not cover:

- parent-facing publishing
- student assessment or promotion checkpoints
- competition-prep documents outside the weekly curriculum
- life-skills theme expansion beyond placeholders already supported by source material

## Source And Authority Model

The build must follow the repository contract:

- `raw/` is immutable source evidence
- `kb/` is normalized knowledge
- `generated/` contains reproducible outputs
- `published/` is human-owned and must not be overwritten automatically

Authority order for this project:

1. Client-approved verbal guidance captured in this design
2. Existing raw source material in `raw/`
3. Existing KB pages derived from those sources

Where verbal guidance extends or overrides an underspecified KB area, the KB should be updated to reflect that guidance conservatively with the correct `claim_label` and confidence.

## Program Model

### Tots

- Audience: ages 4 to 7
- Duration: 12 weeks
- Class length: 30 minutes
- Primary objective: fun, movement quality, athletic development, and age-appropriate BJJ exposure
- Content model: separate from youth and adult

Tots weekly files should not use the standard technical class template. They should instead emphasize:

- movement theme
- game or engagement activity
- coordination or balance focus
- simple intro grappling habit or BJJ exposure

### Youth

- Audience: ages 8 to 13
- Duration: 24 weeks
- Class length: 60 minutes
- Belt range: white through green
- Primary objective: improved understanding of course material that transfers into sparring and competition
- Final two weeks: self-defense, standing and ground

Youth is the canonical technical sequence for the weekly curriculum design.

### Adult

- Audience: age 14 and up
- Duration: 24 weeks
- Class length: 60 minutes
- Belt range: white through black
- Primary objective: reuse the youth positional and topic framework while filtering for adult coaching needs
- Final two weeks: lower-body submission work with IBJJF awareness, but not restricted to IBJJF-only preparation

Adult should reuse the youth week-to-week structure where possible, but still be generated as separate files with adult-specific notes to reduce noise for coaches.

## Weekly Content Rules

### Youth And Adult

- Organize the 24-week sequence by themes.
- Keep offensive and defensive cycles together in two-week blocks where possible.
- Follow the hierarchy of learning for groundwork:
  - survival details only within escape contexts
  - escapes
  - guard
  - pins
  - passing
  - submissions
- Use takedown material informed by judo, freestyle wrestling, and Greco-Roman wrestling.
- Use submission structure with awareness of IBJJF safety constraints, while preparing students to understand broader rule sets.
- Do not force every weekly file to include takedown, ground technique, and submission sections if that weakens the thematic focus.
- Focus each week on the topic at hand.
- Include `Level 1` and `Level 2` options inside the same file rather than separate files.
- `Level 2` should add complexity, transitions, or chains rather than just restating `Level 1`.

Teaching principles that must shape the weekly files:

- position before submission
- rule of three
- ecological approach
- progressive resistance

Baseline class-time allocation for youth and adult:

- roughly one third sparring
- roughly one third drilling
- roughly one third for warm-up, instruction, transitions, and other class needs

### Tots

- Use a distinct weekly structure centered on fun and athletic development for BJJ.
- Prioritize movement, coordination, engagement, and simple grappling behaviors.
- Keep technical density low and age-appropriate.
- Avoid mirroring the youth positional map directly.

## Output Structure

All generated deliverables should be markdown files under `generated/` with Google Docs-friendly formatting.

Planned directory structure:

- `generated/curriculum/tots/`
- `generated/curriculum/youth/`
- `generated/curriculum/adult/`

Each program directory should contain one file per week for each output type:

- `curriculum`
- `quick-outline`
- `coach-guide`
- `fully-scripted-session`

Expected output counts:

- tots: 12 weeks x 4 files = 48 files
- youth: 24 weeks x 4 files = 96 files
- adult: 24 weeks x 4 files = 96 files

Total expected generated files: 240

## KB Changes Required Before Generation

The current KB already contains core curriculum and class-structure frameworks, but it does not yet contain a finalized explicit week-by-week sequence. The missing KB layer should be added before generation.

Required KB work:

- add or update curriculum-unit pages that make the youth 24-week sequence explicit
- add related pages for tots and adult sequencing as needed
- record adult reuse of youth structure with adult-specific deviations
- record the tots-specific structure as its own curriculum model
- mark proposed sequencing choices as `editorial-normalization` or `inference` where they are not directly present in raw sources
- create or retain `open-question` pages if any remaining ambiguity cannot be resolved from source material plus approved guidance

This is intentionally a minimal bridge approach rather than a full KB rebuild from scratch.

## Generation Model

### Curriculum Files

Each weekly curriculum file should define:

- the weekly theme
- the main teaching goal
- the primary technical focus or movement focus
- level 1 and level 2 options where relevant
- coach-useful notes that explain how pieces connect

### Quick Outline Files

Each quick outline should provide a fast-scan version of the week for coaches who already know the system and only need the core plan.

### Coach Guide Files

Each coach guide should expand the week with:

- coaching cues
- common mistakes
- safety notes where relevant
- scaling options where supported by the weekly material
- adult-specific notes or youth-specific notes as applicable

### Fully Scripted Session Files

Each fully scripted session should provide a higher-structure delivery aid for coaches who want a more complete teaching script, while still allowing adaptation to student needs.

## Sequencing Approach

The youth 24-week map should be proposed from existing KIN material and client guidance rather than treated as already fixed in source. The adult program should inherit that map except where adult-specific notes or adult-specific final weeks require divergence. The tots program should be designed independently around movement and engagement rather than around the youth technical sequence.

Weeks 23 and 24:

- youth: self-defense, standing and ground
- adult: lower-body submission module with offensive and defensive cycles, rule-set awareness, and safety framing

## Error Handling And Gaps

- Do not invent unsupported facts.
- If a specific weekly detail cannot be justified from source material or approved client direction, reduce confidence and represent it explicitly in the KB.
- If a needed prerequisite is missing, surface it as an open question or a generation note rather than smoothing it over.
- If existing KB content conflicts with approved client guidance, preserve the distinction and update confidence accordingly.

## Verification

Before considering implementation complete:

- rebuild KB indexes successfully
- verify the expected generated directory structure exists
- verify week counts for tots, youth, and adult
- verify youth weeks 23-24 are self-defense
- verify adult weeks 23-24 are lower-body submission focused
- verify adult files are separate from youth files, even where content is shared
- spot-check that level 1 and level 2 options appear within the same weekly files
- confirm tots files use their own fun and athletic-development structure

## Risks

- The week-by-week sequence is largely a proposed editorial construction rather than a directly authored source artifact.
- Generating 240 files is mechanically straightforward but can drift without careful template discipline.
- Adult reuse of youth content can accidentally introduce too much duplicated noise unless adult-specific filtering is applied deliberately.
- Tots content can become too technical if youth structure leaks into its templates.

## Recommended Next Step

Write an implementation plan that:

- defines the KB pages to add or update
- defines file naming conventions for the generated outputs
- proposes the 24-week youth sequence and corresponding adult adaptations
- proposes the 12-week tots structure
- specifies the generation workflow and verification commands
