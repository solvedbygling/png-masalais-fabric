"""
PNG Masalais (FICTIONAL CLUB, SYNTHETIC DATA)
Step 2: finance data.

Two legal entities, two accounting systems, two currencies:
  AU entity  "Masalais Foundation Ltd" (Australia)   books in AUD, Xero-style export (Debit/Credit columns)
  PNG entity "PNG Masalais Rugby League Club Inc"     books in PGK, signed-amount export

Outputs:
  data/fx/FX_AUD_PGK_Monthly.csv                    monthly average rates
  data/finance/budget/Masalais_Budget_2025-2026.xlsx  wide budget (months as columns)
  data/finance/gl_au/AU_GL_YYYY-MM.xlsx              one file per month (AUD)
  data/finance/gl_png/PNG_GL_YYYY-MM.xlsx            one file per month (PGK)
  data/_answer_key/finance_storylines.md             what was planted, so we can test the build finds it

Run 01_reference.py first.
"""
from datetime import date, timedelta
from pathlib import Path
import calendar
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

rng = np.random.default_rng(675)  # 675 = PNG country calling code, for a fixed, repeatable seed
ROOT = Path(__file__).resolve().parent.parent / "data"
REF = ROOT / "reference"
agreements = pd.read_csv(REF / "Agreements.csv", parse_dates=["StartDate", "EndDate"])
accounts = pd.read_csv(REF / "Accounts.csv", dtype={"AccountCode": str})
acct_name = dict(zip(accounts.AccountCode, accounts.AccountName))

REPORT_END = pd.Timestamp("2026-10-31")
MONTHS = pd.period_range("2025-07", "2026-12", freq="M")          # budget horizon
ACTUAL_MONTHS = [m for m in MONTHS if m.end_time <= REPORT_END + pd.Timedelta(days=1)]

# ------------------------------------------------------------------ FX
# PGK per 1 AUD, monthly average. Gentle PGK depreciation with noise.
fx_rate = {}
r = 2.63
for m in MONTHS:
    fx_rate[m] = round(r, 4)
    r += 0.008 + rng.normal(0, 0.012)
fx = pd.DataFrame({
    "Month": [m.start_time.date() for m in ACTUAL_MONTHS],
    "FromCurrency": "AUD", "ToCurrency": "PGK",
    "AvgRate": [fx_rate[m] for m in ACTUAL_MONTHS],
})
(ROOT / "fx").mkdir(parents=True, exist_ok=True)
fx.to_csv(ROOT / "fx" / "FX_AUD_PGK_Monthly.csv", index=False)

# ------------------------------------------------------------ Budget design
# Budget amount for the 2025-2026 plan, in agreement currency.
budget_total = {
    "CSSP-EST": 9_000_000, "NSCF-2025": 6_000_000, "NSCF-2026": 9_000_000,
    "TUM-PP": 2_000_000,   # 2026 half of a two-year deal
    "BST-FP25": 750_000, "BST-MP26": 1_800_000, "MVA-SCH": 600_000,
}
budget_window = {
    "CSSP-EST": ("2025-07", "2026-12"), "NSCF-2025": ("2025-07", "2025-12"),
    "NSCF-2026": ("2026-01", "2026-12"), "TUM-PP": ("2026-01", "2026-12"),
    "BST-FP25": ("2025-09", "2025-12"), "BST-MP26": ("2026-01", "2026-12"),
    "MVA-SCH": ("2025-10", "2026-12"),
}
prog_share = {
    "CSSP-EST": {"P01": .38, "P02": .14, "P03": .12, "P04": .10, "P05": .06, "P06": .10, "P99": .10},
    "NSCF-2025": {"P01": .70, "P05": .30},
    "NSCF-2026": {"P01": .65, "P05": .35},
    "TUM-PP": {"P01": .40, "P02": .30, "P99": .30},
    "BST-FP25": {"P02": .50, "P99": .50},
    "BST-MP26": {"P02": .40, "P04": .30, "P99": .30},
    "MVA-SCH": {"P03": 1.0},
}
cat_share = {
    "P01": {"Staff": .45, "Facilities": .30, "Equipment": .08, "Sports Science": .10, "Travel": .07},
    "P02": {"Staff": .40, "Travel": .20, "Equipment": .15, "Programme Delivery": .15, "Sports Science": .10},
    "P03": {"Staff": .40, "Programme Delivery": .35, "Equipment": .15, "Travel": .10},
    "P04": {"Staff": .35, "Programme Delivery": .30, "Travel": .20, "Equipment": .15},
    "P05": {"Travel": .45, "Staff": .25, "Programme Delivery": .20, "Equipment": .10},
    "P06": {"Programme Delivery": .50, "Travel": .25, "Staff": .15, "Professional Services": .10},
    "P99": {"Staff": .45, "Overheads": .55},
}
# Month each programme starts real delivery (establishment ramp-up).
prog_start = {"P01": "2025-07", "P02": "2025-11", "P03": "2025-10", "P04": "2026-02",
              "P05": "2025-09", "P06": "2025-09", "P99": "2025-07"}


