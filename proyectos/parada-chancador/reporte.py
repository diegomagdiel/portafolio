import runpy, io
from datetime import timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, Polygon
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

g = runpy.run_path("gen_xml.py")
rows, es, ef, lf, rate, START = g["rows"], g["es"], g["ef"], g["lf"], g["rate"], g["START"]
critical, proj_end = g["critical"], g["proj_end"]
WINDOW = 72

# ---------- estilo ----------
for f in fm.findSystemFonts():
    if "Inter" in f:
        fm.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": "Inter", "font.size": 9, "axes.edgecolor": "#c9c8c3",
    "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#ecebe7", "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.facecolor": "white", "axes.facecolor": "white",
})
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
NIGHT = "#f3f2ee"

def clp(v): return "$" + f"{v:,.0f}".replace(",", ".")
def hlabel(h): return (START + timedelta(hours=h)).strftime("%a %d %H:%M").replace("Mon", "Lun").replace("Tue", "Mar").replace("Wed", "Mié").replace("Thu", "Jue")

def shade_shifts(ax, end):
    h = 0
    while h < end:
        if ((START.hour + h) % 24) >= 19 or ((START.hour + h) % 24) < 7:
            pass
        h += 12
    # turnos: día 07-19, noche 19-07 (el inicio es 07:00)
    for k in range(0, int(end // 12) + 2):
        if k % 2 == 1:
            ax.axvspan(k * 12, (k + 1) * 12, color=NIGHT, zorder=0, lw=0)

def day_ticks(ax, end):
    ticks = list(range(0, int(end) + 13, 12))
    ax.set_xticks(ticks)
    ax.set_xticklabels([(START + timedelta(hours=t)).strftime("%d/%m\n%H:%M") for t in ticks], fontsize=7.5)
    ax.set_xlim(0, end)

def to_img(fig, dpi=220):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return ImageReader(buf)

# ---------- datos ----------
tasks = [r for r in rows if r[6] != "S"]
work_tasks = [r for r in rows if r[6] == "T"]
phase_of = {}
cur = None
for f, lvl, name, h, preds, res, t in rows:
    if t == "S" and lvl == 2:
        cur = name
    elif t != "S":
        phase_of[f] = cur or "Inicio"

hours = list(range(0, proj_end + 1))
def per_hour(fn):
    out = [0.0] * proj_end
    for f, lvl, name, h, preds, res, t in work_tasks:
        for hh in range(es[f], ef[f]):
            out[hh] += fn(f, res)
    return out

cost_h = per_hour(lambda f, res: sum(u * rate[r] for r, u in res))
hh_h = per_hour(lambda f, res: sum(u for r, u in res if r != "Grúa"))
total_cost = sum(cost_h)
total_hh = sum(hh_h)
cum_cost = [0]
for v in cost_h: cum_cost.append(cum_cost[-1] + v)
cum_pct = [0]
for v in hh_h: cum_pct.append(cum_pct[-1] + v / total_hh * 100)

groups = [("Mecánicos", ["Mecánicos"], BLUE), ("Soldadores", ["Soldadores"], ORANGE),
          ("Ayudantes", ["Ayudantes"], AQUA), ("Eléctricos", ["Eléctricos"], YELLOW),
          ("Otros", ["Andamieros", "Supervisor", "Prevencionista", "Inspector", "Operador"], MAGENTA)]
grp_h = {name: per_hour(lambda f, res, m=members: sum(u for r, u in res if r in m)) for name, members, _ in groups}

dur_h = per_hour(lambda f, res: 1)
total_dur = sum(dur_h)
cum_dur = [0]
for v in dur_h: cum_dur.append(cum_dur[-1] + v / total_dur * 100)
h50 = next(i for i, v in enumerate(cum_pct) if v >= 50)
h50d = next(i for i, v in enumerate(cum_dur) if v >= 50)
gap = [abs(a - b) for a, b in zip(cum_pct, cum_dur)]
gmax = max(gap); ghr = gap.index(gmax)
n_crit = sum(1 for r in work_tasks if r[0] in critical)

# ---------- gráficos ----------
def fig_gantt():
    disp = [r for r in rows if r[1] >= 2]
    fig, ax = plt.subplots(figsize=(11.2, 7.0))
    shade_shifts(ax, WINDOW + 4)
    y = 0
    ylabels, yticks = [], []
    for f, lvl, name, h, preds, res, t in disp:
        if t == "S":
            ax.add_patch(Rectangle((es[f], y - 0.12), ef[f] - es[f], 0.24, color=INK, lw=0, zorder=3))
            for x in (es[f], ef[f]):
                ax.add_patch(Polygon([[x - 0.5, y + 0.12], [x + 0.5, y + 0.12], [x, y + 0.42]], color=INK, lw=0, zorder=3))
            ylabels.append(name.upper());
        elif t == "M":
            x = es[f]
            ax.add_patch(Polygon([[x, y - 0.38], [x + 0.9, y], [x, y + 0.38], [x - 0.9, y]], color=INK, lw=0, zorder=4))
            ax.text(x + 1.4, y, hlabel(x), va="center", fontsize=7, color=INK2)
            ylabels.append(name)
        else:
            c = ORANGE if f in critical else BLUE
            ax.barh(y, ef[f] - es[f], left=es[f], height=0.62, color=c, lw=0, zorder=3)
            if f not in critical:
                slack = lf[f] - ef[f]
                ax.plot([ef[f], ef[f] + slack], [y, y], color=MUTED, lw=1, ls=(0, (2, 2)), zorder=2)
            ylabels.append(name)
        yticks.append(y)
        y += 1
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=7.6)
    for lbl, (f, lvl, *_rest) in zip(ax.get_yticklabels(), disp):
        if _rest[-1] == "S":
            lbl.set_fontweight("bold"); lbl.set_color(INK)
    ax.invert_yaxis()
    ax.set_ylim(y - 0.4, -0.7)
    ax.axvline(WINDOW, color="#d03b3b", lw=1.2, zorder=5)
    ax.text(WINDOW + 0.5, y - 1.2, "Ventana\n72 h", ha="left", va="center", fontsize=7.5, color="#d03b3b", fontweight="bold")
    ax.axvline(proj_end, color=INK, lw=0.8, ls=(0, (3, 2)), zorder=5)
    ax.text(proj_end + 0.6, 2.5, "Término\nprogramado\n61 h", ha="left", va="center", fontsize=7.5, color=INK)
    day_ticks(ax, WINDOW + 4)
    ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    ax.legend(handles=[Patch(color=ORANGE, label="Ruta crítica"), Patch(color=BLUE, label="No crítica"),
                       Line2D([0], [0], color=MUTED, ls=(0, (2, 2)), label="Holgura total"),
                       Patch(color=NIGHT, label="Turno noche (19:00–07:00)")],
              loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4, fontsize=7.5, frameon=False)
    return fig

def fig_scurve(series, ylabel, fmt, title_val, second=None):
    fig, ax = plt.subplots(figsize=(5.4, 3.9))
    shade_shifts(ax, proj_end)
    ax.plot(hours, series, color=BLUE, lw=2, zorder=3, label="Ponderado por horas hombre")
    if second is not None:
        ax.plot(hours, second, color=ORANGE, lw=2, zorder=3, label="Ponderado por duración")
        ax.legend(loc="lower right", fontsize=7.5, frameon=True, facecolor="white", edgecolor="#e2e1dc")
    for pct in ((50,) if second is not None else (25, 50, 75)):
        target = series[-1] * pct / 100
        hx = next(i for i, v in enumerate(series) if v >= target)
        ax.plot([hx], [series[hx]], "o", ms=5, color=BLUE, mec="white", mew=1.2, zorder=4)
        ax.annotate(f"{pct}% · h {hx}", (hx, series[hx]), xytext=(-6, 8), textcoords="offset points",
                    ha="right", fontsize=7, color=INK2)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(fmt))
    ax.set_ylim(0, series[-1] * 1.05)
    day_ticks(ax, proj_end)
    return fig

