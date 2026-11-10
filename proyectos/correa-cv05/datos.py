from datetime import date, timedelta
START = date(2027, 1, 4)  # lunes
# (fila, nivel, edt, nombre, dur_dias, preds, presupuesto MM$, tipo) S=resumen M=hito T=tarea
rows = [
 (1,1,"0","MONTAJE CORREA TRANSPORTADORA CV-05",None,[],0,"S"),
 (2,2,"1","Gestión e ingeniería",None,[],0,"S"),
 (3,3,"1.1","Inicio del proyecto",0,[],0,"M"),
 (4,3,"1.2","Ingeniería de detalle y planos aprobados",40,[3],180,"T"),
 (5,3,"1.3","Permisos y plan de seguridad aprobados",30,[3],40,"T"),
 (6,2,"2","Adquisiciones",None,[],0,"S"),
 (7,3,"2.1","Fabricación de estructuras metálicas",100,[4],1200,"T"),
 (8,3,"2.2","Fabricación y despacho de polines y poleas",110,[4],650,"T"),
 (9,3,"2.3","Compra y despacho de banda",120,[4],900,"T"),
 (10,3,"2.4","Despacho de motor, reductor y sala eléctrica",180,[4],1100,"T"),
 (11,2,"3","Obras civiles",None,[],0,"S"),
 (12,3,"3.1","Instalación de faena",15,[5],120,"T"),
 (13,3,"3.2","Movimiento de tierras y plataforma",30,[12],380,"T"),
 (14,3,"3.3","Fundaciones estación motriz y retorno",30,[13],260,"T"),
 (15,3,"3.4","Fundaciones de soportes del trazado",35,[13],420,"T"),
 (16,2,"4","Montaje mecánico",None,[],0,"S"),
 (17,3,"4.1","Montaje de estructuras del trazado",40,[15,7],520,"T"),
 (18,3,"4.2","Montaje estación motriz (poleas, motor, reductor)",25,[14,10,8],240,"T"),
 (19,3,"4.3","Montaje de polines",20,[17,8],180,"T"),
 (20,3,"4.4","Tendido y vulcanizado de banda",15,[19,9,18],210,"T"),
 (21,2,"5","Montaje eléctrico e instrumentación",None,[],0,"S"),
 (22,3,"5.1","Montaje de sala eléctrica",15,[14,10],90,"T"),
 (23,3,"5.2","Tendido de cables y canalizaciones",30,[17],260,"T"),
 (24,3,"5.3","Instrumentación y seguridades (pull cord, desalineamiento)",15,[23,19],110,"T"),
 (25,3,"5.4","Conexionado y pruebas eléctricas",12,[22,24],70,"T"),
 (26,2,"6","Puesta en marcha y cierre",None,[],0,"S"),
 (27,3,"6.1","Pruebas en vacío",7,[20,25],40,"T"),
 (28,3,"6.2","Pruebas con carga",7,[27],50,"T"),
 (29,3,"6.3","Entrega a operaciones",0,[28],0,"M"),
 (30,3,"6.4","Desmovilización y dossier de calidad",10,[29],60,"T"),
 (31,3,"6.5","Fin del proyecto",0,[30],0,"M"),
]
es, ef = {}, {}
for f,l,e,n,d,p,b,t in rows:
    if t=="S": continue
    s = max([ef[x] for x in p], default=0); es[f]=s; ef[f]=s+d
for i,(f,l,e,n,d,p,b,t) in enumerate(rows):
    if t!="S": continue
    kids=[]
    for g,l2,*_ in rows[i+1:]:
        if l2<=l: break
        if g in es: kids.append(g)
    es[f]=min(es[k] for k in kids); ef[f]=max(ef[k] for k in kids)
END = max(ef.values())
succ={f:[] for f in es}
for f,l,e,n,d,p,b,t in rows:
    for x in p: succ[x].append(f)
lf={}
for f,l,e,n,d,p,b,t in reversed(rows):
    if t=="S": continue
    lf[f]=min([lf[s]-(ef[s]-es[s]) for s in succ[f]], default=END)
crit={f for f in lf if lf[f]==ef[f]}
def fecha(d): return START+timedelta(days=d)

CORTE = 140  # fin de la semana 20
# avance real al corte: fila -> (comienzo real, fin real o None, % completado, costo real MM$)
real = {
 4:(0,45,100,198), 5:(0,30,100,41), 12:(30,45,100,128), 13:(45,83,100,456),
 14:(83,115,100,275), 15:(83,123,100,455),
 7:(45,None,80,1010), 8:(45,None,85,560), 9:(45,None,70,640), 10:(45,None,45,520),
}
def plan_pct(f, t=CORTE):
    d = ef[f]-es[f]
    if d == 0: return 100.0 if t >= es[f] else 0.0
    return max(0, min(1, (t-es[f])/d))*100
tareas = [r for r in rows if r[7]=="T"]
BAC = sum(r[6] for r in tareas)
PV = sum(r[6]*plan_pct(r[0])/100 for r in tareas)
EV = sum(r[6]*real[r[0]][2]/100 for r in tareas if r[0] in real)
AC = sum(real[r[0]][3] for r in tareas if r[0] in real)

# pronóstico de término: reprograma lo pendiente desde el corte
def pronostico():
    fs, ff = {}, {}
    for f,l,e,n,d,p,b,t in rows:
        if t=="S": continue
        if f in real:
            s0,f0,pc,_ = real[f]
            fs[f]=s0; ff[f]= f0 if f0 is not None else CORTE + round(d*(100-pc)/100)
        else:
            s = max([ff[x] for x in p], default=0); s=max(s, CORTE) if d else s
            fs[f]=s; ff[f]=s+d
    return fs, ff
