# Diagram Meets Skill

Skill portable para convertir transcripciones de reuniones en diagramas de
flujo HTML/SVG, detectar información incompleta y refinar el proceso mediante
preguntas y respuestas de negocio.

Funciona con Claude Code, Codex y otras herramientas compatibles con el
estándar `SKILL.md`. El repositorio puede alojarse tanto en GitHub como en
GitLab.

## Características

- Analiza transcripciones en DOCX, TXT o Markdown.
- Identifica actores, sistemas, archivos, bases de datos, decisiones,
  transformaciones, rutas paralelas y excepciones.
- Genera un modelo JSON auditable y un HTML autocontenido.
- Incluye iconos para bases de datos, Excel, APIs, archivos, personas,
  transformaciones y reportes.
- Marca información desconocida con nodos `?` y conexiones discontinuas.
- Exporta preguntas de negocio a un TXT editable.
- Procesa las respuestas y regenera el diagrama de forma iterativa.
- Permite descargar SVG o imprimir en PDF horizontal.
- Incluye versionado semántico y comprobación de actualizaciones.

## Requisitos

- Python 3.9 o posterior.
- Node.js y `npx` para la instalación automatizada.
- Claude Code, Codex u otro agente compatible con Agent Skills.

El renderizador usa únicamente la biblioteca estándar de Python. El HTML
generado no requiere conexión a internet.

## Instalación en Claude Code

### Instalación global

Disponible para todos los proyectos del usuario:

```bash
npx skills@latest add jreyes-antonio/diagram-meets-skill \
  --skill transcript-to-flowchart \
  --agent claude-code \
  --global \
  --yes
```

En PowerShell se puede ejecutar en una sola línea:

```powershell
npx skills@latest add jreyes-antonio/diagram-meets-skill --skill transcript-to-flowchart --agent claude-code --global --yes
```

La ruta esperada es:

```text
~/.claude/skills/transcript-to-flowchart/
```

### Instalación sólo para un proyecto

Ejecutar desde la raíz del proyecto y omitir `--global`:

```bash
npx skills@latest add jreyes-antonio/diagram-meets-skill \
  --skill transcript-to-flowchart \
  --agent claude-code \
  --yes
```

La skill quedará en:

```text
<proyecto>/.claude/skills/transcript-to-flowchart/
```

### Instalación desde GitLab

El instalador acepta URLs completas de GitLab. Para un mirror o fork:

```bash
npx skills@latest add https://gitlab.com/<grupo>/diagram-meets-skill \
  --skill transcript-to-flowchart \
  --agent claude-code \
  --global \
  --yes
```

### Comprobar la instalación

```bash
npx skills@latest list --global --agent claude-code
```

Si Claude Code estaba abierto antes de crear por primera vez el directorio de
skills, reiniciarlo.

## Versión y actualizaciones

La versión instalada se encuentra en:

```text
transcript-to-flowchart/VERSION
```

Consultar sólo la versión local:

```bash
python ~/.claude/skills/transcript-to-flowchart/scripts/version_info.py
```

Compararla con la versión publicada:

```bash
python ~/.claude/skills/transcript-to-flowchart/scripts/version_info.py --check
```

En Windows PowerShell:

```powershell
python "$HOME\.claude\skills\transcript-to-flowchart\scripts\version_info.py" --check
```

También se le puede preguntar directamente a Claude:

> Usa `transcript-to-flowchart` y dime qué versión está instalada. Comprueba si
> está actualizada.

Actualizar únicamente esta skill:

```bash
npx skills@latest update transcript-to-flowchart --global --yes
```

Si el gestor no conserva el origen de instalación, reinstalar:

```bash
npx skills@latest add jreyes-antonio/diagram-meets-skill \
  --skill transcript-to-flowchart \
  --agent claude-code \
  --global \
  --yes
```

El proyecto usa versionado semántico:

- `PATCH`: correcciones sin cambiar el contrato.
- `MINOR`: nuevas funciones compatibles.
- `MAJOR`: cambios incompatibles en el JSON, scripts o flujo de uso.

Cada versión publicada debe actualizar `VERSION` y crear un tag Git
`vX.Y.Z`.

## Uso básico

Ejemplo de solicitud:

> Usa la skill `transcript-to-flowchart` para analizar esta transcripción.
> Separa hechos de supuestos, marca con `?` toda información faltante y genera
> el JSON, el HTML y el archivo de preguntas.

El agente debe entregar:

```text
proceso.json
proceso.html
proceso-preguntas.txt
```

El HTML incluye desplazamiento horizontal para diagramas grandes, descarga SVG
y salida PDF A4 horizontal.

## Renderizar un JSON manualmente

```bash
python transcript-to-flowchart/scripts/render_diagram.py \
  proceso.json \
  --output proceso.html
```

## Ciclo de preguntas de negocio

### 1. Exportar las preguntas

```bash
python transcript-to-flowchart/scripts/question_cycle.py export \
  proceso.json \
  --output proceso-preguntas.txt
```

### 2. Completar el TXT

Escribir debajo de cada marcador `RESPUESTA:` sin modificar los identificadores:

```text
[[Q001]]
PREGUNTA: ¿Qué sistema publica el rol?
RESPUESTA:
El rol se publica en Operaciones y se descarga como XLSX.
[[/Q001]]
```

### 3. Procesar las respuestas

Entregar al agente el JSON original y el TXT respondido. Opcionalmente,
estructurar primero las respuestas:

```bash
python transcript-to-flowchart/scripts/question_cycle.py parse \
  proceso.json \
  proceso-preguntas.txt \
  --output proceso-respuestas.json
```

La skill debe:

1. Vincular cada respuesta con sus nodos.
2. Actualizar nodos, conexiones, reglas y supuestos.
3. Conservar respuestas aplicadas en `resolved_questions`.
4. Eliminar un nodo `?` sólo cuando la incertidumbre esté resuelta.
5. Crear repreguntas como `Q003-F1` si la respuesta sigue siendo ambigua.
6. Regenerar el JSON, el HTML y un TXT con las preguntas pendientes.

## Instalación manual

Clonar el repositorio y copiar la carpeta completa:

```bash
git clone https://github.com/jreyes-antonio/diagram-meets-skill.git
mkdir -p ~/.claude/skills
cp -R diagram-meets-skill/transcript-to-flowchart ~/.claude/skills/
```

Para un repositorio GitLab, sustituir la URL del `git clone`.

## Estructura

```text
transcript-to-flowchart/
├── SKILL.md
├── VERSION
├── agents/
├── assets/
├── references/
└── scripts/
    ├── question_cycle.py
    ├── render_diagram.py
    └── version_info.py
```

Los diagramas reales anonimizados están en `meet-example/`.

## Solución de problemas

### `No skills found`

Usar el nombre exacto:

```text
transcript-to-flowchart
```

Y comprobar que `SKILL.md` se encuentre dentro de la carpeta instalada.

### Claude no activa la skill

Invocarla explícitamente:

```text
/transcript-to-flowchart
```

O mencionarla por nombre en la solicitud.

### `python` no está disponible

Instalar Python 3 o usar el nombre disponible en el sistema, por ejemplo
`python3`.

### No se puede comprobar la versión remota

La versión local seguirá disponible. La comparación remota requiere acceso a:

```text
raw.githubusercontent.com
```

## Privacidad

No publicar transcripciones originales ni nombres personales sin autorización.
Los ejemplos del repositorio deben permanecer anonimizados.