def fig_hist():
    fig, ax = plt.subplots(figsize=(11.2, 2.7))
    shade_shifts(ax, proj_end)
    bottom = [0] * proj_end
    for name, _, c in groups:
        vals = grp_h[name]
        ax.bar([h + 0.5 for h in range(proj_end)], vals, width=0.92, bottom=bottom, color=c, lw=0, label=name, zorder=3)
        bottom = [b + v for b, v in zip(bottom, vals)]
    peak = max(bottom); ph = bottom.index(peak)
    ax.annotate(f"Máximo: {peak:.0f} personas (hora {ph})", (ph + 0.5, peak), xytext=(10, 4),
                textcoords="offset points", fontsize=7.5, color=INK)
    ax.set_ylabel("Personas en terreno")
    ax.set_ylim(0, peak * 1.2)
    day_ticks(ax, proj_end)
    ax.legend(ncol=5, loc="upper right", fontsize=7.5, frameon=False, bbox_to_anchor=(1, 1.16))
    return fig

def fig_hbar(items, title, color=BLUE):
    items = sorted(items, key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(5.4, 2.55))
    names = [i[0] for i in items]; vals = [i[1] for i in items]
    ax.barh(names, vals, color=color, height=0.6, lw=0, zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.015, i, clp(v), va="center", fontsize=7.5, color=INK)
    ax.set_xlim(0, max(vals) * 1.28)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v/1e6:.0f} M"))
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", labelsize=8)
    return fig

