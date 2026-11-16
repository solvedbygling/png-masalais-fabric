# Round 3: automatic commentary and final polish

Final round. **Do not add slicers.** Power BI Desktop must be closed. Part A goes to the semantic model via MCP;
parts B and C to `report/Masalais_Board_Pack.Report`. After the changes, screenshot all 7 pages with the service preview
(workspace `5c84a9ef-2839-4030-8f33-a2c1276c7190`), compare against `docs/mockups/Masalais_Page1_Mockup.png` and
`docs/design_spec_v2.md`, and keep fixing until they match. Then list anything still different.

---

## A. Commentary measures (display folder `Commentary`, home table `fact_gl` unless stated)

Design: the four issue rows on page 1 are fixed (bridging finance, budget overruns, admin cap, overdue milestones).
The **text and the status of each row are calculated**, so they change when the data changes. When an issue clears,
the row says so and shows **OK**. Status rules are written into each measure so they can be explained in an interview.

### Row 1: Bridging finance
Risk when any **restricted** agreement has spent more than it has received. Describes the worst one.

**Board Bridging Text**
```dax
VAR t =
    FILTER (
        ADDCOLUMNS (
            CALCULATETABLE ( VALUES ( dim_agreement[AgreementID] ), dim_agreement[Restriction] = "Restricted" ),
            "@cash", [Cash Position (Agreement Ccy)],
            "@rec", [Received (Agreement Ccy)],
            "@sp", [Spend (Agreement Ccy)]
        ),
        [@cash] < 0
    )
VAR n = COUNTROWS ( t )
VAR worst = TOPN ( 1, t, [@cash], ASC )
VAR id = MAXX ( worst, dim_agreement[AgreementID] )
VAR ccy = CALCULATE ( SELECTEDVALUE ( dim_agreement[Currency] ), dim_agreement[AgreementID] = id )
VAR funder = CALCULATE ( SELECTEDVALUE ( dim_agreement[FunderName] ), dim_agreement[AgreementID] = id )
VAR agr = CALCULATE ( SELECTEDVALUE ( dim_agreement[AgreementName] ), dim_agreement[AgreementID] = id )
RETURN
    IF (
        n = 0,
        "No restricted funding is overspent against what funders have paid.",
        funder & ", " & agr & ": " & ccy & " " & FORMAT ( MAXX ( worst, [@rec] ) / 1e6, "0.0" ) & "m received, "
            & ccy & " " & FORMAT ( MAXX ( worst, [@sp] ) / 1e6, "0.0" ) & "m spent. The club is covering a "
            & ccy & " " & FORMAT ( - MAXX ( worst, [@cash] ) / 1e6, "0.0" ) & "m gap from other funds."
            & IF ( n > 1, " " & ( n - 1 ) & " more restricted agreement(s) also overspent.", "" )
    )
```
**Board Bridging Status**: `IF ( <same n> > 0, "Risk", "OK" )`. Reuse the filter logic (copy the `t` and `n` variables).

### Row 2: Budget overruns
Risk when any budget line (agreement, programme, cost category) is more than 10% over budget to date. Lists up to three, worst first.

**Board Overrun Text** (home `fact_budget`)
```dax
VAR lines =
    FILTER (
        ADDCOLUMNS (
            SUMMARIZE ( fact_budget, dim_agreement[AgreementID], dim_programme[ProgrammeID], dim_cost_category[CostCategory] ),
            "@v", [Variance to Date % (Agreement Ccy)]
        ),
        [@v] > 0.10
    )
VAR n = COUNTROWS ( lines )
VAR txt =
    CONCATENATEX (
        TOPN ( 3, lines, [@v], DESC ),
        dim_cost_category[CostCategory] & ", " & dim_agreement[AgreementID] & " (+" & FORMAT ( [@v], "0%" ) & ")",
        "; ", [@v], DESC
    )
RETURN
    IF (
        n = 0,
        "No budget line is more than 10% over budget to date.",
        n & IF ( n = 1, " line is", " lines are" ) & " more than 10% over: " & txt
            & IF ( n > 3, "; and " & ( n - 3 ) & " more.", "." )
    )
```
**Board Overrun Status**: `"Risk"` if n > 0, else `"OK"`.

### Row 3: Admin cap
The Australian grant (CSSP-EST) caps administration at 10% of spending (see its RestrictionNotes).
Watch above 10%, Risk above 12%, otherwise OK.

**Board Admin Text**
```dax
VAR s = CALCULATE ( [Admin Share %], dim_agreement[AgreementID] = "CSSP-EST" )
RETURN "Administration is " & FORMAT ( s, "0.0%" ) & " of Australian grant spending, "
    & IF ( s > 0.10, "above", "within" ) & " the 10% cap in the agreement."
```
**Board Admin Status**: `IF ( s > 0.12, "Risk", IF ( s > 0.10, "Watch", "OK" ) )` (same `s`).

### Row 4: Overdue milestones (home `dim_milestone`)
Risk when an overdue milestone has grant money tied to it (TrancheAmount > 0), because it holds back cash.
Watch when milestones are overdue but none is payment-linked. OK when none are overdue.

**Board Milestone Text**
```dax
VAR od = FILTER ( dim_milestone, dim_milestone[IsOverdue] = TRUE () )
VAR n = COUNTROWS ( od )
RETURN
    IF (
        n = 0,
        "No milestones are overdue.",
        n & IF ( n = 1, " milestone is", " milestones are" ) & " overdue: "
            & CONCATENATEX ( od, dim_milestone[MilestoneID] & " " & dim_milestone[Description]
                & " (" & dim_milestone[DaysLate] & " days late)", "; ", dim_milestone[DaysLate], DESC ) & "."
    )
```
**Board Milestone Status**
```dax
VAR od = FILTER ( dim_milestone, dim_milestone[IsOverdue] = TRUE () )
RETURN IF ( COUNTROWS ( od ) = 0, "OK", IF ( SUMX ( od, dim_milestone[TrancheAmount] ) > 0, "Risk", "Watch" ) )
```

