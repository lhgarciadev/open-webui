# Presentations Gamma-Like Pipeline (Fase Base)

## Objetivo

Implementar un pipeline hibrido (narrativa + render) para producir presentaciones mas efectivas, con calidad visual y estructura tipo Gamma, manteniendo salida en PPTX.

## Alcance implementado en esta fase

- Entrada narrativa `story_spec` en `generate_presentation`.
- Conversor de `story_spec` a slides renderizables.
- Nueva tool `get_story_spec_template` para guiar al agente en la estructura narrativa.
- Compatibilidad con flujo anterior por `slides` directos.

## Arquitectura

1. Capa narrativa (Story Spec):

- Entrada: lista de bloques semanticos (`cover`, `insight`, `metrics`, `comparison`, `timeline`, `quote`, `cta`).
- Responsabilidad: definir mensaje por slide y secuencia argumental.

2. Capa de render:

- Convierte bloques a templates PPTX (`title`, `content`, `stats`, `two_column`, `section`, `quote`, `closing`).
- Aplica branding y estilos consistentes.

3. Capa de entrega:

- Guarda archivo en `DATA_DIR/presentations`.
- Expone descarga por `/api/v1/files/presentations/{filename}`.

## Contrato de bloques (Story Spec)

Tipos soportados:

- `cover`
- `section`
- `insight`
- `metrics`
- `comparison`
- `timeline`
- `quote`
- `cta`

Reglas:

- Si el primer bloque no es `cover`, se agrega portada automatica.
- Si la secuencia no termina en `cta/closing`, se agrega cierre automatizado.
- Limites de densidad: maximo 8 bullets por slide y hasta 4 metrics por slide de KPI.

## Valor esperado

- Menos slides "planas" y mas narrativa accionable.
- Mejor claridad ejecutiva (problema, evidencia, decision, siguiente paso).
- Menor friccion para crear decks efectivos desde prompts.

## Riesgos y mitigacion

- Riesgo: prompts pobres generan story specs debiles.
- Mitigacion: forzar uso de `get_story_spec_template` previo.

- Riesgo: modelos en `function_calling=default` no activan builtin tools.
- Mitigacion: establecer `DEFAULT_FUNCTION_CALLING_MODE=native` en entornos que usen presentaciones.

## Backlog Fase 2 (no implementado aun)

1. Motor de layout mas rico (grid dinamico, iconografia automatica, highlight cards).
2. Scoring de narrativa (completitud, claridad, accionabilidad) antes de render.
3. Export dual `pptx + pdf`.
4. Tema visual por audiencia (board, ventas, producto, inversionistas).
