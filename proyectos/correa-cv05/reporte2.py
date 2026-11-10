import io, glob
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Patch, Polygon
from datetime import timedelta
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datos import *

for f in fm.findSystemFonts():
    if "Inter" in f: fm.fontManager.addfont(f)
plt.rcParams.update({"font.family":"Inter","font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "axes.edgecolor":"#c9c8c3","xtick.color":"#52514e","ytick.color":"#52514e","axes.labelcolor":"#52514e",
 "axes.grid":True,"grid.color":"#ecebe7","axes.axisbelow":True})
INK,INK2,MUTED="#0b0b0b","#52514e","#8a8984"; BLUE,ORANGE,GRAY,RED="#2a78d6","#eb6834","#c9c8c3","#d03b3b"
MES=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
fs,ff=pronostico(); FEND=max(ff.values())
tasks=[r for r in rows if r[7]=="T"]
SPI,CPI=EV/PV,EV/AC
EAC1=BAC/CPI; EAC2=AC+(BAC-EV); EAC3=AC+(BAC-EV)/(CPI*SPI)
def n0(v): return f"{v:,.0f}".replace(",",".")
def n2(v): return f"{v:.2f}".replace(".",",")
def fdate(d): return (START+timedelta(days=d-1)).strftime("%d-%m-%Y")
months=[0,28,59,89,120,150,181,212,242,273,303]
def mticks(ax):
    ax.set_xticks(months); ax.set_xticklabels([MES[(START+timedelta(days=m)).month-1]+(START+timedelta(days=m)).strftime("-%y") for m in months],fontsize=8)
    ax.set_xlim(-5,330)
def to_img(fig):
    b=io.BytesIO(); fig.savefig(b,format="png",dpi=220,bbox_inches="tight",facecolor="white"); plt.close(fig); b.seek(0); return ImageReader(b)

def fig_curvas(w=5.6,h=4.5):
    fig,ax=plt.subplots(figsize=(w,h))
    days=list(range(0,END+1)); hd=list(range(0,CORTE+1))
    lin=lambda s,e,t: 0 if t<=s else (1 if t>=e else (t-s)/(e-s))
    PVc=[sum(r[6]*plan_pct(r[0],t)/100 for r in tasks) for t in days]
    EVc=[sum(r[6]*real[r[0]][2]/100*lin(real[r[0]][0],real[r[0]][1] or CORTE,t) for r in tasks if r[0] in real) for t in hd]
    ACc=[sum(real[r[0]][3]*lin(real[r[0]][0],real[r[0]][1] or CORTE,t) for r in tasks if r[0] in real) for t in hd]
    ax.plot(days,PVc,color=MUTED,lw=2,label="PV · planificado")
    ax.plot(hd,EVc,color=BLUE,lw=2,label="EV · ganado")
    ax.plot(hd,ACc,color=ORANGE,lw=2,label="AC · costo real")
    ax.plot([CORTE,FEND],[AC,EAC1],color=ORANGE,lw=1.2,ls=(0,(3,2)))
    ax.plot([FEND],[EAC1],"o",color=ORANGE,ms=5,mec="white",mew=1.2); ax.text(FEND-4,EAC1+280,f"EAC {n0(EAC1)}",ha="right",fontsize=7.5,color=INK)
    ax.plot([END],[BAC],"o",color=MUTED,ms=5,mec="white",mew=1.2); ax.text(END-4,BAC-700,f"BAC {n0(BAC)}",ha="right",fontsize=7.5,color=INK2)
    ax.axvline(CORTE,color=RED,lw=1.1)
    ax.text(CORTE-3,PV+200,f"PV {n0(PV)}",fontsize=7.5,ha="right",color=INK)
    ax.text(CORTE+4,AC+60,f"AC {n0(AC)}",fontsize=7.5,color=INK)
    ax.text(CORTE+4,EV-420,f"EV {n0(EV)}",fontsize=7.5,color=INK)
    mticks(ax); ax.tick_params(axis="x",labelsize=7)
    ax.set_ylim(0,8200); ax.set_ylabel("MM$ acumulados")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:n0(v)))
    ax.legend(loc="upper left",frameon=False,fontsize=7.5)
    return fig

