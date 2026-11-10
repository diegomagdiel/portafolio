import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Patch, Polygon
from matplotlib.lines import Line2D
from datetime import timedelta
from datos import *
for f in fm.findSystemFonts():
    if "Inter" in f: fm.fontManager.addfont(f)
plt.rcParams.update({"font.family":"Inter","font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "axes.edgecolor":"#c9c8c3","xtick.color":"#52514e","ytick.color":"#52514e","axes.labelcolor":"#52514e",
 "axes.grid":True,"grid.color":"#ecebe7","axes.axisbelow":True})
INK,INK2,MUTED="#0b0b0b","#52514e","#8a8984"; BLUE,ORANGE,AQUA,GRAY="#2a78d6","#eb6834","#1baf7a","#c9c8c3"
MES=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
fs,ff=pronostico(); FEND=max(ff.values())

fig,(ax,ax2)=plt.subplots(2,1,figsize=(12,11.5),gridspec_kw={"height_ratios":[2.3,1]})
fig.subplots_adjust(hspace=0.28)
disp=[r for r in rows if r[1]>=2]
y=0; labels=[]
for f,l,e,n,d,p,b,t in disp:
    if t=="S":
        labels.append((n.upper(),True))
    elif t=="M":
        x=es[f]; ax.add_patch(Polygon([[x,y-.3],[x+2,y],[x,y+.3],[x-2,y]],color=MUTED,lw=0,zorder=3))
        x=fs[f]; ax.add_patch(Polygon([[x,y-.3],[x+2,y],[x,y+.3],[x-2,y]],color=INK,lw=0,zorder=4))
        labels.append((n,False))
    else:
        ax.barh(y+0.22,ef[f]-es[f],left=es[f],height=0.22,color=GRAY,lw=0,zorder=2)
        c = ORANGE if f in crit else BLUE
        if f in real and real[f][1] is not None:
            ax.barh(y-0.08,ff[f]-fs[f],left=fs[f],height=0.42,color=c,lw=0,zorder=3)
        elif f in real:
            ax.barh(y-0.08,CORTE-fs[f],left=fs[f],height=0.42,color=c,lw=0,zorder=3)
            ax.barh(y-0.08,ff[f]-CORTE,left=CORTE,height=0.42,color="white",edgecolor=c,hatch="////",lw=0.8,zorder=3)
            ax.text(ff[f]+2,y-0.08,f"{real[f][2]}%",va="center",fontsize=7.5,color=INK2)
        else:
            ax.barh(y-0.08,ff[f]-fs[f],left=fs[f],height=0.42,color="white",edgecolor=c,hatch="////",lw=0.8,zorder=3)
        dlt = ff[f]-ef[f]
        if dlt>0 and f not in real: pass
        labels.append((n,False))
    y+=1
ax.set_yticks(range(len(labels))); ax.set_yticklabels([l for l,_ in labels],fontsize=7.6)
for tl,(_,b) in zip(ax.get_yticklabels(),labels):
    if b: tl.set_fontweight("bold"); tl.set_color(INK)
ax.invert_yaxis(); ax.set_ylim(len(labels)-.4,-1.6); ax.grid(axis="y",visible=False)
ax.axvline(CORTE,color="#d03b3b",lw=1.2,zorder=5)
ax.text(CORTE+2,-1.1,"Corte 23-05-2027",color="#d03b3b",fontsize=8,fontweight="bold",va="center")
ax.axvline(END,color=MUTED,lw=0.9,ls=(0,(3,2))); ax.axvline(FEND,color=INK,lw=0.9,ls=(0,(3,2)))
ax.text(END-2,-1.1,"Fin base\n14-10",ha="right",fontsize=7.5,color=INK2,va="center")
ax.text(FEND+2,-1.1,"Fin pronosticado\n02-11 (+19 d)",ha="left",fontsize=7.5,color=INK,va="center")
months=[0,28,59,89,120,150,181,212,242,273,303]
ax.set_xticks(months); ax.set_xticklabels([MES[(START+timedelta(days=m)).month-1]+(START+timedelta(days=m)).strftime("-%y") for m in months],fontsize=8)
ax.set_xlim(-5,330)
ax.legend(handles=[Patch(color=GRAY,label="Línea base"),Patch(color=BLUE,label="Real"),Patch(color=ORANGE,label="Real, ruta crítica"),
  Patch(facecolor="white",edgecolor=BLUE,hatch="////",label="Pendiente / pronóstico")],loc="lower left",bbox_to_anchor=(0,1.0),ncol=4,frameon=False,fontsize=8)