def months_between(a, b):
    return [m for m in MONTHS if pd.Period(a, "M") <= m <= pd.Period(b, "M")]


def in_range(m, a, b):
    return pd.Period(a, "M") <= m <= pd.Period(b, "M")


def phase(ag, p, c, m, actual=False):
    """Relative monthly weight for a budget line. actual=True gives the delivered profile."""
    # Training base Stage 1 (CSSP): budgeted Oct 2025 to Mar 2026; really ran to Jun 2026.
    if (ag, p, c) == ("CSSP-EST", "P01", "Facilities"):
        end = "2026-06" if actual else "2026-03"
        return 1.0 if in_range(m, "2025-10", end) else 0.04
    # Training base Stage 2 gymnasium (PNG Govt 2026): Jul to Oct 2026.
    if (ag, p, c) == ("NSCF-2026", "P01", "Facilities"):
        return 1.0 if in_range(m, "2026-07", "2026-10") else 0.08
    if m < pd.Period(prog_start[p], "M"):
        return 0.0 if p not in ("P01", "P99") else 0.3
    w = 1.0
    if ag == "CSSP-EST":  # establishment ramp
        i = (m - pd.Period("2025-07", "M")).n
        w = min(1.0, 0.45 + 0.07 * i)
    if p == "P03" and m.month in (12, 1):  # PNG school holidays
        w *= 0.25
    if p in ("P04", "P05") and m.month in (12, 1):
        w *= 0.6
    return w


# Actual / budget multipliers per line (default about 0.97). The storylines live here.
def actual_factor(ag, p, c, m):
    special = {
        ("CSSP-EST", "P01", "Facilities"): 1.22,       # Stage 1 build overran
        ("NSCF-2026", "P05", "Travel"): 1.18,         # domestic airfares to provinces
        ("CSSP-EST", "P99", "Overheads"): 1.25,       # admin creep, breaches 10% cap
        ("CSSP-EST", "P99", "Staff"): 1.12,
        ("NSCF-2026", "P01", "Facilities"): 1.06,
    }
    if (ag, p, c) in special:
        return special[(ag, p, c)]
    if ag == "CSSP-EST" and p == "P03" and m < pd.Period("2026-04", "M"):
        return 0.55                                    # schools programme slow start
    if ag == "NSCF-2025":
        return 0.92                                    # year-end underspend
    return line_base[(ag, p, c)]


