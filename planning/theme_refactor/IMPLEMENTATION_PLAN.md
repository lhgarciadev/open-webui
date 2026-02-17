# Theme & Styling System Implementation Plan

**Date:** 2026-02-17
**Version:** 2.0
**Total Stages:** 5
**Files to Modify:** ~20 files

---

## Overview

Este plan implementa las correcciones identificadas en `ASIS_TOBE_ANALYSIS.md` en 5 etapas secuenciales. Cada etapa tiene un prompt de ejecucion y uno de validacion.

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE IMPLEMENTACION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ETAPA 1: Variables CSS Chatbox & Titulo                        │
│     ├── Agregar variables chatbox a tailwind.css                │
│     ├── Agregar variables gradient titulo                       │
│     └── Validar compilacion                                     │
│                                                                 │
│  ETAPA 2: ChatBox Theme-Aware                                   │
│     ├── Actualizar MessageInput.svelte                          │
│     └── Validar en 4 temas                                      │
│                                                                 │
│  ETAPA 3: Titulo Gradient Theme-Aware                           │
│     ├── Actualizar Placeholder.svelte                           │
│     ├── Actualizar ChatPlaceholder.svelte                       │
│     └── Validar visibilidad                                     │
│                                                                 │
│  ETAPA 4: Sticky Headers & Fondos Solidos                       │
│     ├── Sidebar.svelte header/footer                            │
│     ├── Admin headers (5 archivos)                              │
│     └── Eliminar gradient workaround                            │
│                                                                 │
│  ETAPA 5: Transparencias & Responsiveness                       │
│     ├── Eliminar opacidades problematicas                       │
│     ├── Agregar breakpoints responsivos                         │
│     └── Validacion final                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Etapa 1: Variables CSS (Chatbox & Titulo)

### Objetivo
Agregar variables CSS para chatbox y gradiente de titulo en `tailwind.css`.

### Archivos a Modificar
| Archivo | Accion | Lineas |
|---------|--------|--------|
| `src/tailwind.css` | AGREGAR | +50 lineas |

### Cambios Especificos

**Agregar DESPUES del bloque existente de variables de tema (aproximadamente linea 193):**

```css
/* ============================================
   CHATBOX COLORS - Theme-aware input styling
   ============================================ */

/* Light Theme */
:root,
[data-theme="light"] {
  --color-chatbox-bg: 255 255 255;
  --color-chatbox-text: 23 23 23;
  --color-chatbox-border: 229 231 235;
  --color-chatbox-ring: 59 130 246 / 0.2;
  --color-chatbox-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.1);

  /* Title Gradient */
  --color-title-gradient-start: 55 65 81;
  --color-title-gradient-end: 107 114 128;
}

/* Dark Theme */
.dark,
[data-theme="dark"] {
  --color-chatbox-bg: 10 10 10 / 0.8;
  --color-chatbox-text: 243 244 246;
  --color-chatbox-border: 255 255 255 / 0.05;
  --color-chatbox-ring: 255 255 255 / 0.1;
  --color-chatbox-shadow: 0 10px 40px -5px rgba(0, 0, 0, 0.5);

  /* Title Gradient */
  --color-title-gradient-start: 236 236 236;
  --color-title-gradient-end: 155 155 155;
}

/* OLED Dark Theme */
[data-theme="oled-dark"] {
  --color-chatbox-bg: 0 0 0 / 0.9;
  --color-chatbox-text: 248 250 252;
  --color-chatbox-border: 255 255 255 / 0.05;
  --color-chatbox-ring: 255 255 255 / 0.1;
  --color-chatbox-shadow: 0 10px 40px -5px rgba(0, 0, 0, 0.8);

  /* Title Gradient - same as dark */
  --color-title-gradient-start: 236 236 236;
  --color-title-gradient-end: 155 155 155;
}

/* Her Theme */
[data-theme="her"] {
  --color-chatbox-bg: 255 250 250;
  --color-chatbox-text: 23 23 23;
  --color-chatbox-border: 254 205 211;
  --color-chatbox-ring: 244 63 94 / 0.2;
  --color-chatbox-shadow: 0 4px 20px -2px rgba(244, 63, 94, 0.1);

  /* Title Gradient */
  --color-title-gradient-start: 136 19 55;
  --color-title-gradient-end: 190 18 60;
}
```

