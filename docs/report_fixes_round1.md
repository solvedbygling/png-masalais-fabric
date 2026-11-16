# Report review: round 1 fixes

Reviewed in Power BI Desktop on 15 Nov 2026. Apply to the semantic model (via MCP) and to
`report/Masalais_Board_Pack.Report` (Desktop closed). Validate when done.

## A. Semantic model
1. Add new lakehouse columns (Gold was rerun): `dim_school[SchoolGroup]` and `dim_participant[AgeBandSort]`.
   Refresh those tables if they can't be queried straight away.
2. Hide `dim_participant[AgeBandSort]`. Set `dim_participant[AgeBand]` to sort by it.
3. Date-only format `dd/MM/yyyy` on every date column: `dim_milestone[DueDate]`, `[CompletedDate]`, `[LastUpdated]`,
   `dim_agreement[StartDate]`, `[EndDate]`, `dim_school[ProgrammeJoinDate]`, `dim_participant[RegisteredDate]`,
   `fact_milestone_update[UpdateDate]`, `dim_date[Date]`.
4. `dim_milestone[LatestPctComplete]` and `fact_milestone_update[PctComplete]`: format `0` (they are 0 to 100 already).

## B. All pages
1. Delete the stray small grey rectangle in the header band (around x 1040, y 10) on every page.
2. Turn off the automatic subtitle on every visual. Titles stay.
3. Card number formatting: no display units for counts (show 6,398 not 6K); currency in millions shown with
   one decimal ($15.3M); currency under a million shown in full ($41,970). Cost per person shown in full ($1,1xx).
4. No card title may be truncated. Use these titles where needed:
   - Page 1 card 6: "Lines >10% over"
   - Pages 3 and 7: "No cost centre" and "Suspense account"

## C. Page 2
1. Agreements table must show all 9 columns and all 7 rows with no scrolling: reduce column widths and wrap headers
   (word wrap on), drop the FunderName column if still needed to fit (the funder slicer covers it), increase height to fit.
2. Matrix must show all programme rows including Unallocated, with no vertical scrolling: give it more height
   (reduce the table above if needed); keep the horizontal fit.

## D. Page 3
1. The budget matrix must open fully expanded to dim_cost_category[CostCategory] (agreement > programme > category).
   If the file format can't store the expanded state, tell me and I will expand it in Desktop and save.
2. Conditional background (red > 10%, amber 0 to 10%) applies to the category level only, not agreement or programme subtotals.
3. Turn off the grand total row (mixed currencies make it blank). Keep agreement subtotals.

## E. Page 4
1. Age band chart now sorts Under 12, 12-15, 16-18, 19-24, 25+ (from the model sort).
2. Programme bar chart: labels must not be truncated (widen the axis area or shrink the font).

## F. Page 5
1. Line chart legend: use `dim_school[SchoolGroup]` instead of `IsProgrammeSchool`; remove the legend title.

## G. Page 6
1. Milestone tracker must show all 9 columns with no horizontal scrolling, so RAG is visible:
   word wrap on the Description column, narrower columns, shorter headers via display names
   ("ID", "Milestone", "Agreement", "Due", "Status", "% done", "Completed", "Days late", "RAG").
2. Turn off the totals row.
3. "Grant payments not yet earned": visual filter Tranches Not Yet Earned (Agreement Ccy) > 0 (NSCF-2026 shows 0 and should disappear);
   header display name "Not yet earned"; totals off. Expected: CSSP-EST 500,000 only.
