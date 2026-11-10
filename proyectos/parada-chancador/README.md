# Parada de planta: chancador primario

Cronograma de una parada programada de 72 horas para cambiar el manto y las cóncavas inferiores de un chancador giratorio primario.

- **Duración programada:** 61 h, con 11 h de margen sobre la ventana de 72 h.
- **Calendario:** continuo 24/7, turnos de 12 h.
- **Ruta crítica:** pasa por el cambio de cóncavas, no por el cambio de manto.
- **Costo de mano de obra y grúa:** $10.135.000 CLP (tasas referenciales).

## Archivos

| Archivo | Qué es |
| --- | --- |
| `parada_chancador_primario.xml` | Cronograma en formato XML de MS Project; se abre en MS Project o ProjectLibre |
| `gen_xml.py` | Genera el XML: actividades, duraciones, predecesoras, recursos y tasas |
| `reporte.py` | Genera el informe PDF (Gantt, curvas S, histograma de dotación y costos) |

El informe está en [`informes/Reporte_Parada_Chancador_Primario.pdf`](../../informes/Reporte_Parada_Chancador_Primario.pdf).

```bash
python gen_xml.py      # crea el XML
python reporte.py      # crea el informe PDF (requiere matplotlib y reportlab)
```

Datos referenciales para fines de portafolio; no corresponden a una faena específica.