def fig_gantt():
    fig,ax=plt.subplots(figsize=(11.6,6.9))
    disp=[r for r in rows if r[1]>=2]; labels=[]
    for y,(f,l,e,n,d,p,b,t) in enumerate(disp):
        if t=="S": labels.append((n.upper(),True)); continue
        labels.append((n,False))
        if t=="M":
            for x,c,z in [(es[f],MUTED,3),(fs[f],INK,4)]:
                ax.add_patch(Polygon([[x,y-.3],[x+2,y],[x,y+.3],[x-2,y]],color=c,lw=0,zorder=z))
            continue
        ax.barh(y+0.22,ef[f]-es[f],left=es[f],height=0.22,color=GRAY,lw=0,zorder=2)
        c=ORANGE if f in crit else BLUE
        if f in real and real[f][1] is not None:
            ax.barh(y-0.08,ff[f]-fs[f],left=fs[f],height=0.42,color=c,lw=0,zorder=3)
        elif f in real:
            ax.barh(y-0.08,CORTE-fs[f],left=fs[f],height=0.42,color=c,lw=0,zorder=3)
            ax.barh(y-0.08,ff[f]-CORTE,left=CORTE,height=0.42,color="white",edgecolor=c,hatch="////",lw=0.8,zorder=3)
            ax.text(ff[f]+2,y-0.08,f"{real[f][2]}%",va="center",fontsize=7.5,color=INK2)
        else:
            ax.barh(y-0.08,ff[f]-fs[f],left=fs[f],height=0.42,color="white",edgecolor=c,hatch="////",lw=0.8,zorder=3)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels([l for l,_ in labels],fontsize=7.6)
    for tl,(_,bb) in zip(ax.get_yticklabels(),labels):
        if bb: tl.set_fontweight("bold"); tl.set_color(INK)
    ax.invert_yaxis(); ax.set_ylim(len(labels)-.4,-1.6); ax.grid(axis="y",visible=False)
    ax.axvline(CORTE,color=RED,lw=1.2,zorder=5); ax.text(CORTE+2,-1.1,"Corte 23-05-2027",color=RED,fontsize=8,fontweight="bold",va="center")
    ax.axvline(END,color=MUTED,lw=0.9,ls=(0,(3,2))); ax.axvline(FEND,color=INK,lw=0.9,ls=(0,(3,2)))
    ax.text(END-2,-1.1,"Fin base\n14-10",ha="right",fontsize=7.5,color=INK2,va="center")
    ax.text(FEND+2,-1.1,"Fin pronosticado\n02-11 (+19 d)",ha="left",fontsize=7.5,color=INK,va="center")
    mticks(ax)
    ax.legend(handles=[Patch(color=GRAY,label="Línea base"),Patch(color=BLUE,label="Real"),Patch(color=ORANGE,label="Real, ruta crítica"),
      Patch(facecolor="white",edgecolor=BLUE,hatch="////",label="Pendiente / pronóstico")],loc="lower left",bbox_to_anchor=(0,1.0),ncol=4,frameon=False,fontsize=8)
    return fig

started=[r for r in tasks if r[0] in real]
def row_ev(r):
    f=r[0]; b=r[6]; pv=b*plan_pct(f)/100; ev=b*real[f][2]/100; ac=real[f][3]
    return pv,ev,ac
def fig_var():
    data=[(r[3],)+row_ev(r) for r in started]
    data.sort(key=lambda x:(x[2]-x[1]))  # SV asc
    names=[d[0] for d in data]
    fig,axs=plt.subplots(1,2,figsize=(11.6,3.6),sharey=True)
    for ax,(title,vals) in zip(axs,[("Variación de programa SV = EV − PV (MM$)",[d[2]-d[1] for d in data]),
                                     ("Variación de costo CV = EV − AC (MM$)",[d[2]-d[3] for d in data])]):
        cols=[ORANGE if v<0 else BLUE for v in vals]
        ax.barh(names,vals,color=cols,height=0.6,lw=0,zorder=3)
        ax.axvline(0,color=INK2,lw=0.8)
        lim=max(abs(v) for v in vals)*1.35
        ax.set_xlim(-lim,lim*0.45)
        for i,v in enumerate(vals):
            if abs(v)>=0.5:
                ax.text(v-(lim*0.02 if v<0 else -lim*0.02),i,n0(v) if v>0 else "−"+n0(-v),va="center",ha="right" if v<0 else "left",fontsize=7.5,color=INK)
            else:
                ax.text(lim*0.02,i,"0",va="center",fontsize=7.5,color=MUTED)
        ax.set_title(title,loc="left",fontsize=9.5,fontweight="bold",color=INK)
        ax.grid(axis="y",visible=False); ax.tick_params(axis="y",labelsize=7.8)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:n0(v)))
    return fig
