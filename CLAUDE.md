# Instrucciones para Claude: portafolio de Diego Ojeda

## Cómo trabajar
- Todo en **español** (textos del sitio, mensajes de commit y respuestas).
- **Preguntar antes de cada paso**: proponer el cambio y esperar aprobación antes de editar o publicar.
- No inventar datos personales, cargos ni logros: la fuente es `docs/CV_Diego_Ojeda.pdf` o lo que Diego indique.
- En los proyectos de ejemplo, dejar claro cuando los datos son referenciales.

## Publicación
- El sitio se publica con **GitHub Pages** desde la rama `main`, carpeta raíz: https://diegomagdiel.github.io/portafolio/
- Cada push a `main` actualiza el sitio en uno o dos minutos.
- `.nojekyll` evita que GitHub procese el sitio con Jekyll.

## Estructura del sitio (`index.html`)
Una sola página con HTML, CSS y JavaScript en el mismo archivo, sin herramientas de compilación.

- **Vistas por hash:** el inicio (`#inicio`, `#proyectos`, `#sobre-mi`, `#habilidades`, `#contacto`) y vistas que reemplazan el inicio:
  - Áreas (carpetas): `#planificacion`, `#datos`, `#apps`, `#diseno-3d`
  - Casos de estudio: `#parada`, `#correa`, `#al-articulo`
  - Para agregar una vista nueva: crear el `<section>`/`<article>` con `hidden` y sumarlo al objeto `cases` del script de rutas.
- **Carpetas por área** (`.folder` en `#proyectos`): cada una tiene clase de color (`plan`, `data`, `apps`, `cad`) y una ilustración SVG en línea que usa los tokens de color, así que cambia sola con la paleta.
- **Tarjetas de proyecto** (`.card`): categoría, estado (`.status.ok` terminado, `.status.wip` en desarrollo), herramientas y métricas.
- **Visor 3D** en `#diseno-3d`: three.js r128 desde cdnjs y OrbitControls desde jsDelivr. Hoy muestra un modelo de muestra; los modelos de SolidWorks se exportan como STL y se convierten para el visor.

## Diseño
- Estética moderna y oscura, temática tecnológica.
- Colores como tokens CSS en `:root`: `--copper` (planificación), `--steel` (datos), `--apps` (aplicaciones), `--cad` (diseño 3D), más `--bg`, `--surface`, `--line`, `--fg`, `--fg-2`, `--muted`.
- **Selector de paletas** (abajo a la derecha): Noche (por defecto), Circuito, Terminal, Plano técnico, Aurora y Topografía. Cada paleta es un bloque `:root[data-skin="..."]` que redefine los tokens, el fondo (`--page-img`) y la fuente de títulos (`--display`). La elección del visitante se guarda en `localStorage`.
- Tipografías de Google Fonts: Archivo, IBM Plex Sans, IBM Plex Mono, Space Grotesk, JetBrains Mono, Sora y Chakra Petch.
- El sitio debe verse bien en teléfono (sin desplazamiento horizontal) y respetar `prefers-reduced-motion`.

## Pendientes conocidos
- Carpeta de **Machine learning**: mantenimiento predictivo de culatas (deep learning) y diagnóstico de fallas en rodamientos (scikit-learn), cuando estén los archivos.
- **Diseño 3D**: reemplazar el modelo de muestra por modelos reales de SolidWorks.
- **Datos y Power BI**: primer dashboard publicado.
- **Riesgo con Monte Carlo** (proyecto 3 de planificación).
