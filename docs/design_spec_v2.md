# Masalais Board Pack: design v2 (restyle)

**PNG Masalais (fictional club, synthetic data).** Restyles the existing 7-page report to the approved mockup
`docs/mockups/Masalais_Page1_Mockup.png`. **Look at that image before starting and compare your result against it.**

Agent instructions:
- Part A goes to the semantic model `SM_Masalais_Board` in workspace `PNG Masalais` via the modeling MCP.
- Parts B to D go to `report/Masalais_Board_Pack.Report`. Power BI Desktop must be closed.
- **Keep the existing positions and sizes on pages 2 to 7.** The owner adjusted them by hand in Desktop. Restyle only,
  except where this spec says to move something. Page 1 is rebuilt to the mockup.
- Replace the theme with `docs/masalais_theme_v2.json`.
- Images: register `PNG Masalais Rugby Logo.png` (project root) and every file in `assets/icons/` as report resources.
- Validate at the end. Report anything you could not do exactly, and what you did instead.

---

## A. Semantic model additions (display folder `Card Text`, home table `fact_gl` unless stated)

**Funding Context** (text)
```dax
VAR f = COUNTROWS ( FILTER ( VALUES ( dim_agreement[FunderID] ), [Funding Received AUD] > 0 ) )
VAR a = COUNTROWS ( FILTER ( VALUES ( dim_agreement[AgreementID] ), [Funding Received AUD] > 0 ) )
RETURN "from " & f & " funders, " & a & " agreements"
```

**Spend Context** (text)
```dax
VAR v = [Variance to Date %]
RETURN FORMAT ( ABS ( v ), "0.0%" ) & IF ( v >= 0, " over", " under" ) & " budget to date"
```

**People Context** (text, home `fact_attendance`)
```dax
FORMAT ( [Attendances], "#,0" ) & " attendances"
```

**Female Context** (text, home `fact_attendance`): overall female share compared with the first month of delivery.
```dax
VAR firstDay = CALCULATE ( MIN ( fact_attendance[SessionDate] ), REMOVEFILTERS ( dim_date ) )
VAR monthStart = DATE ( YEAR ( firstDay ), MONTH ( firstDay ), 1 )
VAR startPct = CALCULATE ( [Female Participation %], REMOVEFILTERS ( dim_date ),
                           DATESBETWEEN ( dim_date[Date], monthStart, EOMONTH ( firstDay, 0 ) ) )
VAR nowPct = [Female Participation %]
RETURN IF ( nowPct >= startPct, "▲ up", "▼ down" ) & " from " & FORMAT ( startPct, "0%" ) & " in " & FORMAT ( firstDay, "mmm yyyy" )
```

**Female Context Colour** (text): `IF ( [Female Participation %] >= <startPct as above>, "#2F7D4F", "#C8102E" )`
(reuse the same variables).

**Milestones Context** (text, home `dim_milestone`): `"of " & [Milestones] & " milestones"`

**Budget Lines Context** (text, home `fact_budget`)
```dax
"of " & COUNTROWS ( SUMMARIZE ( fact_budget, dim_agreement[AgreementID], dim_programme[ProgrammeID], dim_cost_category[CostCategory] ) ) & " budget lines"
```

**Spend Bar Colour** (text): red only where **restricted** money has been overspent against receipts.
Unrestricted sponsorship running slightly ahead of quarterly payments is normal and stays charcoal.
```dax
VAR gap = CALCULATE ( [Spend AUD] - [Funding Received AUD], dim_agreement[Restriction] = "Restricted" )
RETURN IF ( gap > 0, "#C8102E", "#2F2F2F" )
```

Validation: Funding Context = "from 5 funders, 7 agreements"; Spend Context = "0.2% over budget to date";
People Context = "73,775 attendances"; Female Context = "▲ up from 30% in Sep 2025" (approximately);
Milestones Context = "of 12 milestones"; Budget Lines Context = "of 80 budget lines";
Spend Bar Colour by funder: red only for "PNG National Sport and Community Fund".

---

## B. Design system (all pages)

