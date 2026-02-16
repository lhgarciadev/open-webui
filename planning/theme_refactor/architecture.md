# Theme System Architecture

## Overview
This document outlines the architectural changes required to implement a robust theme system with consistent background handling.

## Component Changes

### 1. `src/app.css`
- **Introduction of `[data-theme]` selectors**:
    - `[data-theme="light"]` (Default variables)
    - `[data-theme="dark"]` (Dark mode overrides)
    - `[data-theme="oled-dark"]` (Deep black background overrides)
    - `[data-theme="her"]` (Specific branding colors)
- **Variable Definitions**:
    - Explicitly define `--color-surface-base`, `--color-surface-elevated`, `--color-surface-overlay` effectively for each theme.
    - Ensure Tailwind classes like `bg-gray-900` map correctly to these variables or their palette equivalents.

### 2. `tailwind.config.js` (Verification)
- Ensure `colors.surface` maps to CSS variables:
    ```javascript
    surface: {
        base: 'var(--color-surface-base)',
        elevated: 'var(--color-surface-elevated)',
        overlay: 'var(--color-surface-overlay)',
    }
    ```
- Ensure `colors.gray` maps to variables that change with the theme (already seems to be done, check specifics).

### 3. `src/lib/components/chat/Settings/General.svelte`
- **Refactor `applyTheme`**:
    - Remove manual `document.documentElement.style.setProperty` calls.
    - Instead, set `document.documentElement.setAttribute('data-theme', themeName)`.
    - Ensure `.dark` class is toggled correctly based on whether the theme is "dark-like".

## Data Flow
1. User selects theme in `General.svelte`.
2. `themeChangeHandler` updates store and `localStorage`.
3. `applyTheme` is called.
4. `applyTheme` updates `DOM attributes` (`class="dark"`, `data-theme="..."`).
5. Browser re-paints using new CSS variables defined in `app.css`.

## CSS Variable Structure
```css
:root, [data-theme="light"] {
    --color-surface-base: var(--color-gray-50); /* or white */
    --color-text-primary: var(--color-gray-900);
}

[data-theme="dark"], .dark {
    --color-surface-base: var(--color-gray-900);
    --color-text-primary: var(--color-gray-50);
}

[data-theme="oled-dark"] {
    --color-surface-base: #000000;
    --color-surface-elevated: #101010;
    /* ... other overrides ... */
}
```
