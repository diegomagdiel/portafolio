# Instrucciones para Claude: portafolio de Diego Ojeda

## Cómo trabajar
- Todo en **español** (textos del sitio, mensajes de commit y respuestas).
- **Preguntar antes de cada paso**: proponer el cambio y esperar aprobación antes de editar o publicar.
- **Tesis y trabajos con empresas:** no publicar el nombre de la empresa, la localidad de la planta ni el nombre comercial de los equipos. Revisar también nombres de archivo y metadatos.
- No inventar datos personales, cargos ni logros: la fuente es `docs/CV_Diego_Ojeda.pdf` o lo que Diego indique.
- En los proyectos de ejemplo, dejar claro cuando los datos son referenciales.

## Publicación
- El sitio se publica con **GitHub Pages** desde la rama `main`, carpeta raíz: https://diegomagdiel.github.io/portafolio/
- Cada push a `main` actualiza el sitio en uno o dos minutos.
- `.nojekyll` evita que GitHub procese el sitio con Jekyll.

## Estructura del sitio (`index.html`)
Una sola página con HTML, CSS y JavaScript en el mismo archivo, sin herramientas de compilación.

- **Vistas por hash:** el inicio (`#inicio`, `#proyectos`, `#sobre-mi`, `#habilidades`, `#contacto`) y vistas que reemplazan el inicio:
  - Áreas (carpetas): `#planificacion`, `#datos`, `#apps`, `#diseno-3d`, `#machine-learning`
  - Casos de estudio: `#parada`, `#correa`, `#al-articulo`, `#rodamientos`, `#grietas-rotor`, `#escenario` (escenario móvil, informe para un cliente en 2019; cliente anónimo, imagen en `img/escenario/`)
  - Proyecto de título: carpeta propia en el inicio que abre directo el caso `#tesis` (túnel de congelación). Imágenes en `img/tesis/`.
  - Para agregar una vista nueva: crear el `<section>`/`<article>` con `hidden` y sumarlo al objeto `cases` del script de rutas.
- **Carpetas por área** (`.folder` en `#proyectos`): cada una tiene clase de color (`plan`, `data`, `apps`, `cad`, `ml`, `tes`) y una ilustración SVG en línea que usa los tokens de color, así que cambia sola con la paleta.
- **Tarjetas de proyecto** (`.card`): categoría, estado (`.status.ok` terminado, `.status.wip` en desarrollo), herramientas y métricas.
- **Visor 3D reutilizable**: three.js r128 desde cdnjs, OrbitControls y GLTFLoader desde jsDelivr. Cada `<div class="viewer" data-visor data-modelos="propuesta,actual" data-modo="botones|siguiente">` crea su propio visor y arranca solo cuando su sección se ve; los modelos se registran en el objeto `MODELOS` del script (archivo, etiqueta, nombre del botón de capa). Cada caso lleva su visor (`#tesis`: Actual/Propuesta; `#escenario`: escenario móvil) y `#diseno-3d` tiene una galería con "Siguiente modelo →" que recorre todos. La cámara se encuadra sola según el tamaño del modelo y el botón de capa (Carcasa/Puerta) se oculta si el modelo no tiene malla `carcasa`. `modelos/escenario-movil.glb` se armó igual que la propuesta de la tesis, desde `Base completa.SLDASM` (grupos: techo = `ventiladores`, bases = `cinta`, puerta = `carcasa`). Modelos de la tesis: `modelos/tunel-congelacion-actual.glb?v=3` (situación actual con carcasa, armado desde `Hardeneractualconcinta.SLDASM` con el mismo método; la cinta interior es la pieza oculta `cintafake`, que se fuerza visible con la lista `mostrar` de grupos.json; la cinta se simplificó a 25 000 triángulos) y `modelos/tunel-congelacion-propuesta.glb` (propuesta, reconstruida desde `PropuestaV1.SLDASM` sin las cuatro cintas de alimentación que van antes del túnel sin tener SolidWorks; reemplazó a `PropuestaV2`, que fue una variante descartada que no calza con las fotos del informe. La ruta lleva `?v=3` para saltar la caché del navegador: los bloques internos van comprimidos con deflate crudo; `Contents/DisplayLists` trae la malla por pieza en coordenadas locales como tiras de triángulos, y el XML `swXmlContents` trae el árbol con `swTransform` para colocar cada instancia; se respetan los componentes ocultos salvo las paredes, que van como carcasa). Las mallas se llaman `carcasa`, `cinta`, `ventiladores` y `estructura`; el visor les asigna material por nombre y el botón "Carcasa" oculta la carcasa. Los archivos fuente de la tesis están en un repositorio privado.

## Diseño
- Estética moderna y oscura, temática tecnológica.
- Colores como tokens CSS en `:root`: `--copper` (planificación), `--steel` (datos), `--apps` (aplicaciones), `--cad` (diseño 3D), `--ml` (machine learning) y `--tes` (proyecto de título), definidos por paleta en su propio bloque, más `--bg`, `--surface`, `--line`, `--fg`, `--fg-2`, `--muted`.
- **Selector de paletas** (abajo a la derecha): Noche (por defecto), Circuito, Terminal, Plano técnico, Aurora y Topografía. Cada paleta es un bloque `:root[data-skin="..."]` que redefine los tokens, el fondo (`--page-img`) y la fuente de títulos (`--display`). La elección del visitante se guarda en `localStorage`.
- Tipografías de Google Fonts: Archivo, IBM Plex Sans, IBM Plex Mono, Space Grotesk, JetBrains Mono, Sora y Chakra Petch.
- El sitio debe verse bien en teléfono (sin desplazamiento horizontal) y respetar `prefers-reduced-motion`.

## Pendientes conocidos
- Carpeta de **Machine learning** (`#machine-learning`): publicados ① rodamientos y ② grietas en rotor, con gráficos en `img/ml/` y textos tomados de los README de cada repo (`DIEGO\extraccion-features-rodamientos`, `DIEGO\clasificacion-grietas-rotor`). Los repos del diplomado son privados, así que el sitio no los enlaza. Faltan ③–⑧, con el proyecto final de culatas como estrella; ver `DIEGO\diplomado-bigdata-confiabilidad\README.md`.
- **Diseño 3D**: publicados el túnel de la tesis (actual y propuesta) y el escenario móvil. Planificado: polín de carga de la correa CV-05.
- **Datos y Power BI**: primer dashboard publicado.
- **Riesgo con Monte Carlo** (proyecto 3 de planificación).
