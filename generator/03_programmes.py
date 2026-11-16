"""
PNG Masalais (FICTIONAL CLUB, SYNTHETIC DATA)
Step 3: programme delivery and milestone data.

Field data comes from a (fictional) mobile data-collection app used by programme officers.
Like real field apps (ODK / Kobo style) it exports a main table (sessions) and a
"repeat group" child table (attendance), one pair of CSVs per month.

Outputs:
  data/field/schools.csv                         school master (programme + comparison schools)
  data/field/participants_register.csv           participant register snapshot at 31 Oct 2026
  data/field/sessions/sessions_YYYY-MM.csv       one file per month
  data/field/attendance/attendance_YYYY-MM.csv   one file per month
  data/field/school_attendance_by_term.csv       term attendance rates from provincial education offices
  data/milestones/Milestone_Updates.csv          status update history (seed for the update form)
  data/_answer_key/programme_storylines.md

Run 01_reference.py first.
"""
from datetime import date, timedelta, datetime, time
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(1975)  # PNG independence year
ROOT = Path(__file__).resolve().parent.parent / "data"
REF = ROOT / "reference"
FIELD = ROOT / "field"
for d in (FIELD / "sessions", FIELD / "attendance", ROOT / "milestones", ROOT / "_answer_key"):
    d.mkdir(parents=True, exist_ok=True)

REPORT_END = date(2026, 10, 31)
provinces = pd.read_csv(REF / "Provinces.csv")
prov_region = dict(zip(provinces.ProvinceCode, provinces.Region))

# PNG school terms (approximate, fictional calendar)
TERMS = [
    (2025, 1, date(2025, 2, 3), date(2025, 4, 11)), (2025, 2, date(2025, 4, 28), date(2025, 6, 27)),
    (2025, 3, date(2025, 7, 14), date(2025, 9, 19)), (2025, 4, date(2025, 10, 6), date(2025, 12, 5)),
    (2026, 1, date(2026, 2, 2), date(2026, 4, 10)), (2026, 2, date(2026, 4, 27), date(2026, 6, 26)),
    (2026, 3, date(2026, 7, 13), date(2026, 9, 18)), (2026, 4, date(2026, 10, 5), date(2026, 12, 4)),
]


def in_term(d):
    return any(s <= d <= e for _, _, s, e in TERMS)


def weekly(start, end, weekday):
    d = start + timedelta(days=(weekday - start.weekday()) % 7)
    while d <= end:
        yield d
        d += timedelta(days=7)


# ------------------------------------------------------------------ Schools
words = ["Solwara", "Wara", "Diwai", "Kunai", "Kapul", "Muruk", "Malolo", "Sinabada", "Gaden",
         "Bikpela", "Siroi", "Lapun", "Tambu", "Sanguma", "Mumu", "Pukpuk", "Kakaruk", "Bilum",
         "Kina", "Tok", "Saksak", "Kulau", "Buai", "Tumbuna", "Haus", "Ples", "Sanap", "Kambang"]
suffix = ["Creek", "Ridge", "Valley", "Point", "Hill", "Junction", "Station", "Bay", "Plains", "Gully"]
names = set()
while len(names) < 85:
    names.add(f"{rng.choice(words)} {rng.choice(suffix)}")
names = sorted(names)
rng.shuffle(names)

school_provs = ["NCD", "CEN", "MOR", "MAD", "EHP", "WHP", "SIM", "JIW", "ENB", "ESP", "MBP", "ENG"]
# 55 programme schools join in waves; 30 comparison schools never join.
join_dates = ([date(2025, 10, 6)] * 14 + [date(2026, 2, 2)] * 18 + [date(2026, 4, 20)] * 10 +
              [date(2026, 4, 27)] * 5 + [date(2026, 7, 13)] * 8)
schools = []
for i, nm in enumerate(names):
    prog = i < 55
    schools.append(dict(
        SchoolID=f"SCH{i + 1:03d}",
        SchoolName=f"{nm} {'Primary' if rng.random() < .7 else 'Secondary'} School",
        ProvinceCode=school_provs[i % len(school_provs)],
        IsProgrammeSchool="Y" if prog else "N",
        ProgrammeJoinDate=join_dates[i] if prog else None,
    ))
schools = pd.DataFrame(schools)
schools["Level"] = np.where(schools.SchoolName.str.contains("Primary"), "Primary", "Secondary")
schools = schools[["SchoolID", "SchoolName", "Level", "ProvinceCode", "IsProgrammeSchool", "ProgrammeJoinDate"]]
schools.to_csv(FIELD / "schools.csv", index=False)

