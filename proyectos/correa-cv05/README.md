# Control con valor ganado: correa transportadora CV-05

Montaje de una correa transportadora de 1,2 km, con 284 días de plazo y un presupuesto de 7.080 MM$, controlado al cierre de la semana 20.

| Indicador | Resultado al corte |
| --- | --- |
| SPI | 0,89 |
| CPI | 0,94 |
| EAC (BAC ÷ CPI) | 7.510 MM$ |
| Término pronosticado | 02-11-2027 (+19 días) |

El atraso lo define el despacho del motor, reductor y sala eléctrica, que está en ruta crítica. La fabricación de estructuras tiene la peor variación de programa, pero tiene holgura y no mueve el término.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `datos.py` | Datos del proyecto: EDT, duraciones, presupuesto, avance real al corte, cálculo de ruta crítica y valor ganado |
| `correa_CV05_linea_base.xml` | Línea base en formato XML de MS Project, sin avance, para practicar la carga de avance |
| `gen_xml2.py` | Genera el XML de línea base |
| `vista.py` | Genera la imagen de seguimiento y curvas de valor ganado |
| `reporte2.py` | Genera el informe PDF de 4 páginas |

El informe está en [`informes/Informe_Valor_Ganado_Correa_CV05.pdf`](../../informes/Informe_Valor_Ganado_Correa_CV05.pdf).

Los plazos se calibraron con proyectos publicados: Lumwana (Zambia), CV006 de Fortescue (Australia) y la licitación de ENAMI para una correa en Planta Matta (Copiapó). Datos referenciales para fines de portafolio.
