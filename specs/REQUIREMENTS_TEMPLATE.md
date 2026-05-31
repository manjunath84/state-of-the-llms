# <Feature> — Requirements

> Copy this file into `specs/<YYYY-MM-DD-feature-slug>/requirements.md` when
> starting a new feature. Adapted from the SSM-PDFTool requirements template.

## Goal
One paragraph: what this feature delivers and for whom.

## Non-goals
What this feature explicitly does **not** do (YAGNI boundary).

## Scenarios
Concrete user/system flows. "Given … when … then …" where it helps.

## Constraints
Performance, privacy, platform, deadline, budget — the hard edges.

## Reference calls (verbatim)
Exact external API signatures / model ids / CSV schemas / pricing rows this
feature depends on, copied **verbatim** from the source (never paraphrased).
This is the anti-hallucination discipline: a number with no verbatim source
does not ship.

## Output contracts
The shape of what each unit returns (dataclasses, DataFrame columns, JSON keys).

## Dependencies
Other modules, data files, services, or features this relies on.
