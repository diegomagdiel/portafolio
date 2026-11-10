from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

START = datetime(2026, 11, 16, 7, 0, 0)

# (fila, nivel, nombre, horas, predecesoras, [(recurso, unidades)], tipo) tipo: S=resumen, M=hito, T=tarea
rows = [
    (1, 1, "PARADA CHANCADOR PRIMARIO", None, [], [], "S"),
    (2, 2, "Inicio de parada", 0, [], [], "M"),
    (3, 2, "Detención y aislación", None, [], [], "S"),
    (4, 3, "Vaciado de cámara de chancado", 2, [2], [("Operador", 1)], "T"),
    (5, 3, "Detención de chancador y correa de descarga", 1, [4], [("Operador", 1)], "T"),
    (6, 3, "Bloqueo y aislación de energías (LOTO)", 2, [5], [("Eléctricos", 2), ("Supervisor", 1)], "T"),
    (7, 3, "Prueba de energía cero y charla de seguridad", 1, [6], [("Supervisor", 1), ("Prevencionista", 1)], "T"),
    (8, 2, "Desmontaje", None, [], [], "S"),
    (9, 3, "Instalación de andamios y accesos", 4, [7], [("Andamieros", 3)], "T"),
    (10, 3, "Retiro de araña (spider)", 4, [9], [("Mecánicos", 2), ("Grúa", 1)], "T"),
    (11, 3, "Retiro de conjunto eje principal y manto", 6, [10], [("Mecánicos", 2), ("Grúa", 1)], "T"),
    (12, 3, "Desconexión de sistema hidráulico", 2, [7], [("Mecánicos", 2)], "T"),
    (13, 3, "Limpieza de cámara de descarga", 6, [7], [("Ayudantes", 2)], "T"),
    (14, 2, "Mantención", None, [], [], "S"),
    (15, 3, "Cambio de manto en taller", 18, [11], [("Mecánicos", 2), ("Soldadores", 1)], "T"),
    (16, 3, "Inspección y medición de cóncavas", 4, [11], [("Mecánicos", 2), ("Inspector", 1)], "T"),
    (17, 3, "Cambio de cóncavas hilera inferior", 16, [16], [("Mecánicos", 2), ("Grúa", 1), ("Soldadores", 1)], "T"),
    (18, 3, "Cambio de revestimientos cámara de descarga", 12, [13], [("Soldadores", 1), ("Ayudantes", 2)], "T"),
    (19, 3, "Mantención hidráulica (filtros, aceite, sellos)", 8, [12], [("Mecánicos", 2)], "T"),
    (20, 3, "Mantención eléctrica motor principal", 6, [7], [("Eléctricos", 2)], "T"),
    (21, 3, "Cambio de polines y raspadores correa de descarga", 10, [7], [("Mecánicos", 2), ("Ayudantes", 2)], "T"),
    (22, 3, "Inspección de excéntrica y bujes", 6, [11], [("Mecánicos", 2), ("Inspector", 1)], "T"),
    (23, 2, "Montaje", None, [], [], "S"),
    (24, 3, "Montaje eje principal con manto nuevo", 6, [15, 17, 22], [("Mecánicos", 2), ("Grúa", 1)], "T"),
    (25, 3, "Montaje y ajuste de araña", 4, [24], [("Mecánicos", 2), ("Grúa", 1)], "T"),
    (26, 3, "Reconexión hidráulica y ajuste de setting", 3, [25, 19], [("Mecánicos", 2)], "T"),
    (27, 3, "Retiro de andamios", 3, [26, 18], [("Andamieros", 3)], "T"),
    (28, 2, "Pruebas y entrega", None, [], [], "S"),
    (29, 3, "Retiro de bloqueos y energización", 1, [27, 20, 21], [("Eléctricos", 2), ("Supervisor", 1)], "T"),
    (30, 3, "Prueba en vacío", 2, [29], [("Operador", 1), ("Mecánicos", 2)], "T"),
    (31, 3, "Prueba con carga", 2, [30], [("Operador", 1)], "T"),
    (32, 3, "Entrega a operaciones", 0, [31], [], "M"),
]

# (nombre, dotación máx, tasa estándar CLP/hora)
resources = [
    ("Mecánicos", 6, 18000), ("Soldadores", 3, 20000), ("Ayudantes", 4, 10000), ("Eléctricos", 2, 19000),
    ("Andamieros", 3, 12000), ("Supervisor", 1, 30000), ("Prevencionista", 1, 25000), ("Inspector", 1, 28000),
    ("Operador", 1, 16000), ("Grúa", 1, 120000),
]
rate = {n: r for n, _, r in resources}
res_uid = {name: i + 1 for i, (name, *_ ) in enumerate(resources)}

# forward pass (horas desde inicio)
es, ef = {}, {}
for f, lvl, name, h, preds, res, t in rows:
    if t == "S":
        continue
    s = max([ef[p] for p in preds], default=0)
    es[f], ef[f] = s, s + h
# summaries
for i, (f, lvl, name, h, preds, res, t) in enumerate(rows):
    if t != "S":
        continue
    kids = []
    for g, l2, *_ in rows[i + 1:]:
        if l2 <= lvl:
            break
        if g in es:
            kids.append(g)
    es[f] = min(es[k] for k in kids)
    ef[f] = max(ef[k] for k in kids)

# backward pass for critical flag
proj_end = max(ef.values())
succ = {f: [] for f in es}
for f, lvl, name, h, preds, res, t in rows:
    for p in preds:
        succ[p].append(f)