# ------------------------------------------------------------- Participants
participants = []   # dicts
pid = 0


def new_participant(gender, age_lo, age_hi, prov, reg_date, prog):
    global pid
    pid += 1
    participants.append(dict(ParticipantID=f"PRT{pid:06d}", Gender=gender,
                             BirthYear=reg_date.year - int(rng.integers(age_lo, age_hi + 1)),
                             ProvinceCode=prov, RegisteredDate=reg_date, HomeProgrammeID=prog))
    return f"PRT{pid:06d}"


sessions, attendance = [], []
sid = 0
facilitators = [f"FAC{i:03d}" for i in range(1, 41)]


def add_session(d, prog, prov, school, mins, attendees):
    global sid
    sid += 1
    s = f"SES{sid:06d}"
    sessions.append(dict(SessionID=s, SessionDate=d, ProgrammeID=prog, ProvinceCode=prov,
                         SchoolID=school or "", FacilitatorID=rng.choice(facilitators), DurationMins=mins))
    attendance.extend((s, p) for p in attendees)
    return s


# P03 Schools Rugby League: weekly session in term, from the school's join date.
for sc in schools[schools.IsProgrammeSchool == "Y"].itertuples():
    cohort = [new_participant("F" if rng.random() < .38 else "M",
                              8 if sc.Level == "Primary" else 13, 12 if sc.Level == "Primary" else 17,
                              sc.ProvinceCode, sc.ProgrammeJoinDate, "P03")
              for _ in range(int(rng.integers(35, 61)))]
    for d in weekly(sc.ProgrammeJoinDate, REPORT_END, int(rng.integers(0, 5))):
        if in_term(d) and rng.random() > .08:      # some sessions missed (weather, exams)
            att = [p for p in cohort if rng.random() < rng.uniform(.70, .88)]
            add_session(d, "P03", sc.ProvinceCode, sc.SchoolID, 60, att)

# P04 Women's and Girls' Pathways: hubs launched by region (M08 met late, Jul 2026).
hubs = [("NCD", date(2026, 2, 9)), ("CEN", date(2026, 2, 16)), ("MOR", date(2026, 3, 9)),
        ("MAD", date(2026, 3, 16)), ("EHP", date(2026, 4, 13)), ("WHP", date(2026, 4, 20)),
        ("SIM", date(2026, 5, 4)), ("ENB", date(2026, 7, 6)), ("MAN", date(2026, 7, 10)),
        ("MOR", date(2026, 8, 3)), ("NCD", date(2026, 8, 10)), ("JIW", date(2026, 9, 7))]
for prov, start in hubs:
    cohort = []
    for d in weekly(start, REPORT_END, 5):     # Saturdays
        if date(2025, 12, 15) <= d <= date(2026, 1, 25):
            continue
        weeks_in = (d - start).days // 7
        target = min(45, 14 + weeks_in * 2)
        while len(cohort) < target:
            cohort.append(new_participant("F", 12, 24, prov, d, "P04"))
        add_session(d, "P04", prov, None, 90, [p for p in cohort if rng.random() < .78])

# P05 Provincial Clinics: one-day clinics. 12 provinces reached by 30 Sep 2026 (target 15: M10 overdue).
clinic_plan = [("NCD", "2025-09-20"), ("MOR", "2025-10-18"), ("EHP", "2025-11-15"), ("CEN", "2026-02-21"),
               ("WHP", "2026-03-14"), ("MAD", "2026-04-18"), ("ENB", "2026-05-16"), ("SIM", "2026-06-13"),
               ("ESP", "2026-07-11"), ("MBP", "2026-08-08"), ("ENG", "2026-08-29"), ("HEL", "2026-09-26"),
               ("JIW", "2026-10-24")]
repeat_pool = {}
for prov, first in clinic_plan:
    d0 = date.fromisoformat(first)
    visits = [d0] + [d0 + timedelta(days=int(x)) for x in (70, 140, 210, 280)]
    for d in visits:
        if d > REPORT_END:
            break
        pool = repeat_pool.setdefault(prov, [])
        returning = [p for p in pool if rng.random() < .25]
        new = [new_participant("F" if rng.random() < .30 else "M", 8, 18, prov, d, "P05")
               for _ in range(int(rng.integers(45, 95)))]
        pool.extend(new)
        add_session(d, "P05", prov, None, 240, returning + new)

# P02 Academy: intake 20 Feb 2026 (M03), three sessions a week.
academy = [new_participant("M", 16, 20, rng.choice(provinces.ProvinceCode), date(2026, 2, 20), "P02")
           for _ in range(48)]
