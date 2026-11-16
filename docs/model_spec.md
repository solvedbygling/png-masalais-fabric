# SM_Masalais_Board: semantic model specification

**PNG Masalais (fictional club, synthetic data).** Direct Lake semantic model on `LH_Gold`, workspace `PNG Masalais`.
This file is the single source of truth for model housekeeping and measures. An agent applies it; a human reads it.

Agent instructions:
- Connect to semantic model `SM_Masalais_Board` in Fabric workspace `PNG Masalais`. Do not create a new model.
- The 16 tables and 23 relationships already exist and are correct. **Do not add, remove or change relationships or tables.**
- Apply sections 1 to 3 in order. Add each measure's description as the measure description (used later by a Fabric data agent).
- Then run the validation queries in section 4 and report actual vs expected.

---

## 1. Housekeeping

### 1.1 Date table
- Mark `dim_date` as the date table, key column `Date` (skip if already marked).

### 1.2 Sort by column
| Column | Sort by |
|---|---|
| dim_date[MonthName] | dim_date[MonthSort] |
| dim_date[AU_FY] | dim_date[AU_FY_Sort] |
| fact_school_attendance[TermLabel] | fact_school_attendance[TermSort] |
| fact_school_attendance[Period] | fact_school_attendance[PeriodSort] (hidden) |

### 1.3 Hide (report builders should only see what is worth dragging onto a visual)
- Every fact table: `DateKey` and every key column that joins to a dimension
  (`AccountCode`, `ProgrammeID`, `AgreementID`, `CostCategory`, `ProvinceCode`, `SchoolID`, `ParticipantID`, `MilestoneID`).
  The dimension's copy of each key stays visible.
- `dim_milestone`: `AgreementID`, `ProgrammeID` (they join to dimensions).
- `fact_gl`: `BudgetLineKey`, `SourceFile`, `AUDtoPGK`, `AgreementCurrency`.
- `fact_budget`: `BudgetLineKey`.
- `dim_date`: `DateKey`, `MonthSort`, `AU_FY_Sort`. `fact_school_attendance`: `TermSort`.
- Raw amount columns that measures replace: `fact_gl[AmountLocal]`, `fact_gl[AmountAUD]`, `fact_gl[AmountAgreementCcy]`,
  `fact_budget[BudgetAmount]`, `fact_budget[BudgetAUD]`. (Report authors use measures, not raw sums.)

### 1.4 Summarize by: None
`dim_date[Year]`, `dim_date[PNG_FY]`, `fact_school_attendance[Year]`, `fact_school_attendance[Term]`,
`fact_school_attendance[Enrolled]`, `fact_school_attendance[AvgAttendanceRate]`, `dim_participant[AgeAtRegistration]`,
`dim_milestone[DaysLate]`, `dim_milestone[LatestPctComplete]`, `dim_milestone[TrancheAmount]`,
`dim_agreement[CommittedAmount]`, `fact_session[DurationMins]`.

---

## 2. Conventions used by every measure

- **Sign:** the ledger stores expenses positive and income negative (credits). Income measures put a minus in front to show positive.
- **AUD measures** are for board-level totals across funders. PGK is converted at the monthly average rate (done in Gold).
- **Agreement Ccy measures** judge each agreement in its own currency. They return blank when more than one currency is
  in the filter context (`HASONEVALUE`), because adding AUD to PGK is meaningless. Use them per agreement.
- **Formats:** AUD `$#,0`; agreement currency `#,0`; percentages `0.0%`; counts `#,0`.

---

## 3. Measures

### Folder: Finance (home table `fact_gl`)

**Spend AUD**: `$#,0`
Money spent (expense accounts only), in AUD.
```dax
CALCULATE ( SUM ( fact_gl[AmountAUD] ), dim_account[AccountType] = "Expense" )
```

**Funding Received AUD**: `$#,0`
Grant and sponsorship money received from funders, in AUD. Excludes bank interest (no agreement).
```dax
- CALCULATE (
    SUM ( fact_gl[AmountAUD] ),
    dim_account[AccountType] = "Revenue",
    NOT ISBLANK ( fact_gl[AgreementID] )
)
```

**Sponsorship Revenue AUD**: `$#,0`
Corporate sponsorship income (account 4200), in AUD.
```dax
- CALCULATE ( SUM ( fact_gl[AmountAUD] ), dim_account[AccountCode] = "4200" )
```

**Spend (Agreement Ccy)**: `#,0`
Spending charged to an agreement, in that agreement's own currency. Blank if currencies are mixed.
```dax
IF (
    HASONEVALUE ( dim_agreement[Currency] ),
    CALCULATE ( SUM ( fact_gl[AmountAgreementCcy] ), dim_account[AccountType] = "Expense" )
)
```