### Criterios de Validacion
- [ ] No errores de compilacion CSS
- [ ] Variables accesibles via DevTools
- [ ] Hot reload funciona correctamente

### Prompts
- Ejecutar: `prompts/1.1-css-variables-ejecutar.md`
- Validar: `prompts/1.2-css-variables-validar.md`

---

## Etapa 2: ChatBox Theme-Aware

### Objetivo
Actualizar MessageInput.svelte para usar variables CSS en lugar de colores hardcodeados.

### Archivos a Modificar
| Archivo | Accion | Lineas |
|---------|--------|--------|
| `src/lib/components/chat/MessageInput.svelte` | MODIFICAR | ~10 lineas |

### Cambios Especificos

**Buscar (linea ~1167):**
```svelte
<div id="message-input-container"
  class="flex-1 flex flex-col relative w-full rounded-[2.5rem] border transition px-2 py-1 text-gray-100 backdrop-blur-3xl bg-[#0a0a0a]/80 shadow-[0_10px_40px_-5px_rgba(0,0,0,0.5)] ring-1 ring-white/10 {$temporaryChatEnabled
    ? 'border-dashed border-gray-500/30 hover:border-gray-400/50 focus-within:border-blue-500/50'
    : 'border-white/5 hover:border-white/10 focus-within:border-blue-500/40 focus-within:shadow-[0_0_30px_rgba(59,130,246,0.3)]'}"
```

**Reemplazar con:**
```svelte
<div id="message-input-container"
  class="flex-1 flex flex-col relative w-full rounded-[2.5rem] border transition px-2 py-1 backdrop-blur-3xl
         text-gray-900 dark:text-gray-100
         bg-white/95 dark:bg-[rgb(var(--color-chatbox-bg))]
         shadow-lg dark:shadow-[var(--color-chatbox-shadow)]
         ring-1 ring-gray-200/50 dark:ring-[rgb(var(--color-chatbox-ring))]
         {$temporaryChatEnabled
           ? 'border-dashed border-gray-300 dark:border-gray-500/30 hover:border-gray-400 dark:hover:border-gray-400/50 focus-within:border-blue-500/50'
           : 'border-gray-200 dark:border-white/5 hover:border-gray-300 dark:hover:border-white/10 focus-within:border-blue-500/40 focus-within:shadow-[0_0_30px_rgba(59,130,246,0.2)]'}"
```

### Criterios de Validacion
- [ ] Light theme: Chatbox blanco con texto oscuro
- [ ] Dark theme: Chatbox oscuro con texto claro
- [ ] OLED theme: Chatbox negro puro
- [ ] Her theme: Chatbox con tinte rose
- [ ] Input funcional en todos los temas

### Prompts
- Ejecutar: `prompts/2.1-chatbox-theme-ejecutar.md`
- Validar: `prompts/2.2-chatbox-theme-validar.md`

---

## Etapa 3: Titulo Gradient Theme-Aware

### Objetivo
Actualizar el gradiente del titulo para ser visible en todos los temas.

### Archivos a Modificar
| Archivo | Accion | Lineas |
|---------|--------|--------|
| `src/lib/components/chat/Placeholder.svelte` | MODIFICAR | ~5 lineas |
| `src/lib/components/chat/ChatPlaceholder.svelte` | MODIFICAR | ~5 lineas |

### Cambios Especificos

**En ambos archivos, buscar:**
```svelte
<h1 class="text-6xl md:text-7xl font-secondary font-light tracking-tight pb-2"
    style="background: linear-gradient(to bottom, rgb(236, 236, 236), rgba(155, 155, 155, 0.8)); -webkit-background-clip: text; background-clip: text; color: transparent;">
```

**Reemplazar con:**
```svelte
<h1 class="text-6xl md:text-7xl font-secondary font-light tracking-tight pb-2"
    style="background: linear-gradient(to bottom, rgb(var(--color-title-gradient-start)), rgb(var(--color-title-gradient-end) / 0.8)); -webkit-background-clip: text; background-clip: text; color: transparent;">
```