line_base = {}
rows = []
for ag, total in budget_total.items():
    win = months_between(*budget_window[ag])
    for p, ps in prog_share[ag].items():
        for c, cs in cat_share[p].items():
            line_base[(ag, p, c)] = float(np.clip(rng.normal(0.97, 0.035), 0.88, 1.06))
            weights = np.array([phase(ag, p, c, m) for m in win])
            weights = weights / weights.sum()
            line_amt = total * ps * cs
            for m, w in zip(win, weights):
                rows.append((ag, p, c, m, round(line_amt * w, 0)))
budget = pd.DataFrame(rows, columns=["AgreementID", "ProgrammeID", "CostCategory", "Month", "Budget"])
cur = dict(zip(agreements.AgreementID, agreements.Currency))
budget["Currency"] = budget.AgreementID.map(cur)

# ------------------------------------------------------- Budget workbook (wide)
wide = budget.pivot_table(index=["AgreementID", "ProgrammeID", "CostCategory", "Currency"],
                          columns="Month", values="Budget", aggfunc="sum", fill_value=0)
wide.columns = [m.strftime("%b %Y") for m in wide.columns]   # "Jul 2025" style headers
wide = wide.reset_index()
bdir = ROOT / "finance" / "budget"
bdir.mkdir(parents=True, exist_ok=True)
bfile = bdir / "Masalais_Budget_2025-2026.xlsx"
with pd.ExcelWriter(bfile, engine="openpyxl") as xw:
    wide.to_excel(xw, sheet_name="Budget", index=False, startrow=3)
wb = load_workbook(bfile)
ws = wb["Budget"]
ws["A1"] = "PNG Masalais (fictional) - Approved Budget 2025-2026, by funding agreement"
ws["A2"] = "Amounts in agreement currency. Board approved 30 June 2025. SYNTHETIC DATA."
ref = f"A4:{get_column_letter(wide.shape[1])}{wide.shape[0] + 4}"
t = Table(displayName="tblBudget", ref=ref)
t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
ws.add_table(t)
for i in range(1, wide.shape[1] + 1):
    ws.column_dimensions[get_column_letter(i)].width = 20 if i <= 3 else 11
    if i > 4:
        for r_ in range(5, wide.shape[0] + 5):
            ws.cell(r_, i).number_format = "#,##0"
wb.save(bfile)

# ------------------------------------------------------------ Actual spend
def accounts_for(p, c):
    """(account, share) for a programme/category."""
    if c == "Staff":
        sal = {"P01": "5100", "P99": "5120"}.get(p, "5110")
        return [(sal, .89), ("5130", .11)]
    if c == "Facilities":
        return [("5320", .80), ("5300", .20)] if p == "P01" else [("5300", 1.0)]
    if c == "Equipment":
        return [("5310", .6), ("5500", .4)] if p == "P01" else [("5500", 1.0)]
    if c == "Travel":
        if p in ("P01", "P02"):
            return [("5410", .45), ("5400", .25), ("5420", .30)]
        return [("5400", .60), ("5420", .40)]
    if c == "Programme Delivery":
        if p == "P06":
            return [("5510", .85), ("5800", .15)]
        return [("5520", .88), ("5800", .12)]
    if c == "Sports Science":
        return [("5600", 1.0)]
    if c == "Professional Services":
        return [("5200", 1.0)]
    if c == "Overheads":
        return [("5700", .25), ("5710", .35), ("5720", .35), ("5730", .05)]
    raise ValueError(c)


AU_PAID = {"5200", "5410", "5600"}  # Australian grant costs paid from the Australian entity

spend = []  # entity, agreement, programme, account, month, amount (entity currency)
for (ag, p, c), base in line_base.items():
    win = [m for m in months_between(*budget_window[ag]) if m in ACTUAL_MONTHS]
    if not win:
        continue
    full_win = months_between(*budget_window[ag])
    line_total = budget.query("AgreementID==@ag and ProgrammeID==@p and CostCategory==@c").Budget.sum()
    w_act = np.array([phase(ag, p, c, m, actual=True) for m in full_win])
    w_act = w_act / w_act.sum()
    for m, w in zip(full_win, w_act):
        if m not in ACTUAL_MONTHS:
            continue
        amt_ag = line_total * w * actual_factor(ag, p, c, m) * rng.normal(1, 0.06)
        for acct, s in accounts_for(p, c):
            a = amt_ag * s
            if ag == "CSSP-EST" and acct in AU_PAID:
                spend.append(("AU", ag, p, acct, m, a))
            else:
                a_pgk = a * fx_rate[m] if cur[ag] == "AUD" else a
                spend.append(("PNG", ag, p, acct, m, a_pgk))