def fig_eac():
    items=[("Optimista: el sobrecosto no se repite\nAC + (BAC − EV)",EAC2),("Tendencia de costo\nBAC ÷ CPI",EAC1),
           ("Pesimista: costo y atraso se combinan\nAC + (BAC − EV) ÷ (CPI × SPI)",EAC3)]
    fig,ax=plt.subplots(figsize=(5.6,2.6))
    ax.barh([i[0] for i in items],[i[1] for i in items],color=[GRAY,ORANGE,GRAY],height=0.55,lw=0,zorder=3)
    ax.axvline(BAC,color=INK,lw=1,ls=(0,(3,2))); ax.text(BAC+40,-0.5,f"BAC {n0(BAC)}",ha="left",fontsize=7.5,color=INK)
    for i,(nm,v) in enumerate(items): ax.text(v+60,i,f"{n0(v)}  (+{n0(v-BAC)})",va="center",fontsize=7.8,color=INK)
    ax.set_xlim(6000,8900); ax.invert_yaxis(); ax.grid(axis="y",visible=False); ax.tick_params(axis="y",labelsize=7.4)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:n0(v)))
    ax.set_xlabel("Costo final estimado (MM$)")
    return fig

# ---------- PDF ----------
def reg(name, pat):
    c=[p for p in glob.glob("/usr/share/fonts/**/*",recursive=True) if p.endswith(pat)]
    if c: pdfmetrics.registerFont(TTFont(name,c[0])); return True
F,FB=("Inter","Inter-Bold") if reg("Inter","Inter-Regular.ttf") and reg("Inter-Bold","Inter-Bold.ttf") else ("Sans","Sans-Bold")
if F=="Sans": reg("Sans","DejaVuSans.ttf"); reg("Sans-Bold","DejaVuSans-Bold.ttf")
W,H=landscape(A4); M=14*mm
c=canvas.Canvas("Informe_Valor_Ganado_Correa_CV05.pdf",pagesize=(W,H))
c.setTitle("Informe de control con valor ganado – Correa Transportadora CV-05"); c.setAuthor("Diego Ojeda")
pg=[0]; TOT=4
def rgb(h): h=h.lstrip("#"); return [int(h[i:i+2],16)/255 for i in (0,2,4)]
def header(t,s):
    pg[0]+=1
    c.setFillColorRGB(*rgb(INK)); c.setFont(FB,17); c.drawString(M,H-M-6*mm,t)
    c.setFont(F,9.5); c.setFillColorRGB(*rgb(INK2)); c.drawString(M,H-M-12*mm,s)
    c.setStrokeColorRGB(*rgb("#e2e1dc")); c.setLineWidth(0.6); c.line(M,H-M-15*mm,W-M,H-M-15*mm)
    c.setFont(F,7.5); c.setFillColorRGB(*rgb(MUTED))
    c.drawString(M,M-6*mm,"Correa Transportadora CV-05 · Informe de control al 23-05-2027 · Datos referenciales para portafolio")
    c.drawRightString(W-M,M-6*mm,f"{pg[0]} / {TOT}")
def sec(x,y,t): c.setFont(FB,10.5); c.setFillColorRGB(*rgb(INK)); c.drawString(x,y,t)
def img(fig,x,ytop,w):
    im=to_img(fig); iw,ih=im.getSize(); h=w*ih/iw; c.drawImage(im,x,ytop-h,w,h); return h
def para(x,y,text,w,size=8.6,lead=12,color=INK2,font=None):
    from reportlab.lib.utils import simpleSplit
    c.setFont(font or F,size); c.setFillColorRGB(*rgb(color))
    for line in simpleSplit(text,font or F,size,w): c.drawString(x,y,line); y-=lead
    return y