for wd in (0, 2, 4):
    for d in weekly(date(2026, 2, 23), REPORT_END, wd):
        if date(2026, 6, 29) <= d <= date(2026, 7, 10):   # mid-year break
            continue
        add_session(d, "P02", "NCD", None, 120, [p for p in academy if rng.random() < .90])

# P06 Coach and Match Official Development: two-day courses, unique participants.
course_d = date(2025, 9, 13)
course_provs = ["NCD", "MOR", "EHP", "CEN", "WHP", "MAD", "ENB", "SIM", "ESP", "MBP", "ENG", "JIW"]
k = 0
while course_d <= REPORT_END:
    prov = course_provs[k % len(course_provs)]
    female_p = .18 + .12 * min(1, (course_d - date(2025, 9, 1)).days / 400)   # rising female share
    att = [new_participant("F" if rng.random() < female_p else "M", 20, 45, prov, course_d, "P06")
           for _ in range(int(rng.integers(12, 21)))]
    for day in (course_d, course_d + timedelta(days=1)):
        add_session(day, "P06", prov, None, 420, att)
    course_d += timedelta(days=int(rng.integers(12, 20)))
    k += 1

sessions = pd.DataFrame(sessions)
attendance = pd.DataFrame(attendance, columns=["SessionID", "ParticipantID"])
participants = pd.DataFrame(participants)

# ---------------------------------------------------- Plant field data issues
# 1. Gender typed inconsistently in the register
mess = rng.choice(participants.index, size=int(len(participants) * .06), replace=False)
participants.loc[mess, "Gender"] = [{"F": rng.choice(["Female", "female", "f", " F"]),
                                     "M": rng.choice(["Male", "male", "m", "M "])}[g]
                                    for g in participants.loc[mess, "Gender"]]
# 2. Duplicate session submissions (same SessionID, resubmitted later after an edit)
sessions["SubmittedAt"] = [datetime.combine(d, time(int(rng.integers(15, 20)), int(rng.integers(0, 60))))
                           + timedelta(days=int(rng.integers(0, 4))) for d in sessions.SessionDate]
dup_idx = rng.choice(sessions.index, size=int(len(sessions) * .015), replace=False)
dups = sessions.loc[dup_idx].copy()
dups["SubmittedAt"] = dups.SubmittedAt + pd.to_timedelta(rng.integers(1, 48, len(dups)), unit="h")
dups["DurationMins"] = [m if rng.random() < .5 else m + 15 for m in dups.DurationMins]
sessions_out = pd.concat([sessions, dups]).sort_values(["SessionDate", "SessionID", "SubmittedAt"])
# 3. School sessions with province left blank (app field not mandatory)
blank_prov = rng.choice(sessions_out.index[sessions_out.SchoolID != ""], size=40, replace=False)
sessions_out.loc[blank_prov, "ProvinceCode"] = ""
# 4. Attendance rows pointing at participants missing from the register
orphans = pd.DataFrame({"SessionID": rng.choice(sessions.SessionID, 22),
                        "ParticipantID": [f"PRT9{int(x):05d}" for x in rng.integers(0, 99999, 22)]})
attendance_out = pd.concat([attendance, orphans])

# ------------------------------------------------------------------- Write
sessions_out["Month"] = pd.to_datetime(sessions_out.SessionDate).dt.strftime("%Y-%m")
sess_month = dict(zip(sessions.SessionID, pd.to_datetime(sessions.SessionDate).dt.strftime("%Y-%m")))
attendance_out["Month"] = attendance_out.SessionID.map(sess_month)
for m, g in sessions_out.groupby("Month"):
    g.drop(columns="Month").to_csv(FIELD / "sessions" / f"sessions_{m}.csv", index=False)
for m, g in attendance_out.groupby("Month"):
    g.drop(columns="Month").to_csv(FIELD / "attendance" / f"attendance_{m}.csv", index=False)
participants.to_csv(FIELD / "participants_register.csv", index=False)

# ------------------------------------------------- School attendance by term
rows = []
for sc in schools.itertuples():
    base = float(np.clip(rng.normal(.71, .06), .55, .86))
    enrol = int(rng.integers(180, 650))
    for yr, t, s, e in TERMS:
        if e > REPORT_END:
            continue
        seasonal = {1: -.02, 2: 0, 3: -.015, 4: -.03}[t]
        lift = 0.0
        if sc.IsProgrammeSchool == "Y" and s >= sc.ProgrammeJoinDate - timedelta(days=7):
            terms_in = sum(1 for y2, t2, s2, e2 in TERMS if sc.ProgrammeJoinDate - timedelta(days=7) <= s2 <= s)
            lift = min(.07, .025 * terms_in)
        drift = .004 * TERMS.index((yr, t, s, e))     # general improvement everywhere
        rate = np.clip(base + seasonal + lift + drift + rng.normal(0, .015), .4, .97)
        rows.append(dict(SchoolID=sc.SchoolID, Year=yr, Term=t, TermStart=s, TermEnd=e,
                         Enrolled=enrol + int(rng.integers(-15, 16)), AvgAttendanceRate=round(rate, 3)))