spend = pd.DataFrame(spend, columns=["Entity", "AgreementID", "ProgrammeID", "AccountCode", "Month", "Amount"])

# --------------------------------------------------------------- Receipts
receipts = [  # entity, agreement, date, amount (agreement currency), account, narration
    ("AU", "CSSP-EST", "2025-07-22", 2_500_000, "4100", "CSSP tranche 1 - agreement signed (M01)"),
    ("AU", "CSSP-EST", "2025-11-20", 2_000_000, "4100", "CSSP tranche 2 - inception plan approved (M02)"),
    ("AU", "CSSP-EST", "2026-03-18", 1_500_000, "4100", "CSSP tranche 3 - staff recruited, academy intake (M03)"),
    ("AU", "CSSP-EST", "2026-07-09", 1_500_000, "4100", "CSSP tranche 4 - training base Stage 1 (M04)"),
    ("AU", "CSSP-EST", "2026-09-24", 1_000_000, "4100", "CSSP tranche 5 - mid-term report accepted (M05)"),
    ("PNG", "NSCF-2025", "2025-09-15", 3_000_000, "4110", "NSCF 2025 appropriation - release 1"),
    ("PNG", "NSCF-2025", "2025-12-10", 3_000_000, "4110", "NSCF 2025 appropriation - release 2"),
    ("PNG", "NSCF-2026", "2026-03-25", 4_500_000, "4110", "NSCF 2026 appropriation - release 1"),
    ("PNG", "NSCF-2026", "2026-10-20", 2_000_000, "4110", "NSCF 2026 appropriation - release 2 (part payment)"),
    ("PNG", "BST-FP25", "2025-09-20", 375_000, "4200", "Bismarck Sea Telecom foundation partner - instalment 1"),
    ("PNG", "BST-FP25", "2025-12-05", 375_000, "4200", "Bismarck Sea Telecom foundation partner - instalment 2"),
    ("PNG", "BST-MP26", "2026-02-12", 450_000, "4200", "Bismarck Sea Telecom major partner - Q1"),
    ("PNG", "BST-MP26", "2026-05-14", 450_000, "4200", "Bismarck Sea Telecom major partner - Q2"),
    ("PNG", "BST-MP26", "2026-08-13", 450_000, "4200", "Bismarck Sea Telecom major partner - Q3"),
    ("PNG", "TUM-PP", "2026-01-30", 500_000, "4200", "Tumbuna Resources principal partner - Q1 2026"),
    ("PNG", "TUM-PP", "2026-04-28", 500_000, "4200", "Tumbuna Resources principal partner - Q2 2026"),
    ("PNG", "TUM-PP", "2026-10-05", 500_000, "4200", "Tumbuna Resources principal partner - Q3 2026 (paid late)"),
    ("PNG", "MVA-SCH", "2025-10-14", 120_000, "4200", "Markham Valley Agri schools partner - instalment 1"),
    ("PNG", "MVA-SCH", "2026-01-21", 120_000, "4200", "Markham Valley Agri schools partner - instalment 2"),
    ("PNG", "MVA-SCH", "2026-04-16", 120_000, "4200", "Markham Valley Agri schools partner - instalment 3"),
    ("PNG", "MVA-SCH", "2026-07-15", 120_000, "4200", "Markham Valley Agri schools partner - instalment 4"),
    ("PNG", "MVA-SCH", "2026-10-13", 120_000, "4200", "Markham Valley Agri schools partner - instalment 5"),
]

