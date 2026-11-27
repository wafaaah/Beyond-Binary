"""Template based SMS, WhatsApp and printable briefs (no internet or LLM)."""
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SUPPLIES = [
    ("Saline bags", "saline_bags", "saline_bags_needed"),
    ("Diagnostic kits", "diagnostic_kits", "diagnostic_kits_needed"),
    ("Hospital beds", "hospital_beds", "hospital_beds_required"),
]


def assign_teams(allocation):
    """Give each allocated crew a team ID, in priority order."""
    teams, number = {}, 1
    for _, row in allocation.sort_values("priority_rank").iterrows():
        count = int(row["crews_allocated"])
        teams[row["ward_id"]] = [
            f"TEAM-{i:02d}" for i in range(number, number + count)
        ]
        number += count
    return teams


def _team_text(teams):
    return ", ".join(teams) if teams else "none assigned"


def sms_notice(row, teams):
    alert = row["deficit_alert"] or "No deficit"
    supplies = " ".join(
        f"{code}:{int(row[key + '_allocated'])}/{int(row[need])}"
        for code, (_, key, need) in zip(["Saline", "Kits", "Beds"], SUPPLIES)
    )
    return (
        f"DENGUE {row['risk_level'].upper()} {row['ward_id']} "
        f"wk {row['target_date']:%d-%b-%Y}. "
        f"Pred {row['predicted_cases']:.1f}. {supplies} (got/need). "
        f"Teams: {_team_text(teams)}. {alert}"
    )


def whatsapp_notice(row, teams):
    lines = [
        f"*Dengue Dispatch: {row['ward_id']}* ({row['city']})",
        f"Target week: {row['target_date']:%d %b %Y}",
        f"Risk: *{row['risk_level']}*",
        f"Predicted cases: {row['predicted_cases']:.1f}",
        "",
        "Supplies (allocated / required):",
    ]
    lines += [
        f"- {name}: {int(row[key + '_allocated'])} / {int(row[need])}"
        for name, key, need in SUPPLIES
    ]
    lines += [
        "",
        f"Spraying teams: {_team_text(teams)} "
        f"({int(row['crews_allocated'])} / {int(row['crews_required'])})",
        row["deficit_alert"] or "No supply or crew deficit.",
        "",
        "Forecast based estimate (historical replay). Verify before action.",
    ]
    return "\n".join(lines)


def html_brief(allocation, title="Ward Commissioner Brief"):
    """Self-contained printable HTML (use browser Print > Save as PDF)."""
    teams = assign_teams(allocation)
    sections = []
    for _, row in allocation.sort_values("priority_rank").iterrows():
        rows = "".join(
            f"<tr><td>{name}</td><td>{int(row[need])}</td>"
            f"<td>{int(row[key + '_allocated'])}</td>"
            f"<td>{int(row[key + '_deficit'])}</td></tr>"
            for name, key, need in SUPPLIES
        )
        rows += (
            f"<tr><td>Spraying crews</td><td>{int(row['crews_required'])}</td>"
            f"<td>{int(row['crews_allocated'])}</td>"
            f"<td>{int(row['crews_deficit'])}</td></tr>"
        )
        sections.append(
            f"<section><h2>{escape(row['ward_id'])} - {escape(row['city'])}</h2>"
            f"<p>Priority #{int(row['priority_rank'])} | "
            f"Risk: <b>{row['risk_level']}</b> | "
            f"Predicted cases: {row['predicted_cases']:.1f} | "
            f"Target week: {row['target_date']:%d %b %Y}</p>"
            "<table><tr><th>Item</th><th>Required</th><th>Allocated</th>"
            f"<th>Deficit</th></tr>{rows}</table>"
            f"<p>Teams: {escape(_team_text(teams[row['ward_id']]))}</p>"
            f"<p class='alert'>{escape(row['deficit_alert'])}</p></section>"
        )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{escape(title)}</title><style>"
        "body{font-family:Arial,sans-serif;margin:24px;color:#111}"
        "section{break-inside:avoid;border-bottom:1px solid #ccc;padding:8px 0}"
        "table{border-collapse:collapse;width:100%}"
        "td,th{border:1px solid #999;padding:5px;text-align:left}"
        ".alert{color:#b00020;font-weight:bold}"
        f"</style></head><body><h1>{escape(title)}</h1>"
        "<p>Forecast based estimate from a historical replay. "
        "Crew requirements and stock levels are planning assumptions.</p>"
        f"{''.join(sections)}</body></html>"
    )


def export_all(allocation, folder=ROOT / "exports"):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    teams = assign_teams(allocation)
    ordered = allocation.sort_values("priority_rank")
    sms = [sms_notice(r, teams[r["ward_id"]]) for _, r in ordered.iterrows()]
    chat = [whatsapp_notice(r, teams[r["ward_id"]])
            for _, r in ordered.iterrows()]
    (folder / "sample_sms.txt").write_text("\n\n".join(sms), encoding="utf-8")
    (folder / "sample_whatsapp.txt").write_text(
        "\n\n---\n\n".join(chat), encoding="utf-8")
    (folder / "sample_commissioner_brief.html").write_text(
        html_brief(allocation), encoding="utf-8")
    return folder


if __name__ == "__main__":
    from ml.allocation import allocate, forecast, load_data, peak_week

    data = load_data()
    result = allocate(forecast(data, peak_week(data)), 70, 20)
    print("Exports written to", export_all(result))