school_att = pd.DataFrame(rows)
school_att.to_csv(FIELD / "school_attendance_by_term.csv", index=False)

# -------------------------------------------------------- Milestone updates
# (MilestoneID, [(date, status, pct, comment)...]) as at 31 Oct 2026
H = {
    "M01": [("2025-07-01", "On track", 50, "Final terms agreed with donor"),
            ("2025-07-15", "Complete", 100, "Agreement signed by both parties")],
    "M02": [("2025-08-15", "On track", 30, "Inception plan drafted"),
            ("2025-09-26", "On track", 70, "Safeguarding policy with board for review"),
            ("2025-10-28", "Complete", 100, "Board approved; submitted to donor")],
    "M03": [("2025-09-30", "On track", 20, "Head coach shortlist complete"),
            ("2025-11-28", "On track", 55, "Head coach appointed; S&C role advertised"),
            ("2026-01-30", "On track", 85, "Academy trials held in 6 provinces"),
            ("2026-02-20", "Complete", 100, "48 players in first academy intake")],
    "M04": [("2025-10-31", "On track", 15, "Contractor mobilised"),
            ("2025-12-19", "On track", 35, "Earthworks complete"),
            ("2026-02-27", "At risk", 55, "Wet season delays; drainage redesign needed"),
            ("2026-03-31", "At risk", 70, "Missed due date; variation approved, new date June"),
            ("2026-04-30", "At risk", 82, "Change rooms behind schedule"),
            ("2026-06-12", "Complete", 100, "Practical completion certified")],
    "M05": [("2026-07-31", "On track", 40, "Data collection for report under way"),
            ("2026-08-28", "Complete", 100, "Report and acquittal submitted")],
    "M06": [("2026-09-30", "Not started", 0, "Scheduled to start November"),
            ("2026-10-30", "On track", 15, "Evaluation consultant engaged")],
    "M07": [("2025-11-28", "On track", 35, "14 schools live in Term 4"),
            ("2026-02-27", "On track", 80, "32 schools live in Term 1"),
            ("2026-03-31", "At risk", 80, "Second wave of 10 schools delayed to Term 2"),
            ("2026-04-30", "Complete", 100, "40 schools reached in first week of Term 2")],
    "M08": [("2026-02-27", "On track", 25, "Southern hubs launched"),
            ("2026-04-30", "On track", 75, "Momase and Highlands hubs launched"),
            ("2026-05-29", "At risk", 75, "Islands launch delayed, venue unavailable"),
            ("2026-07-10", "Complete", 100, "Islands hubs launched; 4 regions live")],
    "M09": [("2026-03-31", "On track", 45, "Training rolled out to Southern and Momase coaches"),
            ("2026-05-29", "On track", 72, "Highlands sessions complete"),
            ("2026-06-30", "At risk", 86, "Remote coaches not yet trained; online module sourced"),
            ("2026-07-24", "Complete", 100, "All active coaches trained and recorded")],
    "M10": [("2026-03-31", "On track", 33, "5 provinces reached"),
            ("2026-06-30", "On track", 53, "8 provinces reached"),
            ("2026-08-31", "At risk", 73, "11 provinces; travel costs above budget"),
            ("2026-09-30", "At risk", 80, "12 of 15 provinces; government release delayed"),
            ("2026-10-30", "At risk", 87, "Jiwaka delivered; Western and Gulf need funding")],
    "M11": [("2026-07-31", "On track", 30, "Slab poured"),
            ("2026-08-31", "On track", 55, "Frame and roof complete"),
            ("2026-09-30", "At risk", 75, "Contractor paused pending government payment"),
            ("2026-10-30", "At risk", 90, "Fit-out under way; completion expected late Nov")],
    "M12": [("2026-01-30", "On track", 60, "Term 4 data received from education offices"),
            ("2026-02-25", "Complete", 100, "Baseline report delivered to sponsor")],
}
owners = {"M01": "Chief Executive", "M02": "Chief Executive", "M05": "Finance Manager",
          "M06": "Chief Executive", "M03": "High Performance Manager", "M04": "Facilities Manager",
          "M11": "Facilities Manager", "M07": "Schools Programme Officer", "M12": "Schools Programme Officer",
          "M08": "Women's Pathway Officer", "M09": "Safeguarding Officer", "M10": "Community Programme Officer"}