# Página 1
header("Correa transportadora CV-05 · Control con valor ganado","Informe de estado al 23-05-2027 (semana 20 de 41) · Línea base 04-01-2027 a 14-10-2027 · Presupuesto 7.080 MM$")
kp=[("SPI · índice de programa",n2(SPI),f"Avanzó {SPI*100:.0f}% de lo planificado",True),
    ("CPI · índice de costo",n2(CPI),f"Gasta ${1/CPI:.2f} por $1 ganado".replace(".",","),True),
    ("Avance real vs. planificado",f"{EV/BAC*100:.0f}% / {PV/BAC*100:.0f}%".replace(".",","),"EV ÷ BAC  vs.  PV ÷ BAC",False),
    ("Costo final estimado (EAC)",f"{n0(EAC1)} MM$",f"{n0(EAC1-BAC)} MM$ sobre presupuesto",True),
    ("Término pronosticado","02-11-2027",f"{FEND-END} días después de la línea base",True)]
top=H-M-22*mm; bw=(W-2*M-16*mm)/5
for i,(lab,val,sub,bad) in enumerate(kp):
    x=M+i*(bw+4*mm)
    c.setFillColorRGB(*rgb("#f8f7f4")); c.roundRect(x,top-26*mm,bw,26*mm,3*mm,stroke=0,fill=1)
    if bad:
        c.setFillColorRGB(*rgb(ORANGE)); c.circle(x+bw-5*mm,top-5.5*mm,1.4*mm,stroke=0,fill=1)
    c.setFillColorRGB(*rgb(INK2)); c.setFont(F,8); c.drawString(x+4*mm,top-6*mm,lab)
    c.setFillColorRGB(*rgb(INK)); c.setFont(FB,18); c.drawString(x+4*mm,top-15.5*mm,val)
    c.setFillColorRGB(*rgb(MUTED)); c.setFont(F,7.5); c.drawString(x+4*mm,top-21.5*mm,sub)
y=top-34*mm; colw=(W-2*M-10*mm)/2
sec(M,y,"Curvas de valor ganado (MM$ acumulados)")
img(fig_curvas(),M,y-3*mm,colw)
x2=M+colw+10*mm
sec(x2,y,"Conclusiones")
yy=y-7*mm
for t in ["El proyecto va atrasado y con sobrecosto. El EV queda bajo el PV (atraso de 515 MM$ de trabajo) y bajo el AC (sobrecosto de 246 MM$).",
          "El término se mueve 19 días, al 02-11-2027. La causa es el despacho del motor, reductor y sala eléctrica, en ruta crítica: 5 días vienen de la ingeniería aprobada tarde y 14 del atraso del proveedor.",
          "El sobrecosto viene de obras civiles: roca no prevista en el movimiento de tierras (+20%) y mayor costo en fundaciones. Encareció el proyecto pero no lo atrasó, porque esas actividades tenían holgura.",
          "Recuperar el presupuesto exigiría un TCPI de "+n2((BAC-EV)/(BAC-AC))+", es decir, trabajar un 9% más eficiente que lo planificado en todo lo que queda. No es realista: se recomienda informar el EAC de "+n0(EAC1)+" MM$ como nuevo costo esperado."]:
    c.setFillColorRGB(*rgb(BLUE)); c.circle(x2+1.2*mm,yy+1.1*mm,0.9*mm,stroke=0,fill=1)
    yy=para(x2+4*mm,yy,t,colw-4*mm,size=8.8,lead=12.2,color=INK)-5
c.setFont(F,7.5); c.setFillColorRGB(*rgb(MUTED))
c.drawString(M,M+1*mm,"Historia de EV y AC estimada con avance parejo entre el comienzo real de cada actividad y el corte. PV según línea base.")
c.showPage()

# Página 2
header("Seguimiento del programa","Línea base (barra gris) contra real y pronóstico · El trabajo pendiente se reprograma desde la fecha de corte")
img(fig_gantt(),M,H-M-19*mm,W-2*M)
c.showPage()

# Página 3
header("Desviaciones por actividad","Las 10 actividades iniciadas al corte · Valores en MM$")
h=img(fig_var(),M,H-M-20*mm,W-2*M)
cols=[("Actividad",86),("Presup.",17),("% plan.",15),("% real",15),("PV",17),("EV",17),("AC",17),("SV",17),("CV",17),("SPI",13),("CPI",13),("Crítica",15)]
yy=H-M-24*mm-h; x0=M
c.setFont(FB,7.6); c.setFillColorRGB(*rgb(INK2)); xx=x0
for nm,w in cols:
    (c.drawString if nm=="Actividad" else (lambda X,Y,T: c.drawRightString(X+(w-3)*mm,Y,T)))(xx,yy,nm); xx+=w*mm