**Received (Agreement Ccy)**: `#,0`
Money received under an agreement, in its own currency. Blank if currencies are mixed.
```dax
IF (
    HASONEVALUE ( dim_agreement[Currency] ),
    - CALCULATE ( SUM ( fact_gl[AmountAgreementCcy] ), dim_account[AccountType] = "Revenue" )
)
```

**Committed (Agreement Ccy)**: `#,0`
Total value the funder committed in the agreement, in its own currency.
```dax
IF ( HASONEVALUE ( dim_agreement[Currency] ), SUM ( dim_agreement[CommittedAmount] ) )
```

**Cash Position (Agreement Ccy)**: `#,0`
Received minus spent. Negative means the club has spent more than this funder has paid and is bridging the gap with other money.
```dax
[Received (Agreement Ccy)] - [Spend (Agreement Ccy)]
```

**Utilisation of Received %**: `0.0%`
Share of money received from a funder that has been spent. Over 100% means bridging.
```dax
DIVIDE ( [Spend (Agreement Ccy)], [Received (Agreement Ccy)] )
```

**Utilisation of Committed %**: `0.0%`
Share of the funder's total commitment that has been spent.
```dax
DIVIDE ( [Spend (Agreement Ccy)], [Committed (Agreement Ccy)] )
```

**Admin Spend AUD**: `$#,0`
Spending on governance and administration (programme P99).
```dax
CALCULATE ( [Spend AUD], dim_programme[ProgrammeID] = "P99" )
```

**Admin Share %**: `0.0%`
Administration spending as a share of all spending in the current filter (ignores any programme filter).
The Australian grant caps this at 10%.
```dax
DIVIDE ( [Admin Spend AUD], CALCULATE ( [Spend AUD], REMOVEFILTERS ( dim_programme ) ) )
```

**Unallocated Spend AUD**: `$#,0`
Spending booked without a cost centre. A data quality item for finance to correct.
```dax
CALCULATE ( [Spend AUD], dim_programme[ProgrammeID] = "UNALLOCATED" )
```

**Suspense Spend AUD**: `$#,0`
Spending posted to the suspense account 5999. A data quality item for finance to reclassify.
```dax
CALCULATE ( [Spend AUD], dim_account[AccountCode] = "5999" )
```

### Folder: Budget (home table `fact_budget`)

**Budget AUD**: `$#,0`
Approved budget in AUD (all months, including future months).
```dax
SUM ( fact_budget[BudgetAUD] )
```

**Budget to Date AUD**: `$#,0`
Budget for months up to the reporting date (31 Oct 2026), so it compares fairly with actual spending.
```dax
CALCULATE ( [Budget AUD], dim_date[IsActual] = TRUE () )
```

**Variance to Date AUD**: `$#,0`
Spending minus budget to date. Positive means over budget.
```dax
[Spend AUD] - [Budget to Date AUD]
```

**Variance to Date %**: `0.0%`
Variance as a share of budget to date. Positive means over budget.
```dax
DIVIDE ( [Variance to Date AUD], [Budget to Date AUD] )
```

**Budget to Date (Agreement Ccy)**: `#,0`
Budget to date in the agreement's own currency. Blank if currencies are mixed.
```dax
IF (
    HASONEVALUE ( dim_agreement[Currency] ),
    CALCULATE ( SUM ( fact_budget[BudgetAmount] ), dim_date[IsActual] = TRUE () )
)
```

**Variance to Date % (Agreement Ccy)**: `0.0%`
Budget variance judged in the agreement's own currency. This is the figure the 10% overspend alert uses.
```dax
DIVIDE (
    [Spend (Agreement Ccy)] - [Budget to Date (Agreement Ccy)],
    [Budget to Date (Agreement Ccy)]
)
```

**Over Budget Lines**: `#,0`
Number of budget lines (agreement, programme, cost category) more than 10% over budget to date.
```dax
COUNTROWS (
    FILTER (
        SUMMARIZE ( fact_budget, dim_agreement[AgreementID], dim_programme[ProgrammeID], dim_cost_category[CostCategory] ),
        [Variance to Date % (Agreement Ccy)] > 0.10
    )
)
```

### Folder: Programmes (home table `fact_attendance`)

**Participants Reached**: `#,0`
Distinct people who attended at least one session. This is "reach": one person attending 20 times counts once.
```dax
DISTINCTCOUNT ( fact_attendance[ParticipantID] )
```

**Attendances**: `#,0`
Total attendance records (one per person per session).
```dax
COUNTROWS ( fact_attendance )
```

