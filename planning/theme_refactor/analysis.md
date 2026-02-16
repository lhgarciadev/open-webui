# Theme System Analysis: AS-IS vs TO-BE

## AS-IS (Current State)

### Implementation
- **Location**: `src/lib/components/chat/Settings/General.svelte` in `applyTheme` function.
- **Mechanism**:
    - Manually toggles `.dark` class on `html`.
    - Hardcodes CSS variable overrides via JS for specific themes (`oled-dark`, `her`, `dark`).
    - CSS variables (e.g., `--color-gray-800`) are manipulated directly in the DOM style.
    - `src/app.css` contains some `:root` variables but relies on `.dark` class for dark mode overrides.

### Issues
- **Inconsistency**: Background colors ("fondo") are not consistently applied across different "types" of themes because they rely on ad-hoc JS overrides rather than a structured CSS system.
- **Maintenance**: Adding a new theme requires modifying JS logic in the settings component and manual variable overrides.
- **Scalability**: "Fondo por tipo" (Background by type) is difficult to implement with the current manual override approach.
- **Performance**: JS-based style injection triggers unnecessary repaints/style calcs compared to pure CSS class switching.

## TO-BE (Desired State)

### Solution
- **CSS-First Architecture**: Move theme definitions out of JS and into `src/app.css` (or separate CSS files).
- **Data-Theme Attribute**: Use `data-theme="oled-dark"`, `data-theme="her"`, etc., on the `html` element instead of just `.dark`.
- **Scoped Variables**: Define all color variables (surface, text, brand) within these `[data-theme="..."]` scopes in CSS.
- **Simplified JS**: The `applyTheme` function should only handle switching the `data-theme` attribute and the `.dark` class (for Tailwind dark mode compatibility).

### Benefits
- **Consistent Backgrounds**: Each theme type will have its specific background variables defined in CSS.
- **Easy Extension**: Adding a theme is just adding a new CSS block.
- **Cleaner Code**: Removes specific style manipulation from `General.svelte`.