yy-=2*mm; c.setStrokeColorRGB(*rgb(GRAY)); c.line(x0,yy,W-M,yy)
order=sorted(started,key=lambda r:r[0])
tot=[0,0,0,0]
for r in order:
    pv,ev,ac=row_ev(r); yy-=4.6*mm; f=r[0]
    tot=[tot[0]+r[6],tot[1]+pv,tot[2]+ev,tot[3]+ac]
    vals=[r[3],n0(r[6]),f"{plan_pct(f):.0f}%",f"{real[f][2]}%",n0(pv),n0(ev),n0(ac),n0(ev-pv),n0(ev-ac),n2(ev/pv),n2(ev/ac),"Sí" if f in crit else ""]
    xx=x0
    for (nm,w),v in zip(cols,vals):
        neg=nm in("SV","CV") and v.startswith("-") or nm in("SPI","CPI") and float(v.replace(",","."))<1
        c.setFont(FB if (neg or (nm=="Crítica" and v)) else F,7.5)
        c.setFillColorRGB(*rgb("#b4471c" if neg else INK))
        if nm=="Actividad": c.drawString(xx,yy,v)
        else: c.drawRightString(xx+(w-3)*mm,yy,v.replace("-","−"))
        xx+=w*mm
yy-=2*mm; c.line(x0,yy,W-M,yy); yy-=4.4*mm
vals=["Total actividades iniciadas",n0(tot[0]),"","",n0(PV),n0(EV),n0(AC),n0(EV-PV),n0(EV-AC),n2(SPI),n2(CPI),""]
xx=x0
for (nm,w),v in zip(cols,vals):
    c.setFont(FB,7.6); c.setFillColorRGB(*rgb(INK))
    if nm=="Actividad": c.drawString(xx,yy,v)
    else: c.drawRightString(xx+(w-3)*mm,yy,v.replace("-","−"))
    xx+=w*mm
c.showPage()

# Página 4
header("Pronóstico y acciones","Tres formas de estimar el costo final y las acciones propuestas para recuperar el plazo")
y=H-M-23*mm
sec(M,y,"Costo final estimado según supuesto (MM$)")
he=img(fig_eac(),M,y-3*mm,colw)
para(M,y-3*mm-he-8*mm,"El rango va de "+n0(EAC2)+" a "+n0(EAC3)+" MM$. Se informa el método BAC ÷ CPI porque el sobrecosto viene de una causa (la roca) que podría repetirse en otras excavaciones. El método pesimista sirve como alerta si el atraso obliga a pagar aceleraciones.",colw,size=8.6)
sec(x2,y,"Acciones propuestas")
acts=[("Proveedor del motor y sala eléctrica","Gestión de seguimiento en fábrica (expediting) con informe semanal y fecha comprometida. Cada día recuperado aquí adelanta el término del proyecto."),
      ("Montaje de la estación motriz","Preparar el montaje en paralelo con la llegada de equipos: premontar poleas y bases, y tener grúa y cuadrilla listas para empezar el mismo día de la llegada."),
      ("Pruebas y puesta en marcha","Evaluar pruebas eléctricas por sectores antes del conexionado final para acortar la ruta crítica al cierre."),
      ("Costo","Revisar el estudio de suelos para el resto del trazado y reservar contingencia por roca; congelar cambios de alcance no esenciales."),
      ("Control","Mantener cortes semanales de avance y costo para medir si las acciones mejoran el SPI y el CPI en las próximas 4 semanas.")]
yy=y-7*mm
for t,dsc in acts:
    c.setFont(FB,9); c.setFillColorRGB(*rgb(INK)); c.drawString(x2,yy,t); yy-=11.5
    yy=para(x2,yy,dsc,colw,size=8.5,lead=11.5)-6
yb=M+20*mm
sec(M,yb+6*mm,"Respaldo de plazos")
para(M,yb,"Los plazos del caso se calibraron con proyectos publicados: Lumwana, Zambia (sistema de correas con overland de 3,4 km, 15 meses; E&MJ); CV006, Fortescue, Australia (4,8 km, 7 meses, unas 65.000 HH en terreno; Linkforce); y la licitación de ENAMI para una correa en Planta Matta, Copiapó (270 días corridos para fabricación, suministro y supervisión de montaje; Portal Minero).",W-2*M,size=8,lead=11)
c.showPage(); c.save()
print("ok",n0(EAC1),n0(EAC2),n0(EAC3))