ax.set_title("Seguimiento: línea base vs. real y pronóstico",loc="left",fontsize=12,fontweight="bold",color=INK,pad=26)

# curvas PV / EV / AC (MM$); historia real aproximada lineal entre comienzo real y corte/fin
days=list(range(0,END+1)); tasks=[r for r in rows if r[7]=="T"]
PVc=[sum(r[6]*plan_pct(r[0],t)/100 for r in tasks) for t in days]
def lin(s,e,t): return 0 if t<=s else (1 if t>=e else (t-s)/(e-s))
hd=list(range(0,CORTE+1))
EVc=[sum(r[6]*real[r[0]][2]/100*lin(real[r[0]][0], real[r[0]][1] or CORTE, t) for r in tasks if r[0] in real) for t in hd]
ACc=[sum(real[r[0]][3]*lin(real[r[0]][0], real[r[0]][1] or CORTE, t) for r in tasks if r[0] in real) for t in hd]
ax2.plot(days,PVc,color=MUTED,lw=2,label="PV · valor planificado")
ax2.plot(hd,EVc,color=BLUE,lw=2,label="EV · valor ganado")
ax2.plot(hd,ACc,color=ORANGE,lw=2,label="AC · costo real")
EAC=BAC/(EV/AC)
ax2.plot([CORTE,FEND],[AC,EAC],color=ORANGE,lw=1.2,ls=(0,(3,2)))
ax2.plot([FEND],[EAC],"o",color=ORANGE,ms=6,mec="white",mew=1.2); ax2.text(FEND-3,EAC+250,f"EAC {EAC:,.0f}".replace(",","."),ha="right",fontsize=8,color=INK)
ax2.plot([END],[BAC],"o",color=MUTED,ms=6,mec="white",mew=1.2); ax2.text(END-3,BAC-650,f"BAC {BAC:,.0f}".replace(",","."),ha="right",fontsize=8,color=INK2)
ax2.axvline(CORTE,color="#d03b3b",lw=1.2)
ax2.text(CORTE-3,PV+180,f"PV {PV:,.0f}".replace(",","."),fontsize=8,color=INK,ha="right")
ax2.text(CORTE+3,AC+120,f"AC {AC:,.0f}".replace(",","."),fontsize=8,color=INK)
ax2.text(CORTE+3,EV-380,f"EV {EV:,.0f}".replace(",","."),fontsize=8,color=INK)
ax2.text(4,7300,f"SPI {EV/PV:.2f}   CPI {EV/AC:.2f}".replace(".",","),fontsize=10,fontweight="bold",color=INK,va="top")
ax2.set_xticks(months); ax2.set_xticklabels([MES[(START+timedelta(days=m)).month-1]+(START+timedelta(days=m)).strftime("-%y") for m in months],fontsize=8)
ax2.set_xlim(-5,330); ax2.set_ylim(0,8000); ax2.set_ylabel("MM$ acumulados")
ax2.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f"{v:,.0f}".replace(",",".")))
ax2.legend(loc="lower right",frameon=False,fontsize=8)
ax2.set_title("Curvas de valor ganado",loc="left",fontsize=12,fontweight="bold",color=INK,pad=10)
fig.savefig("vista_proyecto2.png",dpi=150,bbox_inches="tight",facecolor="white")
print("ok",FEND)