### Criterios de Validacion
- [ ] Light theme: Titulo gris oscuro legible
- [ ] Dark theme: Titulo gris claro (como antes)
- [ ] Her theme: Titulo rose

### Prompts
- Ejecutar: `prompts/3.1-title-gradient-ejecutar.md`
- Validar: `prompts/3.2-title-gradient-validar.md`

---

## Etapa 4: Sticky Headers & Fondos Solidos

### Objetivo
Agregar fondos solidos a headers sticky y eliminar workarounds de gradient.

### Archivos a Modificar
| Archivo | Accion | Lineas |
|---------|--------|--------|
| `src/lib/components/layout/Sidebar.svelte` | MODIFICAR | ~8 lineas |
| `src/lib/components/admin/Evaluations/Leaderboard.svelte` | MODIFICAR | ~2 lineas |
| `src/lib/components/admin/Users/UserList.svelte` | MODIFICAR | ~2 lineas |
| `src/lib/components/admin/Analytics/UserUsage.svelte` | MODIFICAR | ~2 lineas |
| `src/lib/components/admin/Analytics/ModelUsage.svelte` | MODIFICAR | ~2 lineas |
| `src/lib/components/admin/Analytics/Dashboard.svelte` | MODIFICAR | ~2 lineas |

### Cambios Especificos

#### Sidebar.svelte

**1. Header sticky (linea ~903):**
```svelte
<!-- BUSCAR -->
<div class="sidebar px-[0.5625rem] pt-2 pb-1.5 flex justify-between space-x-1 text-gray-600 dark:text-gray-400 sticky top-0 z-10 -mb-3">

<!-- REEMPLAZAR CON -->
<div class="sidebar px-[0.5625rem] pt-2 pb-1.5 flex justify-between space-x-1 text-gray-600 dark:text-gray-400 sticky top-0 z-10 -mb-3 bg-gray-50 dark:bg-gray-950">
```

**2. Eliminar gradient workaround (lineas ~946-950):**
```svelte
<!-- ELIMINAR COMPLETAMENTE ESTE BLOQUE -->
<div
  class="{scrollTop > 0
    ? 'visible'
    : 'invisible'} sidebar-bg-gradient-to-b bg-linear-to-b from-gray-50 dark:from-gray-950 to-transparent from-50% pointer-events-none absolute inset-0 -z-10 -mb-6"
></div>
```

**3. Footer sticky (lineas ~1401-1404):**
```svelte
<!-- BUSCAR -->
<div class="px-1.5 pt-1.5 pb-2 sticky bottom-0 z-50 -mt-3 sidebar">
  <div class="sidebar-bg-gradient-to-t bg-linear-to-t from-gray-50 dark:from-gray-950 to-transparent from-50% pointer-events-none absolute inset-0 -z-10 -mt-6"></div>

<!-- REEMPLAZAR CON -->
<div class="px-1.5 pt-1.5 pb-2 sticky bottom-0 z-50 -mt-3 sidebar bg-gray-50 dark:bg-gray-950">
  <!-- Eliminar el div del gradient -->
```

#### Admin Components (5 archivos)

**Patron a buscar:**
```svelte
class="... sticky top-0 z-10 bg-white dark:bg-gray-900"
```

**Reemplazar con:**
```svelte
class="... sticky top-0 z-10 bg-gray-50 dark:bg-gray-950"
```

### Criterios de Validacion
- [ ] Sidebar header: Fondo solido sin superposicion
- [ ] Sidebar footer: Fondo solido sin superposicion
- [ ] Admin headers: Paleta consistente con sidebar
- [ ] Scroll en sidebar: Sin texto visible a traves del header

### Prompts
- Ejecutar: `prompts/4.1-sticky-headers-ejecutar.md`
- Validar: `prompts/4.2-sticky-headers-validar.md`

---

## Etapa 5: Transparencias & Responsiveness

### Objetivo
Eliminar transparencias problematicas y agregar breakpoints responsivos.