| Token | Colour | Use |
|---|---|---|
| Ink | `#1B1B1B` | Header band |
| Charcoal | `#2F2F2F` | Main text, "actual/spent" series, table headers |
| Mid grey | `#8C8C8C` | Secondary text, axis labels |
| Line grey | `#E9E9E9` | Borders, gridlines |
| Page | `#F4F4F3` | Page background |
| Gold | `#F2A900` | Brand accent, "received/budget/target" series, badges |
| Gold tint | `#FBF1D6` | Icon tiles, "Watch" pills (text `#9A6B00`) |
| Red | `#C8102E` | **Warnings only**: overdue, over budget, restricted overspend |
| Red tint | `#FBE5E8` | Warning icon tiles, "Risk" pills |
| Green | `#2F7D4F` | Positive change text only |

Rules: red never decorates; it only marks a problem. Gold means "plan / funding / brand". Charcoal means "actual".
Segoe UI everywhere. Visual titles 14 pt semibold charcoal, left-aligned. Manual subtitles in 10 pt mid grey
(automatic subtitles off). Data labels on for bar and column charts. Light gridlines only. Legends top right.

### Header (every page)
- Rectangle x 0, y 0, w 1280, h 84, fill Ink, no border, no shadow.
- Logo image (PNG Masalais Rugby Logo.png) x 18, y 6, w 108, h 72, transparent background, no border.
- Vertical divider: rectangle x 140, y 20, w 1, h 44, fill `#444444`.
- Title text box x 158, y 14, w 820, h 36: the page name, Segoe UI Bold 22, white.
- Subtitle text box x 158, y 50, w 820, h 22: "Board pack | As at 31 October 2026 | PNG Masalais (fictional club, synthetic data)", Segoe UI 10, `#B5B5B5`.
- Right side: on pages **without** a slicer, a rounded rectangle x 1040, y 26, w 216, h 32 (radius 16, no fill,
  border `#555555`) with centred text "Period: Jul 2025 to Oct 2026", 10 pt, `#E0E0E0`.
  On pages **with** a slicer (2 and 4), move the slicer here instead: x 1040, y 18, w 216, h 50, dropdown style,
  header text white 9 pt, dropdown background `#2F2F2F`, text white, border `#555555`.
- Accent line under the band: rectangle x 0, y 84, w 1050, h 3 gold; rectangle x 1050, y 84, w 230, h 3 red.
- Delete the old green band, old accent bar and any leftover header objects.
- Content starts at y 100 (move every page 2 to 7 visual down by the difference if it overlaps, keeping relative layout).

### KPI cards (all pages with KPI rows)
Target look, as in the mockup: white card, radius 10, light border and shadow, a 40 x 40 icon tile at top left
(x+14, y+16), title to the right of the icon (11.5 pt mid grey), value under the title (24 pt bold), and a context line
along the bottom (11 pt mid grey, or a measure-driven colour).
Build it with whatever is cleanest in PBIR: the new Card visual with image and reference label if supported,
otherwise a background shape plus an image visual plus a transparent card plus a text card for the context line.
Values with a problem (Milestones Overdue > 0, Over Budget Lines > 0, Admin Share % > 10%) use red font.

Number formats on cards: counts in full (6,398); AUD over $1M as `$#,0.0,,"M"` ($14.8M); AUD under $1M in full; percentages 0.0%.

### Tables and matrices
Column header band charcoal with white semibold text (from theme), alternating rows `#FAFAF9`, no vertical gridlines,
light horizontal lines. Status colours by text or rule:
- Risk / Red / over 10%: background red, white bold text
- Watch / Amber / 0 to 10% over: background gold tint, text `#9A6B00`
- Green: background green, white text
- Complete: background `#E9E9E9`, text charcoal

---

## C. Page 1: Where do we stand? (rebuild to the mockup)

Positions are for a 1280 x 720 canvas.

**KPI row** (y 104, h 100, w 192, gap 16, first x 24):
| # | Icon | Title | Value measure | Context line |
|---|---|---|---|---|
| 1 | icon-funding | Funding received | Funding Received AUD | Funding Context |
| 2 | icon-spend | Spent | Spend AUD | Spend Context |
| 3 | icon-people | People reached | Participants Reached | People Context |
| 4 | icon-female | Female participation | Female Participation % | Female Context (colour from Female Context Colour) |
| 5 | icon-milestone-overdue | Milestones overdue | Milestones Overdue (red) | Milestones Context |
| 6 | icon-over-budget | Lines >10% over | Over Budget Lines (red) | Budget Lines Context |

