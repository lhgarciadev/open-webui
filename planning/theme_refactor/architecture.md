# Theme System Architecture

> **UPDATED**: 2026-02-16 - Architecture revised after discovering Tailwind v4 compilation issue.

## Overview

This document outlines the architectural changes required to implement a robust theme system with consistent background handling.

**Critical Discovery**: The original architecture was correct conceptually, but `[data-theme]` selectors in `app.css` are **not compiled** by Tailwind CSS v4. The solution is to move them to `tailwind.css` inside `@layer base`.

## Revised Component Changes

### 1. `src/tailwind.css` (PRIMARY CHANGE)

**Why here?**: Tailwind v4 only compiles CSS that is:
- Inside `@layer` directives
- Using `@apply` utilities
- Standard CSS in the same file as `@import 'tailwindcss'`

**Add inside `@layer base`:**
```css
@layer base {
  :root, [data-theme="light"] {
    --color-surface-base: 249 250 251;
    --color-surface-elevated: 255 255 255;
    /* ... */
  }

  .dark, [data-theme="dark"] {
    --color-surface-base: 23 23 23;
    /* ... */
  }

  [data-theme="oled-dark"] {
    --color-surface-base: 0 0 0;
    /* ... */
  }

  [data-theme="her"] {
    --color-surface-base: 255 250 250;
    /* ... */
  }
}
```

### 2. `src/app.css` (CLEANUP)

- **REMOVE**: All `[data-theme]` selector blocks (now in tailwind.css)
- **REMOVE**: Hardcoded `body { background: #fff }` and `.dark body { background: #171717 }`
- **ADD**: Variable-based body style:
  ```css
  body {
    background-color: rgb(var(--color-surface-base));
    color: rgb(var(--color-text-primary));
  }
  ```

### 3. `tailwind.config.js` (NO CHANGES NEEDED)

Already correctly configured:
```javascript
surface: {
    base: 'var(--color-surface-base)',
    elevated: 'var(--color-surface-elevated)',
    overlay: 'var(--color-surface-overlay)',
}
```

### 4. `General.svelte` (NO CHANGES NEEDED)

The `applyTheme` function is already correct:
- Sets `data-theme` attribute
- Toggles `.dark` class appropriately
- The issue was CSS not being compiled, not JS logic

## Updated Data Flow

```
1. User selects theme in General.svelte
         │
         ▼
2. themeChangeHandler() called
         │
         ├── localStorage.setItem('theme', _theme)
         │
         └── applyTheme(_theme)
                  │
                  ├── Sets data-theme attribute on <html>
                  │
                  └── Toggles .dark class for Tailwind utilities
                           │
                           ▼
3. CSS Variables in @layer base (tailwind.css) ACTIVATE
         │
         ▼
4. body { background: rgb(var(--color-surface-base)) } RESPONDS
         │
         ▼
5. All components using surface-* utilities update
```

## Implementation Reference

See `IMPLEMENTATION_PLAN.md` for step-by-step implementation instructions.
