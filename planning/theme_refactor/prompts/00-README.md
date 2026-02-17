# Prompts - Theme & Styling System Refactor v2.0

> **Estructura:** 5 etapas, 2 prompts por etapa (ejecutar/validar)
> **Objetivo:** Corregir problemas de fondos, colores hardcodeados, y responsiveness
> **Archivos afectados:** ~20 archivos

---

## Problemas a Resolver

1. **ChatBox ilegible en light mode** - Colores hardcodeados para dark mode
2. **Titulo invisible en light mode** - Gradiente con grises claros
3. **Sticky headers sin fondo** - Texto se superpone al hacer scroll
4. **Transparencias problematicas** - Bleed-through de texto
5. **Responsiveness inconsistente** - Anchos fijos sin breakpoints

---

## Flujo de Ejecucion

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW POR ETAPA                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│   │  Leer prompt │ -> │   Ejecutar   │ -> │   Validar    │      │
│   │  X.1-*.md    │    │   cambios    │    │  X.2-*.md    │      │
│   └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                  │               │
│                            ┌─────────────────────┴──────┐       │
│                            ▼                            ▼       │
│                     [PASS] -> Siguiente          [FAIL] ->      │
│                               etapa               Corregir      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Indice de Etapas

| #   | Descripcion                      | Ejecutar                                         | Validar                                         | Impacto |
| --- | -------------------------------- | ------------------------------------------------ | ----------------------------------------------- | ------- |
| 1   | Variables CSS (chatbox + titulo) | [1.1](./1.1-css-variables-ejecutar.md)           | [1.2](./1.2-css-variables-validar.md)           | Alto    |
| 2   | ChatBox theme-aware              | [2.1](./2.1-chatbox-theme-ejecutar.md)           | [2.2](./2.2-chatbox-theme-validar.md)           | Alto    |
| 3   | Titulo gradient theme-aware      | [3.1](./3.1-title-gradient-ejecutar.md)          | [3.2](./3.2-title-gradient-validar.md)          | Alto    |
| 4   | Sticky headers con fondos        | [4.1](./4.1-sticky-headers-ejecutar.md)          | [4.2](./4.2-sticky-headers-validar.md)          | Medio   |
| 5   | Transparencias & responsiveness  | [5.1](./5.1-transparency-responsive-ejecutar.md) | [5.2](./5.2-transparency-responsive-validar.md) | Medio   |

---

## Orden de Ejecucion (OBLIGATORIO)

```
1. [  ] 1.1 - Agregar variables CSS a tailwind.css
2. [  ] 1.2 - Validar compilacion de variables
3. [  ] 2.1 - Actualizar chatbox en MessageInput.svelte
4. [  ] 2.2 - Validar chatbox en todos los temas
5. [  ] 3.1 - Actualizar gradiente de titulo
6. [  ] 3.2 - Validar visibilidad del titulo
7. [  ] 4.1 - Agregar fondos a sticky headers
8. [  ] 4.2 - Validar sin superposicion de texto
9. [  ] 5.1 - Eliminar transparencias y agregar breakpoints
10.[  ] 5.2 - Validacion final en todos los temas y viewports
```

**IMPORTANTE:** Las etapas son secuenciales. No saltar pasos.

---

## Archivos Involucrados (Resumen)

| Etapa | Archivos                                       | Accion             |
| ----- | ---------------------------------------------- | ------------------ |
| 1     | `src/tailwind.css`                             | AGREGAR ~50 lineas |
| 2     | `src/lib/components/chat/MessageInput.svelte`  | MODIFICAR          |
| 3     | `Placeholder.svelte`, `ChatPlaceholder.svelte` | MODIFICAR          |
| 4     | `Sidebar.svelte`, 5 admin components           | MODIFICAR          |
| 5     | 6 components con transparencias                | MODIFICAR          |

---

## Criterios de Exito Final

### Visual

| Tema  | Chatbox        | Titulo      | Sidebar     | Admin       |
| ----- | -------------- | ----------- | ----------- | ----------- |
| Light | Blanco legible | Gris oscuro | Sin overlap | Consistente |
| Dark  | Oscuro legible | Gris claro  | Sin overlap | Consistente |
| OLED  | Negro puro     | Gris claro  | Sin overlap | Consistente |
| Her   | Rose tint      | Rose        | Sin overlap | Consistente |

### Responsiveness

| Viewport | Expectativa           |
| -------- | --------------------- |
| 320px    | Chat y menus legibles |
| 768px    | Sidebar funcional     |
| 1024px+  | Layout completo       |

---

## Rollback

```bash
# Revertir todos los cambios
git checkout HEAD -- src/

# O archivo especifico
git checkout HEAD -- src/tailwind.css
```

---

## Caracteristicas de los Prompts

Cada prompt esta disenado para:

1. **Autocontenido** - Incluye todo el contexto necesario
2. **One-shot** - Ejecutable en una sola interaccion
3. **Verificable** - Criterios claros de exito/fallo
4. **Reversible** - Instrucciones de rollback incluidas

---

## Referencias

- [ASIS_TOBE_ANALYSIS.md](../ASIS_TOBE_ANALYSIS.md) - Analisis detallado de problemas
- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) - Plan tecnico completo