# ------------------------------------------------------- GL line generation
provinces = pd.read_csv(REF / "Provinces.csv").ProvinceName.tolist()
templates = {
    "5100": ["High performance staff payroll", "HP coaching staff salaries"],
    "5110": ["Programme staff payroll", "Development officers salaries"],
    "5120": ["Administration staff payroll", "Club office salaries"],
    "5130": ["Superannuation and payroll on-costs"],
    "5200": ["Contract services - {v}", "Consultancy - {v}"],
    "5300": ["Ground hire and maintenance", "Field maintenance - {p}"],
    "5320": ["Training base works - progress claim", "Training base works - variation"],
    "5310": ["Gym equipment purchase", "Strength and conditioning equipment"],
    "5500": ["Balls, cones and tackle bags", "Playing kit and apparel"],
    "5400": ["Domestic flights - {p}", "Vehicle hire and fuel - {p}", "PMV and boat transport - {p}"],
    "5410": ["International flights - squad camp", "International flights - staff"],
    "5420": ["Accommodation and meals - {p}", "Camp accommodation and catering"],
    "5510": ["Coaching accreditation course - {p}", "Referee course materials"],
    "5520": ["School gala day - {p}", "Community clinic costs - {p}", "Session catering and water - {p}"],
    "5800": ["Safeguarding training", "Working with children checks"],
    "5600": ["Sports science services", "Physiotherapy and medical support"],
    "5700": ["Insurance premium"], "5710": ["Internet and mobile", "Software subscriptions"],
    "5720": ["External audit fee", "Legal advice - agreements", "Bookkeeping services"],
    "5730": ["Bank fees"],
}
vendors = ["sports performance consultant", "facilities project manager", "M&E consultant",
           "coach educator", "governance adviser"]
PAYROLL = {"5100", "5110", "5120", "5130"}


def narr(acct):
    t = rng.choice(templates[acct])
    return t.format(p=rng.choice(provinces), v=rng.choice(vendors))


def rand_day(m):
    return date(m.year, m.month, int(rng.integers(1, calendar.monthrange(m.year, m.month)[1] + 1)))


lines = []
for row in spend.itertuples():
    m = row.Month
    if row.AccountCode in PAYROLL:  # fortnightly pays
        splits = [0.5, 0.5]
        days = [date(m.year, m.month, 14), date(m.year, m.month, 28)]
    else:
        n = int(rng.integers(1, 5))
        splits = rng.dirichlet(np.ones(n))
        days = [rand_day(m) for _ in range(n)]
    for s, d in zip(splits, days):
        amt = round(row.Amount * s, 2)
        if abs(amt) < 1:
            continue
        lines.append(dict(Entity=row.Entity, Date=d, AccountCode=row.AccountCode,
                          ProgrammeID=row.ProgrammeID, AgreementID=row.AgreementID,
                          Amount=amt, Narration=narr(row.AccountCode)))
for ent, ag, d, amt, acct, n in receipts:
    lines.append(dict(Entity=ent, Date=date.fromisoformat(d), AccountCode=acct, ProgrammeID="",
                      AgreementID=ag, Amount=-float(amt), Narration=n))  # income is a credit
for m in ACTUAL_MONTHS:  # small interest income in both banks
    last = date(m.year, m.month, calendar.monthrange(m.year, m.month)[1])
    lines.append(dict(Entity="AU", Date=last, AccountCode="4900", ProgrammeID="", AgreementID="",
                      Amount=-round(rng.uniform(1500, 6000), 2), Narration="Bank interest"))
    lines.append(dict(Entity="PNG", Date=last, AccountCode="4900", ProgrammeID="", AgreementID="",
                      Amount=-round(rng.uniform(4000, 15000), 2), Narration="Bank interest"))
