# Diagram Meets Skill

Skill portable para convertir transcripciones de reuniones en diagramas de flujo
HTML/SVG, identificando procesos, decisiones, fuentes, transformaciones y
preguntas pendientes para el negocio.

## Contenido

- `transcript-to-flowchart/`: skill compatible con agentes que consumen
  instrucciones `SKILL.md`.
- `meet-example/`: ejemplo real anonimizado, con una vista general y otra de
  validaciones.
- `example-output/`: ejemplo básico del renderizador.

## Uso

1. Entregar al agente la transcripción completa en DOCX, TXT o Markdown.
2. Pedirle que use `transcript-to-flowchart/SKILL.md`.
3. El agente genera el modelo JSON siguiendo
   `references/diagram-schema.md`.
4. Renderizar el resultado:

   ```bash
   python transcript-to-flowchart/scripts/render_diagram.py proceso.json --output proceso.html
   ```

5. Abrir el HTML. Desde la barra superior se puede descargar SVG o imprimir y
   guardar como PDF.

Los orígenes, reglas, responsables o transformaciones que no estén claros se
representan mediante un nodo `?`, una conexión discontinua y una pregunta de
negocio al pie del diagrama.

## Ejemplo de prompt

> Usa la skill `transcript-to-flowchart` para analizar esta transcripción.
> Separa hechos de supuestos, marca con `?` toda información faltante y genera
> el JSON y el HTML final.

El renderizador utiliza únicamente la biblioteca estándar de Python y el HTML
resultante funciona sin conexión a internet.
