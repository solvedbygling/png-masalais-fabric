"""Draws the KPI card icons (original artwork) as 80x80 PNGs: tinted rounded tile + glyph.
Displayed at 40x40 in Power BI (2x for sharpness)."""
import cairosvg
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "assets" / "icons"
OUT.mkdir(parents=True, exist_ok=True)
GOLD, GOLDT, RED, REDT, CHAR, WHITE = "#F2A900", "#FBF1D6", "#C8102E", "#FBE5E8", "#2F2F2F", "#FFFFFF"

def glyph(kind, c):
    x, y = 40, 40
    g = {
     "coins": "".join(f'<ellipse cx="40" cy="{50-i*9}" rx="16" ry="6" fill="{c}" stroke="#fff" stroke-width="2"/>' for i in range(3)),
     "bars": "".join(f'<rect x="{24+i*12}" y="{56-h}" width="9" height="{h}" rx="2" fill="{c}"/>' for i, h in enumerate([14, 22, 32])),
     "people": (f'<circle cx="27" cy="33" r="6" fill="{c}"/><path d="M17 54 a10 10 0 0 1 20 0 z" fill="{c}"/>'
                f'<circle cx="53" cy="33" r="6" fill="{c}"/><path d="M43 54 a10 10 0 0 1 20 0 z" fill="{c}"/>'
                f'<circle cx="40" cy="30" r="8" fill="{c}" stroke="{"#FBF1D6"}" stroke-width="2"/><path d="M26 58 a14 14 0 0 1 28 0 z" fill="{c}" stroke="{"#FBF1D6"}" stroke-width="2"/>'),
     "percent": f'<circle cx="29" cy="29" r="6" fill="none" stroke="{c}" stroke-width="5"/><circle cx="51" cy="51" r="6" fill="none" stroke="{c}" stroke-width="5"/><line x1="52" y1="25" x2="28" y2="55" stroke="{c}" stroke-width="5" stroke-linecap="round"/>',
     "flag": f'<rect x="27" y="22" width="4" height="38" rx="2" fill="{c}"/><path d="M31 23 h22 l-6 9 l6 9 h-22 z" fill="{c}"/>',
     "warning": f'<path d="M40 20 L60 56 H20 Z" fill="{c}" stroke="{c}" stroke-width="4" stroke-linejoin="round"/><rect x="38" y="31" width="4" height="13" rx="2" fill="#fff"/><circle cx="40" cy="50" r="2.6" fill="#fff"/>',
     "repeat": f'<path d="M24 38 a16 16 0 0 1 28-10" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/><path d="M50 20 l4 10 l-10 1 z" fill="{c}"/><path d="M56 42 a16 16 0 0 1 -28 10" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round"/><path d="M30 60 l-4 -10 l10 -1 z" fill="{c}"/>',
     "calendar": f'<rect x="22" y="26" width="36" height="32" rx="4" fill="none" stroke="{c}" stroke-width="5"/><rect x="22" y="26" width="36" height="9" fill="{c}"/><rect x="29" y="20" width="4" height="10" rx="2" fill="{c}"/><rect x="47" y="20" width="4" height="10" rx="2" fill="{c}"/>',
     "school": f'<path d="M40 20 L60 32 H20 Z" fill="{c}"/><rect x="24" y="34" width="32" height="22" fill="{c}"/><rect x="36" y="44" width="8" height="12" fill="#fff"/><rect x="20" y="56" width="40" height="4" fill="{c}"/>',
     "pin": f'<path d="M40 62 C28 46 24 40 24 33 a16 16 0 0 1 32 0 c0 7 -4 13 -16 29 z" fill="{c}"/><circle cx="40" cy="33" r="6" fill="#fff"/>',
     "dollar": f'<circle cx="40" cy="40" r="20" fill="none" stroke="{c}" stroke-width="5"/><text x="40" y="49" font-family="Inter" font-size="26" font-weight="700" fill="{c}" text-anchor="middle">$</text>',
     "check": f'<circle cx="40" cy="40" r="20" fill="{c}"/><path d="M30 41 l7 7 l14 -15" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
     "clock": f'<circle cx="40" cy="40" r="19" fill="none" stroke="{c}" stroke-width="5"/><path d="M40 29 V41 L48 46" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
     "list": "".join(f'<circle cx="25" cy="{28+i*12}" r="3.5" fill="{c}"/><rect x="33" y="{25+i*12}" width="24" height="6" rx="3" fill="{c}"/>' for i in range(3)),
     "remove": f'<circle cx="40" cy="40" r="20" fill="{c}"/><rect x="29" y="37" width="22" height="6" rx="3" fill="#fff"/>',
     "edit": f'<path d="M24 56 l3 -11 l20 -20 l8 8 l-20 20 z" fill="{c}"/><rect x="22" y="57" width="36" height="4" rx="2" fill="{c}"/>',
     "shield": f'<path d="M40 19 L58 26 V40 C58 51 50 58 40 62 C30 58 22 51 22 40 V26 Z" fill="{c}"/><rect x="38" y="30" width="4" height="15" rx="2" fill="#fff"/><circle cx="40" cy="51" r="2.6" fill="#fff"/>',
    }[kind]
    return g

icons = {  # name: (glyph, tone)
    "funding": ("coins", "gold"), "spend": ("bars", "gold"), "people": ("people", "gold"),
    "female": ("percent", "gold"), "milestone-overdue": ("flag", "red"), "over-budget": ("warning", "red"),
    "attendances": ("repeat", "gold"), "sessions": ("calendar", "gold"), "schools": ("school", "gold"),
    "provinces": ("pin", "gold"), "cost": ("dollar", "gold"), "milestones": ("flag", "gold"),
    "complete": ("check", "gold"), "late": ("clock", "gold"), "dq-issues": ("list", "gold"),
    "dq-removed": ("remove", "gold"), "dq-corrected": ("edit", "gold"), "dq-flagged": ("shield", "red"),
}
for name, (kind, tone) in icons.items():
    tint, col = (GOLDT, GOLD) if tone == "gold" else (REDT, RED)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80">'
           f'<rect width="80" height="80" rx="18" fill="{tint}"/>{glyph(kind, col)}</svg>')
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / f"icon-{name}.png"), output_width=80, output_height=80)
print(len(icons), "icons written to", OUT)