# costos por fase y recurso
by_phase, by_res = {}, {}
for f, lvl, name, h, preds, res, t in work_tasks:
    for r, u in res:
        c = h * u * rate[r]
        by_phase[phase_of[f]] = by_phase.get(phase_of[f], 0) + c
        by_res[r] = by_res.get(r, 0) + c

# ---------- PDF ----------
for nm, fn in [("Inter", "Inter-Regular.otf"), ("Inter-Bold", "Inter-Bold.otf"), ("Inter-SemiBold", "Inter-SemiBold.otf")]:
    pass
fontdir = "/usr/share/fonts/truetype/"
import glob
def reg(name, pattern):
    cand = [p for p in glob.glob("/usr/share/fonts/**/*", recursive=True) if p.endswith(pattern)]
    pdfmetrics.registerFont(TTFont(name, cand[0]))
try:
    reg("Sans", "DejaVuSans.ttf"); reg("Sans-Bold", "DejaVuSans-Bold.ttf")
except Exception:
    pass
for cand_name, pat in [("Inter", "Inter-Regular.ttf"), ("Inter-Bold", "Inter-Bold.ttf")]:
    try: reg(cand_name, pat)
    except Exception: pass
FONT = "Inter" if "Inter" in pdfmetrics.getRegisteredFontNames() else "Sans"
FONTB = "Inter-Bold" if "Inter-Bold" in pdfmetrics.getRegisteredFontNames() else "Sans-Bold"

W, H = landscape(A4)
M = 14 * mm
c = canvas.Canvas("Reporte_Parada_Chancador_Primario.pdf", pagesize=(W, H))
c.setTitle("Reporte de planificación – Parada Chancador Primario")
c.setAuthor("Diego Ojeda")
pages_total = 4
page_no = [0]

def header(title, subtitle):
    page_no[0] += 1
    c.setFillColor(matplotlib.colors.to_hex(INK))
    c.setFont(FONTB, 17); c.drawString(M, H - M - 6 * mm, title)
    c.setFont(FONT, 9.5); c.setFillColorRGB(0.32, 0.32, 0.31)
    c.drawString(M, H - M - 12 * mm, subtitle)
    c.setStrokeColorRGB(0.89, 0.88, 0.86); c.setLineWidth(0.6)
    c.line(M, H - M - 15 * mm, W - M, H - M - 15 * mm)
    c.setFont(FONT, 7.5); c.setFillColorRGB(0.54, 0.54, 0.52)
    c.drawString(M, M - 6 * mm, "Parada Chancador Primario · Programa línea base · Datos referenciales para portafolio")
    c.drawRightString(W - M, M - 6 * mm, f"{page_no[0]} / {pages_total}")

def section(x, y, text):
    c.setFont(FONTB, 10.5); c.setFillColorRGB(0.04, 0.04, 0.04); c.drawString(x, y, text)

def img(fig, x, y_top, w):
    im = to_img(fig)
    iw, ih = im.getSize()
    h = w * ih / iw
    c.drawImage(im, x, y_top - h, w, h)
    return h

# --- Página 1: resumen ---
header("Parada de planta · Chancador primario", f"Reporte de planificación · Línea base · Inicio {START.strftime('%d-%m-%Y %H:%M')} · Calendario continuo 24/7, turnos de 12 h")
kpis = [("Duración programada", f"{proj_end} h", f"de {WINDOW} h de ventana"),
        ("Margen sobre ventana", f"{WINDOW - proj_end} h", f"{(WINDOW - proj_end) / WINDOW * 100:.0f}% de colchón"),
        ("Costo mano de obra y grúa", f"$ {total_cost/1e6:.1f} M".replace(".", ","), f"{clp(total_cost)} CLP, sin repuestos"),
        ("Horas hombre", f"{total_hh:.0f} HH", "sin contar grúa"),
        ("Actividades críticas", f"{n_crit} de {len(work_tasks)}", f"{n_crit / len(work_tasks) * 100:.0f}% en ruta crítica")]
top = H - M - 22 * mm
bw = (W - 2 * M - 4 * 4 * mm) / 5
for i, (lab, val, sub) in enumerate(kpis):
    x = M + i * (bw + 4 * mm)
    c.setFillColorRGB(0.973, 0.971, 0.965); c.roundRect(x, top - 26 * mm, bw, 26 * mm, 3 * mm, stroke=0, fill=1)
    c.setFillColorRGB(0.32, 0.32, 0.31); c.setFont(FONT, 8); c.drawString(x + 4 * mm, top - 6 * mm, lab)
    c.setFillColorRGB(0.04, 0.04, 0.04); c.setFont(FONTB, 19); c.drawString(x + 4 * mm, top - 15.5 * mm, val)
    c.setFillColorRGB(0.54, 0.54, 0.52); c.setFont(FONT, 7.5); c.drawString(x + 4 * mm, top - 21.5 * mm, sub)

