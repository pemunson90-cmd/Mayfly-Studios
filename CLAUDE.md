## MANDATORY: update stale docs after every PR/push

**Standing order from Pat: every PR and every push must leave current documentation accurate.** After opening, updating or merging a PR, and after every push, review the affected docs against the actual code and repository state. Update stale or outdated instructions, status, versions, paths, commands, links and handoffs before calling the work finished. Include known corrections with the change when possible; verify them again after publication. Do not make empty edits when the docs are already current.

- **Agentic work:** use the smallest capable model available for the documentation pass. Escalate only when the task needs it.
- **Regular chat or bots without model selection:** do the documentation work with the available model. Lack of model selection is not a reason to skip it.
- Update the existing authoritative document and its affected pointers. Preserve historical evidence as history; avoid creating competing status documents.
- End the PR/push closeout with the docs updated, or what was checked and why no update was needed. If blocked, name the stale file/claim, blocker and next action; do not claim the docs are current.
- Respect existing file ownership, approval and publication rules. Pass changes through the current coordinator at a safe boundary; preserve active work. This order does not authorize an otherwise unapproved push, merge, deletion, deployment or spending.
- Keep checks proportional to documentation changes. Do not start broad application suites or automatic push/CI loops just for this order. A docs-only follow-up still gets a freshness check; do not keep committing solely to update the follow-up's own commit identifier.

## Non-negotiable feature continuity (owner directive)

**If Pat did not explicitly authorize removing a working capability, it stays.** Existing working features, gameplay rules, card effects, interfaces, workflows, integrations, content, data, settings, accessibility, and tools survive fixes, refactors, rewrites, ports, engine replacements and architecture changes. Do not silently delete, stub, disable, simplify, postpone or leave them behind because a new implementation is cleaner or the task named only one feature. Lack of an explicit preservation list is **not** permission to drop anything.

**Before coding**, identify the actual most recent owner-accepted/installed usable baseline and the current authoritative development/integration branch; verify commit ancestry and inspect existing successful implementations, including playable prototypes, simulators and branches that the new work replaces. Neither `main` nor the newest-looking version number alone establishes the full feature set. For replacements or substantial refactors, account for each relevant existing capability and preserve behavior or explicitly approved improvements; check meaningful parity/regressions against the old working path. Recheck on the final integration head. If preservation and the requested change conflict, retain the old working functionality and seek Pat's explicit ruling on that **specific** loss; continue independent non-destructive work. Do not substitute extra paperwork or indiscriminate test campaigns for actual continuity checks. Apply updated guidance at the next safe work boundary without disrupting active writers.

