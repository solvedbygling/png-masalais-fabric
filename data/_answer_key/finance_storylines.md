# Finance storylines planted in the synthetic data (answer key)

## Funding position to 31 Oct 2026 (agreement currency)

| AgreementID   |    Committed |      Received |       SpentToOct |
|:--------------|-------------:|--------------:|-----------------:|
| BST-FP25      | 750000       | 750000        | 724042           |
| BST-MP26      |      1.8e+06 |      1.35e+06 |      1.4798e+06  |
| CSSP-EST      |      9e+06   |      8.5e+06  |      8.01456e+06 |
| MVA-SCH       | 600000       | 600000        | 543487           |
| NSCF-2025     |      6e+06   |      6e+06    |      5.56934e+06 |
| NSCF-2026     |      9e+06   |      6.5e+06  |      8.24389e+06 |
| TUM-PP        |      4e+06   |      1.5e+06  |      1.60577e+06 |

CSSP admin share of spend: 11.6% (cap 10%)

## Budget lines more than 10% over, year to date

|                                   |        BudgetYTD |        ActualYTD |   VarPct |
|:----------------------------------|-----------------:|-----------------:|---------:|
| ('CSSP-EST', 'P01', 'Facilities') |      1.01333e+06 |      1.2603e+06  |    0.244 |
| ('CSSP-EST', 'P99', 'Overheads')  | 431373           | 540912           |    0.254 |
| ('CSSP-EST', 'P99', 'Staff')      | 352944           | 389012           |    0.102 |
| ('NSCF-2026', 'P05', 'Travel')    |      1.215e+06   |      1.43595e+06 |    0.182 |

## Planted data quality issues

- PNG expense lines with blank CostCentre: 28
- PNG lines with non-standard FundCode: 71
- PNG lines posted to suspense account 5999 (not in chart of accounts): 6
- AU_GL_2026-03.xlsx repeats the last 15 lines of February (export overlap)
