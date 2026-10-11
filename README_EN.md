# Project Will — Observations #4–#6 and Series Synthesis (2026-09-13 to 09-28)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23277761.svg)](https://doi.org/10.5281/zenodo.23277761)

Full logs and analyses of the third installment of **Project Will**: 32 autonomous LLM villagers in Minecraft, observed for 6 hours with **no rules, no rewards, no assigned roles, and no instruction to cooperate**. This release covers three 6-hour runs — Observation #4 ("mind and books"), #5 ("body and hunger"), #6 ("instinct") — and four verification runs after #6 (B-39 to B-42) that asked: *did society fail to emerge because of defects in our own system?* The report doubles as a **synthesis of the whole series (#1–#6)**.

Video: https://youtu.be/l-lXAbYm5Jo

Previous releases by the same author: [Observation #1](https://github.com/MONOCOLACHANNEL/project-will-observation-1) (DOI [10.5281/zenodo.21723921](https://doi.org/10.5281/zenodo.21723921)) · [Observations #2–#3](https://github.com/MONOCOLACHANNEL/project-will-observations-2-3) (DOI [10.5281/zenodo.22040887](https://doi.org/10.5281/zenodo.22040887)).

Models: decisions and dialogue by Gemini 3.5 Flash-Lite (Gemini 3.8 Flash at branch points), memory consolidation by Gemini 3 Flash preview.

## What was changed

- **#4 — mind and books**: day/time-of-day awareness, a written "foresight" for each action checked against outcomes at night, honest perception (you cannot see inside another's house until you enter), and **a book for every villager from the start** — with no stated purpose.
- **#5 — body and hunger**: 15 body traits (size, strength, speed, digging speed, hunger rate, eyesight, …) independently randomized per individual and hidden from everyone; starvation can now kill.
- **#6 — instinct**: the "discontent" drive was removed and replaced by instincts (lineage, mate, child welfare, stockpile, territory, bond, exploration). We also removed what we judged to be *the system's own morality* — a grudge ledger that auto-adjusted affinity and an attack gate that only opened against grudge targets. Instead, each villager's **own attitude ratings (−2…+2) and promises are persisted and shown back every time**, and children cannot feed themselves for their first 20 minutes.
- **After #6**: we removed conversational prompts that steered talk toward "my plans" (B-39/40), repaired the pathway by which witnessed events reach memory and conversation (B-41), ran a **whole-system audit that found 109 defects** (31 affecting the core questions or measurement), fixed 105 of them (148 fixes in total after #6), **froze the counting rules and thresholds before launch**, and re-ran for 2 hours (B-42).

## Headline results

- **#4 was "a village where nobody needed anybody."** Zero killings (attack was offered 245 times, chosen 0 times). 2,322 pages were written — almost all monologue; no contracts, trades, or signatures. Zero utterances proposing an exchange of goods.
- **#5: hunger created debts that could be called in across time** ("Don't you dare say you forgot about the food I asked for"). Books became accusations and imitation legal codes (numbered articles that could not be cross-referenced). Requests for goods or help rose from 5.6% to 14.4% (two-pass blind coding). Still zero exchanges, zero compensation.
- **#6: violence came from one individual's choice, without any system ledger.** Of 220 attack choices, 157 (71%) were by one villager, Toa Kashiwagi, who committed 10 of the 12 killings; 23 of 38 villagers who could attack never did. The seed — an obsession with "order" and anger at having her plans disrupted — was in the persona card written at the start.
- **Books went from monologue (#4) to circulars and accusations (#5) to objects seized in the name of "censorship" (#6).** Toa killed two villagers while aiming to confiscate their books, and wrote *"Record of the Village's Discipline and Control"* in the book taken from an 11-minute-old child. Nobody ever read it.
- **A child born in the village grew up, married, lost her 11-minute-old son to the tyrant, and killed the tyrant.** It was not the village that stopped the tyrant.
- **Words changed behavior only in situations where a villager's own memories and ratings were placed in front of them every time** (3 cases, no controls: revenge after the son's death; fleeing 3.7× more often — 3.7–9× depending on the count — from someone rated −2; a villager told "show it with actions" went from 0 to 44 farming actions). Yet **peers' commands almost never worked** (8 of 170 commands by "order-minded" villagers were carried out), while the **designer-side persona cards were followed closely, at least in speech** (6 of 10 villagers checked used their card's catchphrase in 70%+ of utterances). The difference is consistent with *how* the words entered the prompt — every time, as "this is who you are," versus once, as a quoted line "X told you …" that fades within minutes — though we did not manipulate this directly.
- **Society stopped at pairs and families**: zero non-family coordination decided in conversation, zero reciprocal exchange, zero norms addressed to the village, zero collective response to the tyrant.
- **After fixing the system, the core signals still did not appear.** In B-42 (105 defects fixed, rules frozen in advance): coordination 0, news delivered to non-witnesses by a speaker who chose to tell them 0, verbal exchange 0. The only signal: villagers who had not witnessed an assault *overheard* a victim scolding the attacker (3 cases, via the newly added overhearing pathway). In that run one villager killed 20; 26 of 35 died; **nobody told anyone about any of the deaths**.

**Series synthesis**: *Part 1 — a society made only of words. Part 2 — four signs. Part 3 — relationships that last only between two.* Under conditions with no rewards, no assigned roles, and no "cooperate," at least with this model and this method, no mechanism for meshing with others emerged within 6 hours. This is **not** a claim that "LLMs cannot build societies": we never provided a collective-action move, a dedicated channel for news, or an exchange move, and we tested only one model family.

The main figures in the report can be recomputed from the bundled data (see `VERIFICATION.md`).

## Files

- `README.md` — Japanese overview / `REPORT.md` (+ `REPORT.pdf`) — full technical report (Japanese)
- `VERIFICATION.md` — claim ↔ data mapping
- `DATA.md` — data dictionary and caveats / `METHOD_AND_LIMITS.md` — honest disclosure of flaws and limits
- `DESIGN_GEN3.md` — design of what was added and removed / `AUDIT_109.md` — the 109 defects and how they were handled / `INVENTORY.md` — all 35 runs and counts of changes
- `data/` — event ledgers (gzipped JSONL), full speech timelines, full book texts, persona cards, death lists for #4, #5, #6, B-39–B-42
- `tools/find.py` — cross-log search utility

## Citation

> Monocola (モノコーラ). (2026). Project Will: Observations #4–#6 and series synthesis — LLM villagers given books, bodies, and instincts [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.23277761

License: data & documents CC BY 4.0 / scripts MIT.
