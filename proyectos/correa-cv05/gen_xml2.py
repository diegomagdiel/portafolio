from datetime import datetime, timedelta, time
import xml.etree.ElementTree as ET
from datos import rows, es, ef, END, START, crit

H_DAY = 11
def d_start(d): return datetime.combine(START + timedelta(days=d), time(8, 0))
def d_finish(d): return datetime.combine(START + timedelta(days=d - 1), time(20, 0))
def iso(x): return x.strftime("%Y-%m-%dT%H:%M:%S")

NS = "http://schemas.microsoft.com/project"
ET.register_namespace("", NS)
def sub(p, tag, text=None):
    e = ET.SubElement(p, f"{{{NS}}}{tag}")
    if text is not None: e.text = str(text)
    return e

P = ET.Element(f"{{{NS}}}Project")
for k, v in [("SaveVersion", 14), ("Name", "Correa Transportadora CV-05"), ("Title", "Montaje Correa Transportadora CV-05"),
             ("ScheduleFromStart", 1), ("StartDate", iso(d_start(0))), ("FinishDate", iso(d_finish(END))),
             ("CalendarUID", 1), ("DefaultStartTime", "08:00:00"), ("DefaultFinishTime", "20:00:00"),
             ("MinutesPerDay", H_DAY * 60), ("MinutesPerWeek", H_DAY * 60 * 7), ("DaysPerMonth", 30),
             ("DurationFormat", 7), ("CurrencySymbol", "$"), ("CurrencyDigits", 0)]:
    sub(P, k, v)

cal = sub(sub(P, "Calendars"), "Calendar")
sub(cal, "UID", 1); sub(cal, "Name", "Turno 7x7 - 11 h"); sub(cal, "IsBaseCalendar", 1); sub(cal, "BaseCalendarUID", -1)
wds = sub(cal, "WeekDays")
for d in range(1, 8):
    wd = sub(wds, "WeekDay"); sub(wd, "DayType", d); sub(wd, "DayWorking", 1)
    wts = sub(wd, "WorkingTimes")
    for a, b in [("08:00:00", "13:00:00"), ("14:00:00", "20:00:00")]:
        wt = sub(wts, "WorkingTime"); sub(wt, "FromTime", a); sub(wt, "ToTime", b)

T = sub(P, "Tasks")
t0 = sub(T, "Task"); sub(t0, "UID", 0); sub(t0, "ID", 0); sub(t0, "Name", "Correa Transportadora CV-05")
sub(t0, "OutlineLevel", 0); sub(t0, "Summary", 1)
for f, lvl, edt, name, d, preds, bud, t in rows:
    dur = ef[f] - es[f]
    st = d_start(es[f]) if (t != "M" or es[f] == 0) else d_finish(es[f])
    fi = d_finish(ef[f]) if dur > 0 else st
    k = sub(T, "Task")
    for tag, v in [("UID", f), ("ID", f), ("Name", name), ("WBS", edt), ("OutlineNumber", edt), ("OutlineLevel", lvl),
                   ("Type", 1), ("Start", iso(st)), ("Finish", iso(fi)), ("Duration", f"PT{dur * H_DAY}H0M0S"),
                   ("DurationFormat", 7), ("Milestone", 1 if t == "M" else 0), ("Summary", 1 if t == "S" else 0),
                   ("Critical", 1 if (f in crit) else 0), ("ConstraintType", 0), ("CalendarUID", -1),
                   ("FixedCost", bud * 1_000_000 if t == "T" else 0), ("FixedCostAccrual", 3)]:
        sub(k, tag, v)
    for p in preds:
        pl = sub(k, "PredecessorLink"); sub(pl, "PredecessorUID", p); sub(pl, "Type", 1)
        sub(pl, "LinkLag", 0); sub(pl, "LagFormat", 7)
sub(P, "Resources"); sub(P, "Assignments")
ET.indent(P)
ET.ElementTree(P).write("correa_CV05_linea_base.xml", encoding="UTF-8", xml_declaration=True)
print("ok", iso(d_finish(END)))
