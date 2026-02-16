# Prompts - Theme System Refactor (Fix Tailwind v4)

> Estructura: 3 etapas, 2 prompts por etapa (ejecutar/validar)
> Objetivo: Corregir sistema de temas que no funciona debido a compilacion de Tailwind v4
> Tiempo estimado: 1-2 horas total

## Problema Raiz

Las reglas CSS `[data-theme='*']` en `app.css` **NO son compiladas** por Tailwind CSS v4.
Resultado: El fondo y colores no cambian al seleccionar un tema diferente.

## Flujo de Ejecucion

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Ejecutar   │ ──► │  Revisar    │ ──► │  Validar    │
│  X.1-*.md   │     │  cambios    │     │  X.2-*.md   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                          ┌───────────────────┴───────────────────┐
                          ▼                                       ▼
                    [PASS] ──► Siguiente etapa            [FAIL] ──► Corregir y repetir
```

## Indice de Etapas

| Etapa | Descripcion | Ejecutar | Validar | Tiempo |
|-------|-------------|----------|---------|--------|
| 1 | Mover variables CSS a tailwind.css @layer base | [1.1](./1.1-tailwind-vars-ejecutar.md) | [1.2](./1.2-tailwind-vars-validar.md) | 30 min |
| 2 | Limpiar app.css (remover duplicados y hardcodes) | [2.1](./2.1-app-css-cleanup-ejecutar.md) | [2.2](./2.2-app-css-cleanup-validar.md) | 20 min |
| 3 | Actualizar splash screen en app.html | [3.1](./3.1-app-html-splash-ejecutar.md) | [3.2](./3.2-app-html-splash-validar.md) | 10 min |

## Orden de Ejecucion (OBLIGATORIO)

```
1. [  ] 1.1 - Agregar variables a tailwind.css
2. [  ] 1.2 - Validar variables en navegador
3. [  ] 2.1 - Limpiar app.css
4. [  ] 2.2 - Validar que body responde a tema
5. [  ] 3.1 - Actualizar splash screen
6. [  ] 3.2 - Validar visualmente todos los temas
```

**IMPORTANTE:** Las etapas son secuenciales. No saltar pasos.

## Archivos Involucrados

| Archivo | Accion | Lineas Aprox |
|---------|--------|--------------|
| `src/tailwind.css` | AGREGAR | +100 lineas (variables de tema) |
| `src/app.css` | MODIFICAR | -170 lineas (remover duplicados) |
| `src/app.html` | MODIFICAR | ~5 lineas (splash background) |

## Evidencia del Problema

```javascript
// Ejecutado en navegador con tema "dark":
{
  theme: "dark",           // localStorage ✓
  dataTheme: null,         // data-theme NO se aplica
  surfaceBase: "15 23 42"  // Siempre igual (deberia ser "23 23 23")
}

// dataThemeRulesCount: 8 (todos de Sonner/Tippy, ninguno de app.css)
```

## Criterios de Exito Final

| Tema | Background Esperado | Test |
|------|---------------------|------|
| Light | `rgb(249, 250, 251)` #f9fafb | [ ] |
| Dark | `rgb(23, 23, 23)` #171717 | [ ] |
| OLED Dark | `rgb(0, 0, 0)` #000000 | [ ] |
| Her | `rgb(255, 250, 250)` #fffafa | [ ] |

## Validacion Final (DevTools Console)

```javascript
// Despues de implementar, este test debe pasar:
['light', 'dark', 'oled-dark', 'her'].forEach(theme => {
  document.documentElement.setAttribute('data-theme', theme);
  document.documentElement.classList.toggle('dark', theme === 'dark' || theme === 'oled-dark');
  const bg = getComputedStyle(document.body).backgroundColor;
  console.log(`${theme}: ${bg}`);
});

// Salida esperada:
// light: rgb(249, 250, 251)
// dark: rgb(23, 23, 23)
// oled-dark: rgb(0, 0, 0)
// her: rgb(255, 250, 250)
```

## Rollback

Si algo falla:
```bash
git checkout HEAD -- src/tailwind.css src/app.css src/app.html
```

## Referencias

- [ASIS_TOBE_ANALYSIS.md](../ASIS_TOBE_ANALYSIS.md) - Analisis detallado
- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) - Plan tecnico completo
- [architecture.md](../architecture.md) - Arquitectura del sistema de temas
