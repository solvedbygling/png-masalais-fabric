"""
PNG Masalais (FICTIONAL CLUB, SYNTHETIC DATA)
Step 1: reference lists that every other dataset hangs off.

Outputs:
  data/reference/*.csv                       one CSV per list (for the repo / lakehouse)
  data/reference/Masalais_Reference_Lists.xlsx   one formatted Excel table per sheet,
                                                 ready for SharePoint "Create list > From Excel"
"""
from datetime import date
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

OUT = Path(__file__).resolve().parent.parent / "data" / "reference"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- Funders
funders = pd.DataFrame([
    ("F01", "Coral Sea Sport Partnership", "Bilateral donor", "Australia"),
    ("F02", "PNG National Sport and Community Fund", "Host government", "Papua New Guinea"),
    ("F03", "Tumbuna Resources Ltd", "Corporate sponsor", "Papua New Guinea"),
    ("F04", "Bismarck Sea Telecom", "Corporate sponsor", "Papua New Guinea"),
    ("F05", "Markham Valley Agri Ltd", "Corporate sponsor", "Papua New Guinea"),
], columns=["FunderID", "FunderName", "FunderType", "Country"])

# ------------------------------------------------------------- Agreements
# AgreementID doubles as the FUND CODE on every GL line.
agreements = pd.DataFrame([
    ("CSSP-EST", "F01", "Establishment Phase Grant", "AUD", 9_000_000,
     date(2025, 7, 1), date(2026, 12, 31), "Restricted",
     "All programmes; governance and admin capped at 10% of grant", "Milestone tranches"),
    ("NSCF-2025", "F02", "2025 Appropriation", "PGK", 6_000_000,
     date(2025, 7, 1), date(2025, 12, 31), "Restricted",
     "High performance staff and facilities; provincial clinics", "Budget release"),
    ("NSCF-2026", "F02", "2026 Appropriation", "PGK", 9_000_000,
     date(2026, 1, 1), date(2026, 12, 31), "Restricted",
     "High performance staff and facilities; provincial clinics", "Budget release"),
    ("TUM-PP", "F03", "Principal Partner 2026-2027", "PGK", 4_000_000,
     date(2026, 1, 1), date(2027, 12, 31), "Unrestricted", "", "Quarterly instalments"),
    ("BST-FP25", "F04", "Foundation Partner 2025", "PGK", 750_000,
     date(2025, 9, 1), date(2025, 12, 31), "Unrestricted", "", "Quarterly instalments"),
    ("BST-MP26", "F04", "Major Partner 2026 (renewal)", "PGK", 1_800_000,
     date(2026, 1, 1), date(2026, 12, 31), "Unrestricted", "", "Quarterly instalments"),
    ("MVA-SCH", "F05", "Schools Programme Partner", "PGK", 600_000,
     date(2025, 10, 1), date(2026, 12, 31), "Restricted",
     "Schools Rugby League programme only", "Quarterly instalments"),
], columns=["AgreementID", "FunderID", "AgreementName", "Currency", "CommittedAmount",
            "StartDate", "EndDate", "Restriction", "RestrictionNotes", "PaymentBasis"])

# ------------------------------------------------------------- Programmes
programmes = pd.DataFrame([
    ("P01", "High Performance Staff and Facilities", "High Performance", "No"),
    ("P02", "Academy", "Pathway", "Yes"),
    ("P03", "Schools Rugby League", "Community", "Yes"),
    ("P04", "Women's and Girls' Pathways", "Pathway", "Yes"),
    ("P05", "Provincial Clinics", "Community", "Yes"),
    ("P06", "Coach and Match Official Development", "Capability", "Yes"),
    ("P99", "Governance and Administration", "Administration", "No"),
], columns=["ProgrammeID", "ProgrammeName", "Stream", "IsParticipantBased"])

# ------------------------------------------------------ Chart of accounts
accounts = pd.DataFrame([
    ("4100", "Grant Income - Bilateral Donor", "Revenue", "Grant Income"),
    ("4110", "Grant Income - Government", "Revenue", "Grant Income"),
    ("4200", "Sponsorship Income", "Revenue", "Sponsorship Income"),
    ("4900", "Interest Income", "Revenue", "Other Income"),
    ("5100", "Salaries - High Performance Staff", "Expense", "Staff"),
    ("5110", "Salaries - Programme Staff", "Expense", "Staff"),
    ("5120", "Salaries - Administration Staff", "Expense", "Staff"),
    ("5130", "Superannuation and On-costs", "Expense", "Staff"),
    ("5200", "Contractors and Consultants", "Expense", "Professional Services"),
    ("5300", "Facility Hire and Ground Maintenance", "Expense", "Facilities"),
    ("5320", "Training Base Works", "Expense", "Facilities"),
    ("5310", "Gym and Training Equipment", "Expense", "Equipment"),
    ("5500", "Rugby Equipment and Apparel", "Expense", "Equipment"),
    ("5400", "Domestic Travel", "Expense", "Travel"),
    ("5410", "International Travel", "Expense", "Travel"),
    ("5420", "Accommodation and Meals", "Expense", "Travel"),
    ("5510", "Coaching Courses and Resources", "Expense", "Programme Delivery"),
    ("5520", "School and Community Event Costs", "Expense", "Programme Delivery"),
    ("5800", "Safeguarding and Compliance", "Expense", "Programme Delivery"),
    ("5600", "Medical and Sports Science", "Expense", "Sports Science"),
    ("5700", "Insurance", "Expense", "Overheads"),
    ("5710", "IT and Communications", "Expense", "Overheads"),
    ("5720", "Audit, Legal and Accounting", "Expense", "Overheads"),
    ("5730", "Bank Fees", "Expense", "Overheads"),
], columns=["AccountCode", "AccountName", "AccountType", "CostCategory"]).sort_values("AccountCode")