gl = pd.DataFrame(lines).sort_values(["Entity", "Date", "AccountCode"]).reset_index(drop=True)

# ----------------------------------------------------- Plant data quality issues
png_exp = gl.index[(gl.Entity == "PNG") & gl.AccountCode.str.startswith("5")]
dq_blank_cc = rng.choice(png_exp, size=int(len(png_exp) * 0.008), replace=False)
gl.loc[dq_blank_cc, "ProgrammeID"] = ""
remaining = np.setdiff1d(png_exp, dq_blank_cc)
dq_fund = rng.choice(remaining, size=int(len(png_exp) * 0.02), replace=False)
gl.loc[dq_fund, "AgreementID"] = [rng.choice([a.lower(), a.replace("-", " "), a + " "])
                                  for a in gl.loc[dq_fund, "AgreementID"]]
remaining = np.setdiff1d(remaining, dq_fund)
dq_susp = rng.choice(remaining, size=6, replace=False)
gl.loc[dq_susp, "AccountCode"] = "5999"
acct_name["5999"] = "Suspense - Unallocated"

# ----------------------------------------------------------------- Write GL
au_dir, png_dir = ROOT / "finance" / "gl_au", ROOT / "finance" / "gl_png"
au_dir.mkdir(parents=True, exist_ok=True)
png_dir.mkdir(parents=True, exist_ok=True)


def save_table(df, path, title_lines, table_name):
    start = len(title_lines) + 1
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="GL", index=False, startrow=start)
    wb_ = load_workbook(path)
    ws_ = wb_["GL"]
    for i, t_ in enumerate(title_lines, 1):
        ws_.cell(i, 1, t_)
    tbl = Table(displayName=table_name,
                ref=f"A{start + 1}:{get_column_letter(df.shape[1])}{start + 1 + len(df)}")
    tbl.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showRowStripes=True)
    ws_.add_table(tbl)
    for i, col in enumerate(df.columns, 1):
        ws_.column_dimensions[get_column_letter(i)].width = 48 if col in ("Description", "Narration") else 16
    wb_.save(path)


au_seq, png_seq = 1000, 5000
au_months = {}
for m in ACTUAL_MONTHS:
    mstart, mend = m.start_time.date(), m.end_time.date()
    # AU: Xero-style
    a = gl[(gl.Entity == "AU") & (gl.Date >= mstart) & (gl.Date <= mend)].copy()
    au = pd.DataFrame({
        "Date": [d.strftime("%d/%m/%Y") for d in a.Date],
        "Journal": [f"AUJ-{au_seq + i:05d}" for i in range(len(a))],
        "Account Code": a.AccountCode.values,
        "Account": [acct_name[x] for x in a.AccountCode],
        "Description": a.Narration.values,
        "Tracking - Programme": a.ProgrammeID.values,
        "Tracking - Fund": a.AgreementID.values,
        "Debit (AUD)": [x if x > 0 else None for x in a.Amount],
        "Credit (AUD)": [-x if x < 0 else None for x in a.Amount],
    })
    au_seq += len(a)
    au_months[m] = au
    # PNG: signed amount
    p_ = gl[(gl.Entity == "PNG") & (gl.Date >= mstart) & (gl.Date <= mend)].copy()
    png = pd.DataFrame({
        "TxnDate": p_.Date.values,
        "Ref": [f"PV{m.year % 100}-{png_seq + i:05d}" for i in range(len(p_))],
        "GLAccount": p_.AccountCode.values,
        "Narration": p_.Narration.values,
        "CostCentre": p_.ProgrammeID.values,
        "FundCode": p_.AgreementID.values,
        "Amount": p_.Amount.values,
    })
    png_seq += len(p_)
    save_table(png, png_dir / f"PNG_GL_{m.strftime('%Y-%m')}.xlsx",
               [f"PNG Masalais Rugby League Club Inc - General Ledger export {m.strftime('%B %Y')}",
                "Currency: PGK. Debits positive, credits negative. SYNTHETIC DATA."], "tblGL")