**Funder chart** (card x 24, y 220, w 616, h 262): clustered bar.
Title "Funding received vs spent, by funder"; manual subtitle "AUD, 1 Jul 2025 to 31 Oct 2026".
Y axis dim_agreement[FunderName] (no axis title), values Funding Received AUD (gold) and Spend AUD.
Spend AUD bar colour by field value **Spend Bar Colour** (red only for the PNG government funding).
Data labels on, `$#,0.00,,"M"`; Spend label colour also by Spend Bar Colour. Legend top right: "Received", "Spent"
(rename the series display names). Sort by Spend AUD descending. No X axis, no gridlines.

**Monthly chart** (card x 656, y 220, w 600, h 262): line and clustered column.
Title "Monthly spending vs budget"; subtitle "AUD". X dim_date[MonthName]; columns Spend AUD (charcoal); line Budget AUD
(gold, 2.5 px, markers on, white fill). Visual filter IsActual = True and IsEstablishmentPeriod = True.
Data label only on the last line point if possible; otherwise none. Legend top right "Spent", "Budget".
Y axis `$#,0.0,,"M"` with light gridlines.

**For the board's attention** (card x 24, y 496, w 1232, h 212): static, built from shapes and text boxes to match the mockup.
- Title text 14 pt semibold.
- Header band: rounded rectangle x 44, y 536, w 1192, h 26, fill charcoal, with white 10 pt semibold labels
  "#" (x 66), "Issue" (x 96), "What the board needs to know" (x 268), "Status" (x 1080), "See" (x 1160).
- Four rows, 34 px each, starting y 566, alternating row fill `#FAFAF9` on rows 2 and 4. Each row: gold circle (r 10)
  with a white bold number at x 70; Issue (12 pt semibold); detail (11 pt); status pill (rounded rectangle 56 x 18,
  radius 9); page reference (11 pt mid grey).

| # | Issue | What the board needs to know | Status | See |
|---|---|---|---|---|
| 1 | Bridging finance | PNG Government 2026 funding: PGK 6.5m received, PGK 8.2m spent. The club is covering a PGK 1.7m gap from sponsor funds. | Risk | Page 2 |
| 2 | Budget overruns | Three lines are more than 10% over: training base Stage 1 and Australian grant overheads (both +24%), clinic travel (+18%). | Risk | Page 3 |
| 3 | Admin cap | Administration is 11.5% of Australian grant spending, above the 10% cap in the agreement. | Watch | Page 3 |
| 4 | Overdue milestones | Provincial clinics (13 of 15 provinces) and the gymnasium (now expected late November). | Watch | Page 6 |

If possible, make each "Page n" text a page navigation link to that page.

---

## D. Pages 2 to 7: restyle (keep positions)

**Page 2**: slicer into the header (B). Agreements table and matrix get the table style. Cash Position red font if < 0
(keep). Restricted vs unrestricted bars: charcoal, data labels on.

**Page 3**: matrix table style; variance colours per B (red over 10%, gold tint 0 to 10%). Admin share card in KPI style
with icon-over-budget, red value if > 10%. Variance by category columns: red where Variance to Date AUD > 0, charcoal
otherwise, data labels on. The two data-quality cards in KPI style (icon-dq-flagged), titles "No cost centre" and
"Suspense account".

**Page 4**: slicer into the header. KPI cards with icons: People reached (icon-people), Attendances (icon-attendances),
Sessions (icon-sessions), Schools (icon-schools), Provinces (icon-provinces), Cost per person reached (icon-cost).
Programme bars charcoal; female participation line gold; age band stack Female gold, Male charcoal; province bars charcoal.

**Page 5**: line chart: Programme schools gold, Comparison schools charcoal. Before vs after columns: Before joining
mid grey, After joining gold, Comparison school charcoal (colour by category), data labels on. "How to read this" box
in card style. Schools card in KPI style (icon-schools).

**Page 6**: KPI cards with icons: Milestones (icon-milestones), Complete (icon-complete), Completed late (icon-late),
Overdue (icon-milestone-overdue, red value). Milestone tracker table style; RAG colours per B. "Not yet earned" table
same style. Explanation text in card style.

**Page 7**: KPI cards with icons: Issues found (icon-dq-issues), Removed (icon-dq-removed), Corrected (icon-dq-corrected),
Flagged or quarantined (icon-dq-flagged). Table style. Rules text box in card style. Two spend cards in KPI style
(icon-dq-flagged).
