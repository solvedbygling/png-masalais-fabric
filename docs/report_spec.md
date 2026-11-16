# Masalais Board Pack: report specification

**PNG Masalais (fictional club, synthetic data).** Thin report (PBIP, PBIR format) live-connected to the semantic model
`SM_Masalais_Board` in workspace `PNG Masalais`. Build all visuals from **measures** in the model; never sum raw columns.

Agent instructions:
- Report folder: `report/Masalais_Board_Pack.Report`. Power BI Desktop must be **closed** while editing.
- Apply the theme in `docs/masalais_theme.json`.
- Canvas 1280 x 720 on every page. Page background `#F4F7F5`. Visuals have white backgrounds and 6 px rounded borders (from theme).
- Build pages 1 to 7 in order, in the page order given. Use the exact page names (they are the board's questions).
- Do not create measures in the report. If a needed measure is missing, stop and say so.
- After building, validate the report files with the CLI and list any warnings.

## Shared layout (every page)

**Header band**: rectangle shape, x 0, y 0, w 1280, h 64, fill `#1B4332`, no border.
- Text box on the band, x 24, y 8, w 900, h 30: the page name, Segoe UI Semibold 18, white.
- Text box on the band, x 24, y 36, w 900, h 22: "As at 31 October 2026 · PNG Masalais (fictional club, synthetic data)", Segoe UI 10, colour `#B7D3C4`.
- Small accent bar: rectangle x 0, y 64, w 1280, h 4, fill `#E9A23B`.

Content area starts at y 84. Use 16 px gaps and a 24 px left and right margin.

Status colours (use only for status, never decoration): red `#C0392B`, amber `#E9A23B`, green `#2E8B57`.

---

## Page 1: Where do we stand?

**Row of 6 KPI cards** (y 84, h 100, each w 188, 16 px gaps, first at x 24, last ending at x 1256):
1. Funding Received AUD, title "Funding received (AUD)"
2. Spend AUD, title "Spent (AUD)"
3. Participants Reached, title "People reached"
4. Female Participation %, title "Female participation"
5. Milestones Overdue, title "Milestones overdue". Conditional font colour: red if > 0.
6. Over Budget Lines, title "Budget lines >10% over". Conditional font colour: red if > 0.

**Clustered bar chart** (x 24, y 200, w 600, h 300): "Funding received vs spent, by funder (AUD)"
- Y axis: dim_agreement[FunderName]; values: Funding Received AUD, Spend AUD. Sort by Spend AUD descending.

**Line and clustered column chart** (x 640, y 200, w 616, h 300): "Monthly spending vs budget (AUD)"
- X axis: dim_date[MonthName]; columns: Spend AUD; line: Budget AUD.
- Visual filter: dim_date[IsActual] = True and dim_date[IsEstablishmentPeriod] = True.

**Text box** (x 24, y 516, w 1232, h 180): title "For the board's attention", body as bullets:
- "PNG Government 2026 funding: PGK 6.5m received against PGK 8.2m spent. The club is bridging a PGK 1.7m gap with sponsor funds, and the delayed payment held up the gymnasium build (page 2, page 6)."
- "Three budget lines are more than 10% over, led by the training base Stage 1 and Australian grant overheads, both about 24% over (page 3)."
- "Administration is 11.5% of Australian grant spending, above the 10% cap in the agreement (page 3)."
- "Two milestones are overdue: provincial clinics (13 of 15 provinces, Western and Gulf outstanding) and the gymnasium, now expected late November (page 6)."
- Note in small grey text: "Commentary reflects data as at 31 October 2026."

## Page 2: Where did each funder's money go?

**Slicer** (x 24, y 84, w 300, h 60, dropdown): dim_agreement[FunderName].

**Table** (x 24, y 160, w 1232, h 260): "Funding agreements, in each agreement's own currency"
- Columns: dim_agreement[AgreementName], dim_agreement[FunderName], dim_agreement[Restriction], dim_agreement[Currency],
  Committed (Agreement Ccy), Received (Agreement Ccy), Spend (Agreement Ccy), Cash Position (Agreement Ccy),
  Utilisation of Received %.
- Totals row: off (agreement-currency measures can't be totalled across currencies).
- Conditional font colour on Cash Position (Agreement Ccy): red if < 0.
- Conditional data bars on Utilisation of Received %.

**Matrix** (x 24, y 436, w 800, h 260): "Where the money went: spending by programme and funder (AUD)"
- Rows: dim_programme[ProgrammeName]; columns: dim_agreement[AgreementID]; values: Spend AUD. Row and column totals on.

**Clustered bar** (x 840, y 436, w 416, h 260): "Restricted vs unrestricted spending (AUD)"
- Y axis: dim_agreement[Restriction]; values: Spend AUD.

## Page 3: Are we on budget?

**Matrix** (x 24, y 84, w 820, h 612): "Budget lines to date, in each agreement's currency"
- Rows (stepped): dim_agreement[AgreementID] > dim_programme[ProgrammeName] > dim_cost_category[CostCategory].
- Values: Budget to Date (Agreement Ccy), Spend (Agreement Ccy), Variance to Date % (Agreement Ccy).
- Conditional background on Variance to Date % (Agreement Ccy): red `#C0392B` with white font if > 0.10;
  amber `#E9A23B` if > 0 and <= 0.10; none otherwise.
- Expand to the lowest level by default.

**Card** (x 860, y 84, w 396, h 120): Admin Share %, title "Admin share of Australian grant (cap 10%)".
- Visual filter: dim_agreement[AgreementID] = "CSSP-EST". Conditional font colour: red if > 0.10.

**Clustered column** (x 860, y 220, w 396, h 260): "Variance to date by cost category (AUD)"
- X axis: dim_cost_category[CostCategory]; values: Variance to Date AUD. Sort descending.

**Two cards** (y 496, h 100, w 190 each, x 860 and x 1066):
- Unallocated Spend AUD, title "Spend with no cost centre"
- Suspense Spend AUD, title "Spend in suspense account"

**Text box** (x 860, y 612, w 396, h 84), small grey: "Unallocated and suspense amounts are real spending that finance has not yet coded correctly. They are kept in all totals. See page 7."

## Page 4: Who are we reaching?

**Slicer** (x 24, y 84, w 300, h 60, dropdown): dim_programme[ProgrammeName].
- Visual filter: dim_programme[IsParticipantBased] = "Yes".

**Row of 5 KPI cards** (x 340 to 1256, y 84, h 60, w 168 each):
Participants Reached ("People reached"), Attendances, Sessions Delivered ("Sessions"), Schools Reached ("Schools"),
Provinces Reached ("Provinces").

**Card** (x 24, y 160, w 300, h 100): Cost per Participant AUD, title "Cost per person reached (AUD)".

**Clustered bar** (x 24, y 276, w 300, h 420): "People reached by programme"
- Y axis: dim_programme[ProgrammeName]; values: Participants Reached. Visual filter IsParticipantBased = "Yes". Sort descending.

**Line chart** (x 340, y 160, w 456, h 260): "Female participation by month"
- X axis: dim_date[MonthName]; values: Female Participation %.
- Visual filter: dim_date[IsEstablishmentPeriod] = True. Y axis starts at 0.

**Stacked column** (x 812, y 160, w 444, h 260): "People reached by age band and gender"
- X axis: dim_participant[AgeBand]; legend: dim_participant[GenderLabel]; values: Participants Reached.

**Clustered bar** (x 340, y 436, w 916, h 260): "People reached by province"
- Y axis: dim_province[ProvinceName]; values: Participants Reached; sort descending; tooltip: dim_province[Region].

## Page 5: Is school rugby league linked to attendance?

**Line chart** (x 24, y 84, w 820, h 400): "School attendance rate by term"
- X axis: fact_school_attendance[TermLabel] (sorted by TermSort); values: School Attendance Rate;
  legend: dim_school[IsProgrammeSchool] (Y = programme school, N = comparison school). Legend title "Programme school".

**Clustered column** (x 860, y 84, w 396, h 400): "Attendance rate: before vs after joining"
- X axis: fact_school_attendance[Period], sorted by fact_school_attendance[PeriodSort] (Before joining, After joining, Comparison school); values: School Attendance Rate.

**Card** (x 24, y 500, w 300, h 100): Schools Reached, title "Schools in the programme".

**Text box** (x 340, y 500, w 916, h 196): title "How to read this", body:
"Programme schools started at about the same attendance rate as comparison schools. After joining, their rate rose by about seven points, while comparison schools rose by about two. This is consistent with the programme helping, but it does not prove it: schools were not chosen at random, and other factors may differ. A stronger test would compare matched schools over a longer period."

## Page 6: Are we delivering what we promised?

**Row of 4 KPI cards** (y 84, h 90, w 296 each): Milestones ("Milestones"), Milestones Complete ("Complete"),
Milestones Completed Late ("Completed late"), Milestones Overdue ("Overdue", font red if > 0).

**Table** (x 24, y 190, w 900, h 506): "Milestone tracker"
- Columns: dim_milestone[MilestoneID], dim_milestone[Description], dim_agreement[AgreementID], dim_milestone[DueDate],
  dim_milestone[LatestStatus], dim_milestone[LatestPctComplete], dim_milestone[CompletedDate], dim_milestone[DaysLate],
  dim_milestone[RAG].
- Sort by DueDate ascending.
- Conditional background on RAG by text value: "Red" `#C0392B` (white font), "Amber" `#E9A23B`, "Green" `#2E8B57` (white font),
  "Complete" `#DDE5E0`.

**Table** (x 940, y 190, w 316, h 250): "Grant payments not yet earned"
- Columns: dim_agreement[AgreementID], Tranches Not Yet Earned (Agreement Ccy). Visual filter: measure is not blank.

**Text box** (x 940, y 456, w 316, h 240), small: "Some grant payments are released only when a milestone is met. A late milestone delays the cash: the training base (M04) finished 73 days late, delaying an AUD 1.5m payment by about three months."

## Page 7: Can we trust the numbers?

**Row of 4 KPI cards** (y 84, h 90, w 296 each): DQ Issues ("Issues found"), DQ Rows Removed ("Removed"),
DQ Rows Corrected ("Corrected"), DQ Rows Flagged ("Flagged or quarantined").

**Table** (x 24, y 190, w 820, h 506): "What the pipeline found and did"
- Columns: dq_log[SourceTable], dq_log[Rule], dq_log[Action], DQ Issues. Sort by DQ Issues descending.

**Text box** (x 860, y 190, w 396, h 300): title "Rules this pipeline follows", bullets:
- "Real money is never dropped. Lines with problems stay in every total and are flagged for finance."
- "Only records that are not real are removed, such as the same journal exported twice."
- "Fixable errors are corrected and logged with the original value, such as fund codes typed in different ways."
- "Attendance that can't be linked to a registered person is set aside, so reach isn't overstated."

**Two cards** (y 506, h 90, w 190 each, x 860 and x 1066): Unallocated Spend AUD, Suspense Spend AUD.