### Status pill colours (one pair, used by all four rows via the row's status measure)
Create per row: **Board <Row> Pill Back** and **Board <Row> Pill Font**, or one generic pattern:
`SWITCH ( [Board X Status], "Risk", "#FBE5E8", "Watch", "#FBF1D6", "#E3F1E8" )` (background) and
`SWITCH ( [Board X Status], "Risk", "#C8102E", "Watch", "#9A6B00", "#2F7D4F" )` (font).

### Page 6 explanation (home `dim_milestone`)
**Milestone Cash Note**: uses the payment-linked milestone that finished latest relative to its due date.
```dax
VAR late = FILTER ( dim_milestone, dim_milestone[TrancheAmount] > 0 && dim_milestone[CompletedLate] = TRUE () )
VAR w = TOPN ( 1, late, dim_milestone[DaysLate], DESC )
VAR id = MAXX ( w, dim_milestone[MilestoneID] )
VAR ccy = CALCULATE ( SELECTEDVALUE ( dim_agreement[Currency] ),
                      TREATAS ( { MAXX ( w, dim_milestone[AgreementID] ) }, dim_agreement[AgreementID] ) )
RETURN
    "Some grant payments are released only when a milestone is met, so a late milestone delays the cash. "
        & IF (
            COUNTROWS ( late ) = 0,
            "So far, every payment-linked milestone has been met on time.",
            "The latest so far: " & MAXX ( w, dim_milestone[Description] ) & " (" & id & ") finished "
                & MAXX ( w, dim_milestone[DaysLate] ) & " days late, delaying the " & ccy & " "
                & FORMAT ( MAXX ( w, dim_milestone[TrancheAmount] ) / 1e6, "0.0" ) & "m payment tied to it."
        )
```

### Validation (no filters)
| Measure | Expected |
|---|---|
| Board Bridging Text | "PNG National Sport and Community Fund, 2026 Appropriation: PGK 6.5m received, PGK 8.2m spent. The club is covering a PGK 1.7m gap from other funds." |
| Board Bridging Status | Risk |
| Board Overrun Text | "3 lines are more than 10% over: Facilities, CSSP-EST (+24%); Overheads, CSSP-EST (+24%); Travel, NSCF-2026 (+18%)." |
| Board Overrun Status | Risk |
| Board Admin Text / Status | "Administration is 11.5% of Australian grant spending, above the 10% cap in the agreement." / Watch |
| Board Milestone Text | "2 milestones are overdue: M10 Provincial clinics delivered in 15 provinces (31 days late); M11 Training base Stage 2 (gymnasium) complete (16 days late)." |
| Board Milestone Status | Watch (neither overdue milestone has a tranche) |
| Milestone Cash Note | mentions Training base Stage 1 complete (M04), 73 days late, AUD 1.5m |

Note to agent: dim_milestone[AgreementID] is hidden but usable in DAX. If a measure errors, fix the DAX and say what you changed.

---

## B. Wire the commentary into the report

**Page 1 panel**: keep the layout, numbered badges, Issue labels (static text is fine for these four labels) and page links.
- Replace each row's detail text box with a visual that shows the row's **Text** measure: left aligned, 11 pt charcoal,
  word wrap on, no title, no background, no border, no truncation. If a text runs over one line, reduce to 10.5 pt or
  give the row a little more height; every word must be visible.
- Replace each status pill with a visual showing the row's **Status** measure, background colour from the Pill Back
  measure and font colour from the Pill Font measure (conditional formatting by field value), rounded 9, bold 10.5 pt, centred.
- Delete the old static detail text boxes and pills.

**Page 6**: replace the explanation text box with a visual showing **Milestone Cash Note**, same style as the other
text on that page (word wrap, no truncation).

---

## C. Polish

1. **Table and matrix headers: plain labels, never field names** (rename in the visual, not the model):
   - Page 2 agreements: Agreement, Funder, Restriction, Currency, Committed, Received, Spent, Cash position, Utilisation
   - Page 2 matrix: Programme (rows); keep the agreement IDs as columns
   - Page 3 matrix: Agreement / programme / category (row header), Budget to date, Spent, Variance
   - Page 6 "Grant payments not yet earned": Agreement, Not yet earned
   - Page 7: Source, Rule, Action, Issues
2. **Page 2**: matrix shows every programme row (including Schools, Women's and Unallocated) with no vertical scroll:
   tighten row padding and give it more height, shrinking the table above if it has spare space.
   Restricted vs unrestricted labels with one decimal ($13.2M style).
3. **Page 3**: no truncated row headers (widen the first column so "High Performance Staff and Facilities" fits).
   Variance by cost category: red `#C8102E` columns where Variance to Date AUD > 0, charcoal otherwise
   (use a rule on the single measure; this chart has only one measure so conditional colour is allowed).
4. **Page 4**: programme chart data labels as whole numbers with no display units (Academy 48, Provincial Clinics 2,803);
   every bar labelled (widen the chart area or put labels inside end if needed).
5. **Page 5**: balance the bottom row: Schools card and "How to read this" box the same height, sized to the text with no big empty area.
6. **Page 7**: shrink the table card to fit its rows (no large empty space), and remove the big left indent on the rules text.