**Female Participants**: `#,0`
Distinct female participants reached.
```dax
CALCULATE ( [Participants Reached], dim_participant[GenderLabel] = "Female" )
```

**Female Participation %**: `0.0%`
Share of participants reached who are female.
```dax
DIVIDE ( [Female Participants], [Participants Reached] )
```

**Sessions Delivered**: `#,0`
Number of sessions delivered.
```dax
COUNTROWS ( fact_session )
```

**Schools Reached**: `#,0`
Distinct schools where participants attended a session.
```dax
DISTINCTCOUNTNOBLANK ( fact_attendance[SchoolID] )
```

**Provinces Reached**: `#,0`
Distinct provinces where participants attended a session.
```dax
DISTINCTCOUNTNOBLANK ( fact_attendance[ProvinceCode] )
```

**Cost per Participant AUD**: `$#,0`
Spending divided by participants reached, for participant-based programmes only
(excludes high-performance staff and facilities, administration and unallocated spending).
```dax
DIVIDE (
    CALCULATE ( [Spend AUD], dim_programme[IsParticipantBased] = "Yes" ),
    CALCULATE ( [Participants Reached], dim_programme[IsParticipantBased] = "Yes" )
)
```

**School Attendance Rate**: `0.0%`
Average school attendance rate, weighted by enrolment so large schools count for more than small ones.
```dax
DIVIDE (
    SUMX ( fact_school_attendance, fact_school_attendance[AvgAttendanceRate] * fact_school_attendance[Enrolled] ),
    SUM ( fact_school_attendance[Enrolled] )
)
```

### Folder: Milestones (home table `dim_milestone`)

**Milestones**: `#,0`
```dax
COUNTROWS ( dim_milestone )
```

**Milestones Complete**: `#,0`
```dax
CALCULATE ( [Milestones], dim_milestone[IsComplete] = TRUE () )
```

**Milestones Overdue**: `#,0`
Milestones past their due date and not complete, as at the reporting date.
```dax
CALCULATE ( [Milestones], dim_milestone[IsOverdue] = TRUE () )
```

**Milestones Completed Late**: `#,0`
```dax
CALCULATE ( [Milestones], dim_milestone[CompletedLate] = TRUE () )
```

**Tranches Not Yet Earned (Agreement Ccy)**: `#,0`
Grant payments tied to milestones that are not yet complete, in the agreement's currency.
```dax
IF (
    HASONEVALUE ( dim_agreement[Currency] ),
    CALCULATE ( SUM ( dim_milestone[TrancheAmount] ), dim_milestone[IsComplete] = FALSE () )
)
```

### Folder: Data Quality (home table `dq_log`)

**DQ Issues**: `#,0`
Data quality findings from the latest pipeline run.
```dax
COUNTROWS ( dq_log )
```

**DQ Rows Removed**: `#,0`
```dax
CALCULATE ( [DQ Issues], dq_log[Action] = "Removed" )
```

**DQ Rows Corrected**: `#,0`
```dax
CALCULATE ( [DQ Issues], CONTAINSSTRING ( dq_log[Action], "Corrected" ) )
```

**DQ Rows Flagged**: `#,0`
```dax
CALCULATE ( [DQ Issues], CONTAINSSTRING ( dq_log[Action], "Flagged" ) || dq_log[Action] = "Quarantined" )
```

---

## 4. Validation (run as DAX queries, report actual vs expected)

| Check | Query idea | Expected |
|---|---|---|
| Received / spent per agreement | `[Received (Agreement Ccy)]`, `[Spend (Agreement Ccy)]` by `dim_agreement[AgreementID]` | CSSP-EST 8,500,000 / 8,014,565; NSCF-2026 6,500,000 / 8,243,892; TUM-PP 1,500,000 / 1,605,767 |
| Cash position NSCF-2026 | `[Cash Position (Agreement Ccy)]` | about -1,743,892 |
| Budget lines over 10% | `[Over Budget Lines]` (no filters) | 3 |
| Admin share, CSSP-EST | `[Admin Share %]` filtered to CSSP-EST | 11.5% (over the 10% cap) |
| Admin share, all funders | `[Admin Share %]` (no filters) | 9.5% |
| Reach | `[Participants Reached]` (no filters) | 6,398 |
| Reach by programme | by `dim_programme[ProgrammeID]` | P02 48, P03 2,614, P04 505, P05 2,803, P06 428 |
| Attendances | `[Attendances]` | 73,775 |
| Overdue milestones | `[Milestones Overdue]` | 2 (M10, M11) |
| DQ issues | `[DQ Issues]` | 595 |
| Mixed currency guard | `[Spend (Agreement Ccy)]` with no filters | blank |