upd = []
n = 0
for mid, hist in H.items():
    for d, st, pct, c in hist:
        n += 1
        upd.append(dict(UpdateID=f"UPD{n:04d}", MilestoneID=mid, UpdateDate=d, Status=st,
                        PctComplete=pct, Comment=c, UpdatedBy=owners[mid]))
upd = pd.DataFrame(upd).sort_values(["UpdateDate", "MilestoneID"])
upd.to_csv(ROOT / "milestones" / "Milestone_Updates.csv", index=False)

# -------------------------------------------------------------- Self-check
s = sessions.merge(attendance, on="SessionID")
s = s.merge(participants[["ParticipantID", "Gender"]], on="ParticipantID")
s["G"] = s.Gender.str.strip().str.upper().str[0]
s["Month"] = pd.to_datetime(s.SessionDate).dt.to_period("M")
reach = s.groupby("ProgrammeID").ParticipantID.nunique()
fem = s.drop_duplicates("ParticipantID").groupby("ProgrammeID").G.apply(lambda g: (g == "F").mean())
first_session = sessions[sessions.SchoolID != ""].groupby("SchoolID").SessionDate.min().sort_values()
clinic_provs_sep = sessions[(sessions.ProgrammeID == "P05") & (sessions.SessionDate <= date(2026, 9, 30))].ProvinceCode.nunique()
monthly_fem = s.drop_duplicates(["Month", "ParticipantID"]).groupby("Month").G.apply(lambda g: (g == "F").mean())

sa = school_att.merge(schools[["SchoolID", "IsProgrammeSchool"]], on="SchoolID")
sa_tbl = sa.pivot_table(index=["Year", "Term"], columns="IsProgrammeSchool", values="AvgAttendanceRate").round(3)

with open(ROOT / "_answer_key" / "programme_storylines.md", "w") as f:
    f.write("# Programme storylines planted in the synthetic data (answer key)\n\n")
    f.write(f"Unique participants: {s.ParticipantID.nunique():,}  |  Attendances: {len(s):,}  |  Sessions: {len(sessions):,}\n\n")
    f.write("## Reach by programme (unique participants, female share)\n\n")
    f.write(pd.DataFrame({"Participants": reach, "FemaleShare": fem.round(3)}).to_markdown() + "\n\n")
    f.write("## Female share of active participants by month\n\n")
    f.write(monthly_fem.round(3).to_frame("FemaleShare").to_markdown() + "\n\n")
    f.write(f"## Milestone ties\n\n- 40th school first session: {first_session.iloc[39]} (M07 due 2026-03-31)\n")
    f.write(f"- Provinces with a clinic by 30 Sep 2026: {clinic_provs_sep} (M10 target 15, overdue)\n")
    f.write("- M11 gym at risk/overdue: contractor paused while PNG government release delayed (ties to finance)\n\n")
    f.write("## School attendance rate by term (N = comparison, Y = programme schools)\n\n")
    f.write(sa_tbl.to_markdown() + "\n\n")
    f.write("## Planted field data issues\n\n")
    f.write(f"- Inconsistent Gender values in register: {len(mess)}\n")
    f.write(f"- Duplicate session submissions (keep latest SubmittedAt): {len(dups)}\n")
    f.write("- School sessions with blank ProvinceCode (derive from school): 40\n")
    f.write("- Attendance rows with ParticipantID not in register: 22\n")

print(open(ROOT / "_answer_key" / "programme_storylines.md").read())

# ---------------------------------------- Add updates to the SharePoint list workbook
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
wbp = REF / "Masalais_Reference_Lists.xlsx"
wb = load_workbook(wbp)
if "MilestoneUpdates" in wb.sheetnames:
    del wb["MilestoneUpdates"]
ws = wb.create_sheet("MilestoneUpdates")
ws.append(list(upd.columns))
for r_ in upd.itertuples(index=False):
    ws.append([date.fromisoformat(v) if i == 2 else v for i, v in enumerate(r_)])
tbl = Table(displayName="tblMilestoneUpdates", ref=f"A1:{get_column_letter(upd.shape[1])}{len(upd) + 1}")
tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
ws.add_table(tbl)
for i, w in enumerate([10, 12, 12, 12, 12, 55, 28], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
for r_ in range(2, len(upd) + 2):
    ws.cell(r_, 3).number_format = "yyyy-mm-dd"
wb.save(wbp)