# -------------------------------------------------------------- Provinces
# Real PNG provincial-level divisions (geography, not a brand).
provinces = pd.DataFrame([
    ("SHP", "Southern Highlands", "Highlands"), ("HEL", "Hela", "Highlands"),
    ("ENG", "Enga", "Highlands"), ("WHP", "Western Highlands", "Highlands"),
    ("JIW", "Jiwaka", "Highlands"), ("SIM", "Simbu", "Highlands"),
    ("EHP", "Eastern Highlands", "Highlands"),
    ("MOR", "Morobe", "Momase"), ("MAD", "Madang", "Momase"),
    ("ESP", "East Sepik", "Momase"), ("SAN", "West Sepik (Sandaun)", "Momase"),
    ("WES", "Western", "Southern"), ("GUL", "Gulf", "Southern"),
    ("CEN", "Central", "Southern"), ("NCD", "National Capital District", "Southern"),
    ("MBP", "Milne Bay", "Southern"), ("ORO", "Oro (Northern)", "Southern"),
    ("MAN", "Manus", "Islands"), ("NIP", "New Ireland", "Islands"),
    ("ENB", "East New Britain", "Islands"), ("WNB", "West New Britain", "Islands"),
    ("ARB", "Bougainville", "Islands"),
], columns=["ProvinceCode", "ProvinceName", "Region"])

# ------------------------------------------------------------- Milestones
# TrancheAmount = money released when the milestone is met (agreement currency).
# DueDate is the CONTRACTED date. Actual completion comes later from status updates.
milestones = pd.DataFrame([
    # Coral Sea Sport Partnership (AUD 9.0m in six tranches)
    ("M01", "CSSP-EST", "P99", "Grant agreement signed", date(2025, 7, 15), 2_500_000, "Tranche trigger"),
    ("M02", "CSSP-EST", "P99", "Inception plan and safeguarding policy approved", date(2025, 10, 31), 2_000_000, "Tranche trigger"),
    ("M03", "CSSP-EST", "P01", "Head coach and HP staff recruited; first academy intake", date(2026, 2, 28), 1_500_000, "Tranche trigger"),
    ("M04", "CSSP-EST", "P01", "Training base Stage 1 complete", date(2026, 3, 31), 1_500_000, "Tranche trigger"),
    ("M05", "CSSP-EST", "P99", "Mid-term progress and financial acquittal report", date(2026, 8, 31), 1_000_000, "Tranche trigger"),
    ("M06", "CSSP-EST", "P99", "Final establishment report", date(2026, 12, 15), 500_000, "Tranche trigger"),
    # Programme delivery milestones (no money attached, but funders track them)
    ("M07", "CSSP-EST", "P03", "Schools programme live in 40 schools", date(2026, 3, 31), 0, "Delivery"),
    ("M08", "CSSP-EST", "P04", "Women's pathway launched in 4 regions", date(2026, 5, 31), 0, "Delivery"),
    ("M09", "CSSP-EST", "P06", "All active coaches safeguarding-trained", date(2026, 6, 30), 0, "Compliance"),
    ("M10", "NSCF-2026", "P05", "Provincial clinics delivered in 15 provinces", date(2026, 9, 30), 0, "Delivery"),
    ("M11", "NSCF-2026", "P01", "Training base Stage 2 (gymnasium) complete", date(2026, 10, 15), 0, "Delivery"),
    ("M12", "MVA-SCH", "P03", "Schools attendance baseline report delivered", date(2026, 2, 28), 0, "Reporting"),
], columns=["MilestoneID", "AgreementID", "ProgrammeID", "Description", "DueDate", "TrancheAmount", "MilestoneType"])

lists = {
    "Funders": funders, "Agreements": agreements, "Programmes": programmes,
    "Accounts": accounts, "Provinces": provinces, "Milestones": milestones,
}

# ----------------------------------------------------------------- Write
for name, df in lists.items():
    df.to_csv(OUT / f"{name}.csv", index=False)

xlsx = OUT / "Masalais_Reference_Lists.xlsx"
with pd.ExcelWriter(xlsx, engine="openpyxl") as xw:
    for name, df in lists.items():
        df.to_excel(xw, sheet_name=name, index=False)

wb = load_workbook(xlsx)
for name, df in lists.items():
    ws = wb[name]
    ref = f"A1:{get_column_letter(df.shape[1])}{df.shape[0] + 1}"
    t = Table(displayName=f"tbl{name}", ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(t)
    for i, col in enumerate(df.columns, 1):
        width = max(len(str(col)), *(len(str(v)) for v in df[col])) + 2
        ws.column_dimensions[get_column_letter(i)].width = min(width, 60)
        if "Date" in col:
            for r in range(2, df.shape[0] + 2):
                ws.cell(r, i).number_format = "yyyy-mm-dd"
        if "Amount" in col:
            for r in range(2, df.shape[0] + 2):
                ws.cell(r, i).number_format = "#,##0"
wb.save(xlsx)

# --------------------------------------------------------- Sanity checks
cssp = milestones.query("AgreementID == 'CSSP-EST'")["TrancheAmount"].sum()
assert cssp == 9_000_000, cssp
assert set(agreements.FunderID) <= set(funders.FunderID)
assert set(milestones.AgreementID) <= set(agreements.AgreementID)
assert set(milestones.ProgrammeID) <= set(programmes.ProgrammeID)
assert len(provinces) == 22
print({k: len(v) for k, v in lists.items()})