y = top - 34 * mm
colw = (W - 2 * M - 8 * mm) / 2
section(M, y, "Curva S de avance planificado (%)")
section(M + colw + 8 * mm, y, "Curva S de costo acumulado (CLP)")
img(fig_scurve(cum_pct, "Avance acumulado", lambda v, p: f"{v:.0f}%", None, second=cum_dur), M, y - 3 * mm, colw)
img(fig_scurve(cum_cost, "Costo acumulado", lambda v, p: f"{v/1e6:.0f} M", None), M + colw + 8 * mm, y - 3 * mm, colw)
c.setFont(FONT, 8); c.setFillColorRGB(0.32, 0.32, 0.31)
c.drawString(M, M + 2 * mm, f"Lectura: ambas curvas llegan al 50% en la hora {h50} y casi coinciden (diferencia máxima {gmax:.1f} puntos, hora {ghr}), porque casi todas las tareas llevan 2 a 3 personas.")
c.showPage()

# --- Página 2: Gantt ---
header("Programa y ruta crítica", "Diagrama de Gantt por fase · Holgura total en línea punteada · Fondo gris = turno noche")
img(fig_gantt(), M, H - M - 19 * mm, W - 2 * M)
c.showPage()

# --- Página 3: recursos y costos ---
header("Recursos y costos", "Dotación en terreno hora a hora y distribución del costo de la parada")
section(M, H - M - 23 * mm, "Histograma de dotación por hora")
hh = img(fig_hist(), M, H - M - 26 * mm, W - 2 * M)
y2 = H - M - 30 * mm - hh
section(M, y2, "Costo por fase")
section(M + colw + 8 * mm, y2, "Costo por recurso")
img(fig_hbar(list(by_phase.items()), ""), M, y2 - 3 * mm, colw)
img(fig_hbar(list(by_res.items()), ""), M + colw + 8 * mm, y2 - 3 * mm, colw)
c.showPage()

# --- Página 4: tabla ---
header("Detalle de actividades", "Fechas de línea base, duración, holgura total y costo por actividad")
cols = [("Fila", 12), ("Actividad", 92), ("Inicio", 30), ("Fin", 30), ("Dur. (h)", 18), ("Holgura (h)", 22), ("Costo (CLP)", 28), ("Crítica", 16)]
x0 = M; yy = H - M - 24 * mm
c.setFont(FONTB, 7.8); c.setFillColorRGB(0.32, 0.32, 0.31)
xx = x0
for nm, w in cols:
    c.drawString(xx, yy, nm); xx += w * mm
yy -= 2.2 * mm
c.setStrokeColorRGB(0.79, 0.78, 0.76); c.line(x0, yy, W - M, yy)
rh = 4.55 * mm
for i, (f, lvl, name, h, preds, res, t) in enumerate(rows):
    yy -= rh
    if t == "S":
        c.setFillColorRGB(0.95, 0.949, 0.933); c.rect(x0, yy - 1.4 * mm, W - 2 * M, rh, stroke=0, fill=1)
    cost = sum(u * rate[r] for r, u in res) * (h or 0) if t != "S" else sum(
        sum(u * rate[r] for r, u in rr[5]) * (rr[3] or 0) for rr in rows if rr[6] == "T" and es[rr[0]] >= es[f] and ef[rr[0]] <= ef[f] and (lvl == 1 or phase_of.get(rr[0]) == name))
    slack = "" if t == "S" else f"{lf[f] - ef[f]:.0f}"
    crit = "" if t == "S" else ("Sí" if f in critical else "")
    vals = [str(f), ("    " * (lvl - 1)) + name, (START + timedelta(hours=es[f])).strftime("%d-%m %H:%M"),
            (START + timedelta(hours=ef[f])).strftime("%d-%m %H:%M"), f"{ef[f] - es[f]:.0f}", slack,
            clp(cost) if cost else "", crit]
    xx = x0
    for (nm, w), v in zip(cols, vals):
        bold = t == "S" or (nm == "Crítica" and v)
        c.setFont(FONTB if bold else FONT, 7.4)
        if nm == "Crítica" and v:
            c.setFillColor(matplotlib.colors.to_hex(ORANGE)); c.circle(xx + 1.2 * mm, yy + 0.9 * mm, 1.1 * mm, stroke=0, fill=1)
            c.setFillColorRGB(0.04, 0.04, 0.04); c.drawString(xx + 3.2 * mm, yy, v)
        else:
            c.setFillColorRGB(0.04, 0.04, 0.04)
            if nm in ("Dur. (h)", "Holgura (h)", "Costo (CLP)"):
                c.drawRightString(xx + (w - 4) * mm, yy, v)
            else:
                c.drawString(xx, yy, v)
        xx += w * mm
c.showPage()
c.save()
print("ok", total_cost, total_hh, n_crit, by_phase)