### Archivos a Modificar
| Archivo | Accion | Cambios |
|---------|--------|---------|
| `src/lib/components/chat/MessageInput/VoiceRecording.svelte` | MODIFICAR | Eliminar `/50` |
| `src/lib/components/chat/MessageInput/FilesOverlay.svelte` | MODIFICAR | Eliminar `/50` |
| `src/lib/components/chat/MessageInput/InputMenu.svelte` | MODIFICAR | Eliminar `/50` en hovers |
| `src/lib/components/chat/MessageInput/IntegrationsMenu.svelte` | MODIFICAR | Eliminar `/50` en hovers |
| `src/lib/components/chat/MessageInput.svelte` | MODIFICAR | Eliminar opacidades en queue |
| `src/lib/components/chat/Messages/Message.svelte` | MODIFICAR | Agregar breakpoints |

### Cambios Especificos

#### Patron de Transparencias a Reemplazar

**Buscar y reemplazar globalmente:**
| Buscar | Reemplazar |
|--------|------------|
| `bg-gray-100/50` | `bg-gray-100` |
| `dark:bg-gray-850/50` | `dark:bg-gray-850` |
| `dark:hover:bg-gray-800/50` | `dark:hover:bg-gray-800` |
| `hover:bg-gray-100/50` | `hover:bg-gray-100` |
| `dark:hover:bg-gray-850/50` | `dark:hover:bg-gray-850` |

#### MessageInput.svelte - Queue Container (linea ~1151)

**Buscar:**
```svelte
class="mb-1 mx-2 py-0.5 px-1.5 rounded-2xl bg-gray-900/60 border border-gray-800/50 overflow-hidden"
```

**Reemplazar:**
```svelte
class="mb-1 mx-2 py-0.5 px-1.5 rounded-2xl bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 overflow-hidden"
```

#### Responsiveness - Message.svelte

**Buscar:**
```svelte
class="... max-w-5xl ..."
```

**Reemplazar:**
```svelte
class="... max-w-full sm:max-w-xl md:max-w-2xl lg:max-w-4xl xl:max-w-5xl ..."
```

### Criterios de Validacion
- [ ] Hovers sin transparencia problematica
- [ ] Queue container visible en light mode
- [ ] Mensajes responsivos en mobile (320px, 375px, 414px)
- [ ] No texto superpuesto en ningun componente

### Prompts
- Ejecutar: `prompts/5.1-transparency-responsive-ejecutar.md`
- Validar: `prompts/5.2-transparency-responsive-validar.md`

---

## Checklist de Validacion Final

### Visual (Todos los Temas)
| Test | Light | Dark | OLED | Her |
|------|-------|------|------|-----|
| Chatbox legible | [ ] | [ ] | [ ] | [ ] |
| Titulo visible | [ ] | [ ] | [ ] | [ ] |
| Sidebar sin overlap | [ ] | [ ] | [ ] | [ ] |
| Admin headers | [ ] | [ ] | [ ] | [ ] |
| Hovers funcionan | [ ] | [ ] | [ ] | [ ] |

### Responsiveness
| Viewport | Test |
|----------|------|
| 320px (iPhone SE) | [ ] Chat legible |
| 375px (iPhone) | [ ] Menus funcionales |
| 768px (Tablet) | [ ] Sidebar comportamiento |
| 1024px+ (Desktop) | [ ] Layout completo |

### Funcional
- [ ] Theme switching funciona
- [ ] Theme persiste en reload
- [ ] No errores en consola
- [ ] Build production exitoso

---

## Rollback

Si algo falla en cualquier etapa:

```bash
# Revertir todos los cambios
git checkout HEAD -- src/

# O revertir archivos especificos
git checkout HEAD -- src/tailwind.css
git checkout HEAD -- src/lib/components/chat/MessageInput.svelte
git checkout HEAD -- src/lib/components/layout/Sidebar.svelte
```

---

## Orden de Ejecucion

```
1. [  ] Etapa 1: Variables CSS
2. [  ] Etapa 2: ChatBox
3. [  ] Etapa 3: Titulo
4. [  ] Etapa 4: Sticky Headers
5. [  ] Etapa 5: Transparencias
6. [  ] Validacion Final
7. [  ] Commit
```

**IMPORTANTE:** Las etapas son secuenciales. No saltar pasos.