lf = {}
for f, lvl, name, h, preds, res, t in reversed(rows):
    if t == "S":
        continue
    lf[f] = min([lf[s] - (ef[s] - es[s]) for s in succ[f]], default=proj_end)
critical = {f for f in lf if abs(lf[f] - ef[f]) < 1e-9}

def dt(hours):
    return (START + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")

def dur(hours):
    return f"PT{int(hours)}H0M0S"

NS = "http://schemas.microsoft.com/project"
ET.register_namespace("", NS)
def sub(parent, tag, text=None):
    e = ET.SubElement(parent, f"{{{NS}}}{tag}")
    if text is not None:
        e.text = str(text)
    return e

proj = ET.Element(f"{{{NS}}}Project")
sub(proj, "SaveVersion", 14)
sub(proj, "Name", "Parada Chancador Primario")
sub(proj, "Title", "Parada Chancador Primario")
sub(proj, "ScheduleFromStart", 1)
sub(proj, "StartDate", dt(0))
sub(proj, "FinishDate", dt(proj_end))
sub(proj, "CalendarUID", 1)
sub(proj, "DefaultStartTime", "00:00:00")
sub(proj, "DefaultFinishTime", "00:00:00")
sub(proj, "MinutesPerDay", 1440)
sub(proj, "MinutesPerWeek", 10080)
sub(proj, "DaysPerMonth", 30)
sub(proj, "DurationFormat", 5)
sub(proj, "WorkFormat", 2)

cals = sub(proj, "Calendars")
cal = sub(cals, "Calendar")
sub(cal, "UID", 1)
sub(cal, "Name", "24 Horas")
sub(cal, "IsBaseCalendar", 1)
sub(cal, "BaseCalendarUID", -1)
wds = sub(cal, "WeekDays")
for d in range(1, 8):
    wd = sub(wds, "WeekDay")
    sub(wd, "DayType", d)
    sub(wd, "DayWorking", 1)
    wts = sub(wd, "WorkingTimes")
    wt = sub(wts, "WorkingTime")
    sub(wt, "FromTime", "00:00:00")
    sub(wt, "ToTime", "00:00:00")

tasks = sub(proj, "Tasks")
t0 = sub(tasks, "Task")
sub(t0, "UID", 0); sub(t0, "ID", 0); sub(t0, "Name", "Parada Chancador Primario")
sub(t0, "OutlineLevel", 0); sub(t0, "Summary", 1)
sub(t0, "Start", dt(0)); sub(t0, "Finish", dt(proj_end))

counters = {}
for f, lvl, name, h, preds, res, t in rows:
    # código EDT
    counters[lvl] = counters.get(lvl, 0) + 1
    for k in list(counters):
        if k > lvl:
            del counters[k]
    wbs = ".".join(str(counters[k]) for k in sorted(counters))
    d = ef[f] - es[f]
    tk = sub(tasks, "Task")
    sub(tk, "UID", f); sub(tk, "ID", f); sub(tk, "Name", name)
    sub(tk, "WBS", wbs); sub(tk, "OutlineNumber", wbs); sub(tk, "OutlineLevel", lvl)
    sub(tk, "Type", 1)  # duración fija
    sub(tk, "Start", dt(es[f])); sub(tk, "Finish", dt(ef[f]))
    sub(tk, "Duration", dur(d)); sub(tk, "DurationFormat", 5)
    sub(tk, "Milestone", 1 if t == "M" else 0)
    sub(tk, "Summary", 1 if t == "S" else 0)
    sub(tk, "Critical", 1 if f in critical or (t == "S") else 0)
    sub(tk, "ConstraintType", 0)
    sub(tk, "CalendarUID", -1)
    for p in preds:
        pl = sub(tk, "PredecessorLink")
        sub(pl, "PredecessorUID", p)
        sub(pl, "Type", 1)  # fin-comienzo
        sub(pl, "LinkLag", 0)
        sub(pl, "LagFormat", 5)

rs = sub(proj, "Resources")
for name, mx, rt in resources:
    r = sub(rs, "Resource")
    sub(r, "UID", res_uid[name]); sub(r, "ID", res_uid[name]); sub(r, "Name", name)
    sub(r, "Type", 1)
    sub(r, "MaxUnits", f"{mx:.2f}")
    sub(r, "StandardRate", rt); sub(r, "StandardRateFormat", 2)
    sub(r, "OvertimeRate", 0); sub(r, "OvertimeRateFormat", 2)
    sub(r, "CostPerUse", 0); sub(r, "AccrueAt", 3)
    sub(r, "CalendarUID", 1)

asg = sub(proj, "Assignments")
auid = 1
for f, lvl, name, h, preds, res, t in rows:
    for rname, units in res:
        a = sub(asg, "Assignment")
        sub(a, "UID", auid); auid += 1
        sub(a, "TaskUID", f); sub(a, "ResourceUID", res_uid[rname])
        sub(a, "Units", f"{units:.2f}")
        sub(a, "Work", dur(h * units))
        sub(a, "Cost", h * units * rate[rname])
        sub(a, "Start", dt(es[f])); sub(a, "Finish", dt(ef[f]))

ET.indent(proj)
ET.ElementTree(proj).write("parada_chancador_primario.xml", encoding="UTF-8", xml_declaration=True)

print("Fin del proyecto (h):", proj_end, "->", dt(proj_end))
print("Ruta crítica:", sorted(f for f in critical if f in lf))

tot = {}
for f, lvl, name, h, preds, res, t in rows:
    for rname, units in res:
        tot[rname] = tot.get(rname, 0) + h * units * rate[rname]
for k, v in tot.items(): print(k, v)
print("TOTAL", sum(tot.values()))