# Planted overlap: the March 2026 AU export repeats the last 15 lines of February.
feb, mar = pd.Period("2026-02", "M"), pd.Period("2026-03", "M")
au_months[mar] = pd.concat([au_months[feb].tail(15), au_months[mar]], ignore_index=True)
for m, au in au_months.items():
    save_table(au, au_dir / f"AU_GL_{m.strftime('%Y-%m')}.xlsx",
               [f"Masalais Foundation Ltd - Account Transactions {m.strftime('%B %Y')}",
                "Currency: AUD. SYNTHETIC DATA."], "tblGL")

# ------------------------------------------------------------- Self-check
fxm = {m: fx_rate[m] for m in ACTUAL_MONTHS}
spend["AmtAgCur"] = [
    (r_.Amount / fxm[r_.Month]) if (cur[r_.AgreementID] == "AUD" and r_.Entity == "PNG") else r_.Amount
    for r_ in spend.itertuples()]
spend["CostCategory"] = spend.AccountCode.map(dict(zip(accounts.AccountCode, accounts.CostCategory)))
act = spend.groupby(["AgreementID", "ProgrammeID", "CostCategory"]).AmtAgCur.sum()
bud = budget[budget.Month.isin(ACTUAL_MONTHS)].groupby(["AgreementID", "ProgrammeID", "CostCategory"]).Budget.sum()
var = pd.DataFrame({"BudgetYTD": bud, "ActualYTD": act}).fillna(0)
var["VarPct"] = (var.ActualYTD / var.BudgetYTD - 1).round(3)
flags = var[var.VarPct > 0.10]

rec = pd.DataFrame(receipts, columns=["Entity", "AgreementID", "Date", "Amount", "Acct", "N"]).groupby("AgreementID").Amount.sum()
spent = spend.groupby("AgreementID").AmtAgCur.sum()
summary = pd.DataFrame({"Committed": agreements.set_index("AgreementID").CommittedAmount,
                        "Received": rec, "SpentToOct": spent.round(0)}).fillna(0)
cssp_admin = spend.query("AgreementID=='CSSP-EST' and ProgrammeID=='P99'").AmtAgCur.sum()
cssp_total = spend.query("AgreementID=='CSSP-EST'").AmtAgCur.sum()

key = ROOT / "_answer_key"
key.mkdir(exist_ok=True)
with open(key / "finance_storylines.md", "w") as f:
    f.write("# Finance storylines planted in the synthetic data (answer key)\n\n")
    f.write("## Funding position to 31 Oct 2026 (agreement currency)\n\n")
    f.write(summary.to_markdown() + "\n\n")
    f.write(f"CSSP admin share of spend: {cssp_admin / cssp_total:.1%} (cap 10%)\n\n")
    f.write("## Budget lines more than 10% over, year to date\n\n")
    f.write(flags.to_markdown() + "\n\n")
    f.write("## Planted data quality issues\n\n")
    f.write(f"- PNG expense lines with blank CostCentre: {len(dq_blank_cc)}\n")
    f.write(f"- PNG lines with non-standard FundCode: {len(dq_fund)}\n")
    f.write("- PNG lines posted to suspense account 5999 (not in chart of accounts): 6\n")
    f.write("- AU_GL_2026-03.xlsx repeats the last 15 lines of February (export overlap)\n")

print(summary)
print(f"\nCSSP admin share: {cssp_admin / cssp_total:.1%}")
print("\nLines >10% over:\n", flags)
print(f"\nGL rows: AU {sum(len(v) for v in au_months.values())}, PNG {(gl.Entity == 'PNG').sum()}")
print(f"DQ: blank CC {len(dq_blank_cc)}, fund variants {len(dq_fund)}, suspense 6, AU dup 15")
