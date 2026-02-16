# Theme System Implementation Plan

**Date:** 2026-02-16
**Estimated Effort:** 2-4 hours
**Files to Modify:** 3 files
**Risk Level:** Medium (visual changes across entire app)

---

## Pre-Implementation Checklist

- [ ] Backup current state: `git stash` or commit current changes
- [ ] Ensure dev server is running: `npm run dev`
- [ ] Have browser DevTools open for live testing
- [ ] Test current broken state to establish baseline

---

## Phase 1: Move Theme Variables to Tailwind Layer

### Step 1.1: Update `src/tailwind.css`

**File:** `src/tailwind.css`

**Action:** Add theme variable definitions inside `@layer base` block.

**Insert AFTER** the existing `@layer base` block (around line 72), add a NEW `@layer base` block:

```css
@layer base {
  /* ============================================
     THEME SYSTEM - CSS Custom Properties
     These variables drive the entire color system.
     They MUST be in @layer base for Tailwind v4 to compile them.
     ============================================ */

  /* Light Theme (Default) */
  :root,
  [data-theme="light"] {
    /* Surface Colors */
    --color-surface-base: 249 250 251;
    --color-surface-elevated: 255 255 255;
    --color-surface-overlay: 229 231 235;

    /* Text Colors */
    --color-text-primary: 15 23 42;
    --color-text-secondary: 71 85 105;
    --color-text-muted: 100 116 139;

    /* Gray Scale */
    --color-gray-50: 249 249 249;
    --color-gray-100: 236 236 236;
    --color-gray-200: 227 227 227;
    --color-gray-300: 205 205 205;
    --color-gray-400: 180 180 180;
    --color-gray-500: 155 155 155;
    --color-gray-600: 103 103 103;
    --color-gray-700: 78 78 78;
    --color-gray-800: 51 51 51;
    --color-gray-850: 38 38 38;
    --color-gray-900: 23 23 23;
    --color-gray-950: 13 13 13;

    /* Brand Colors - Cognitia Blue */
    --color-brand-50: 239 246 255;
    --color-brand-100: 219 234 254;
    --color-brand-200: 191 219 254;
    --color-brand-300: 147 197 253;
    --color-brand-400: 96 165 250;
    --color-brand-500: 59 130 246;
    --color-brand-600: 37 99 235;
    --color-brand-700: 29 78 216;
    --color-brand-800: 30 64 175;
    --color-brand-900: 30 58 138;
  }

  /* Dark Theme */
  .dark,
  [data-theme="dark"] {
    /* Surface Colors */
    --color-surface-base: 23 23 23;
    --color-surface-elevated: 38 38 38;
    --color-surface-overlay: 51 51 51;

    /* Text Colors */
    --color-text-primary: 248 250 252;
    --color-text-secondary: 148 163 184;
    --color-text-muted: 100 116 139;

    /* Gray Scale - Inverted for dark */
    --color-gray-50: 249 249 249;
    --color-gray-100: 236 236 236;
    --color-gray-200: 227 227 227;
    --color-gray-300: 205 205 205;
    --color-gray-400: 180 180 180;
    --color-gray-500: 155 155 155;
    --color-gray-600: 103 103 103;
    --color-gray-700: 78 78 78;
    --color-gray-800: 51 51 51;
    --color-gray-850: 38 38 38;
    --color-gray-900: 23 23 23;
    --color-gray-950: 13 13 13;
  }

  /* OLED Dark Theme - True Black */
  [data-theme="oled-dark"] {
    /* Surface Colors - Pure black for OLED */
    --color-surface-base: 0 0 0;
    --color-surface-elevated: 5 5 5;
    --color-surface-overlay: 16 16 16;

    /* Text Colors */
    --color-text-primary: 248 250 252;
    --color-text-secondary: 148 163 184;
    --color-text-muted: 100 116 139;

    /* Gray Scale - Deep blacks */
    --color-gray-800: 16 16 16;
    --color-gray-850: 5 5 5;
    --color-gray-900: 0 0 0;
    --color-gray-950: 0 0 0;
  }

  /* Her Theme - Rose/Pink */
  [data-theme="her"] {
    /* Surface Colors - Warm rose tints */
    --color-surface-base: 255 250 250;
    --color-surface-elevated: 255 255 255;
    --color-surface-overlay: 255 228 230;

    /* Text Colors */
    --color-text-primary: 23 23 23;
    --color-text-secondary: 71 85 105;
    --color-text-muted: 100 116 139;

    /* Brand Colors - Rose palette */
    --color-brand-50: 255 241 242;
    --color-brand-100: 255 228 230;
    --color-brand-200: 254 205 211;
    --color-brand-300: 253 164 175;
    --color-brand-400: 251 113 133;
    --color-brand-500: 244 63 94;
    --color-brand-600: 225 29 72;
    --color-brand-700: 190 18 60;
    --color-brand-800: 159 18 57;
    --color-brand-900: 136 19 55;
  }

  /* Semantic Colors - Shared across all themes */
  :root {
    --color-success: 34 197 94;
    --color-warning: 245 158 11;
    --color-error: 239 68 68;
    --color-info: 59 130 246;
  }
}
```

### Step 1.2: Verification

After saving, check browser DevTools:

```javascript
// Should return a value like "23 23 23" for dark theme
getComputedStyle(document.documentElement).getPropertyValue('--color-surface-base')
```

---

## Phase 2: Update Body Styles in `app.css`

### Step 2.1: Remove Hardcoded Body Colors

**File:** `src/app.css`

**Find and REMOVE** these lines (around lines 882-890):

```css
/* DELETE THIS BLOCK */
body {
	background: #fff;
	color: #000;
}

.dark body {
	background: #171717;
	color: #eee;
}
```

### Step 2.2: Add Variable-Based Body Styles

**Replace with:**

```css
body {
	background-color: rgb(var(--color-surface-base));
	color: rgb(var(--color-text-primary));
	transition: background-color 0.2s ease, color 0.2s ease;
}
```

### Step 2.3: Remove Duplicate Theme Variable Definitions

**Find and REMOVE** the `[data-theme]` blocks in `app.css` (lines ~38-206) since they're now in `tailwind.css`:

```css
/* DELETE ALL THESE BLOCKS - they're now in tailwind.css */

/* Default (Light) Theme */
:root,
[data-theme='light'] {
  /* ... all variables ... */
}

[data-theme='dark'] {
  /* ... all variables ... */
}

[data-theme='oled-dark'] {
  /* ... all variables ... */
}

[data-theme='her'] {
  /* ... all variables ... */
}
```

**KEEP** only:
- The `@reference` directive at the top
- Font definitions
- The `--app-text-scale` variable in `:root`
- All other utility classes and styles

---

## Phase 3: Update Splash Screen in `app.html`

### Step 3.1: Update Splash Background

**File:** `src/app.html`

**Find** the inline style block (around line 152-164):

```css
#splash-screen {
	background: #fff;
}

html.dark #splash-screen {
	background: #000;
}
```

**Replace with:**

```css
#splash-screen {
	background: rgb(var(--color-surface-base, 255 255 255));
}
```

This uses CSS variable with a fallback for initial load.

---

## Phase 4: Testing & Validation

### Step 4.1: Manual Testing Checklist

Open browser to `http://localhost:8080` and test each theme:

| Theme | Background Expected | Test Result |
|-------|---------------------|-------------|
| Light | Light gray `#f9fafb` | [ ] Pass / [ ] Fail |
| Dark | Dark gray `#171717` | [ ] Pass / [ ] Fail |
| OLED Dark | Pure black `#000000` | [ ] Pass / [ ] Fail |
| Her | Rose tint `#fffafa` | [ ] Pass / [ ] Fail |

### Step 4.2: DevTools Verification

Run in browser console:

```javascript
// Test 1: Check data-theme is set
console.log('data-theme:', document.documentElement.getAttribute('data-theme'));

// Test 2: Check surface variable changes
['light', 'dark', 'oled-dark', 'her'].forEach(theme => {
  document.documentElement.setAttribute('data-theme', theme);
  if (theme === 'dark' || theme === 'oled-dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  const surfaceBase = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-surface-base').trim();
  const bodyBg = getComputedStyle(document.body).backgroundColor;
  console.log(`${theme}: surface=${surfaceBase}, body=${bodyBg}`);
});
```

**Expected output:**
```
light: surface=249 250 251, body=rgb(249, 250, 251)
dark: surface=23 23 23, body=rgb(23, 23, 23)
oled-dark: surface=0 0 0, body=rgb(0, 0, 0)
her: surface=255 250 250, body=rgb(255, 250, 250)
```

### Step 4.3: Persistence Test

1. Select "OLED Dark" theme in Settings
2. Reload the page
3. Verify background is still pure black
4. Verify localStorage.theme === 'oled-dark'

---

## Phase 5: Cleanup

### Step 5.1: Remove Unused Code

After verification, ensure these are cleaned up:

- [ ] No duplicate CSS variable definitions
- [ ] No hardcoded color values for body/background
- [ ] No console.log statements left in theme code

### Step 5.2: Commit Changes

```bash
git add src/tailwind.css src/app.css src/app.html
git commit -m "fix(theme): move CSS variables to @layer base for Tailwind v4 compatibility

- Move all [data-theme] variable definitions to tailwind.css @layer base
- Replace hardcoded body colors with CSS variable references
- Update splash screen to use CSS variables
- Fixes OLED dark theme showing wrong background
- Fixes surface colors not changing between themes

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Rollback Plan

If issues arise:

```bash
# Revert all changes
git checkout HEAD -- src/tailwind.css src/app.css src/app.html

# Or restore from stash if you stashed before starting
git stash pop
```

---

## Post-Implementation Monitoring

1. **Visual QA**: Check all major pages (chat, settings, admin) in each theme
2. **Mobile Testing**: Verify themes work on mobile viewport
3. **Performance**: Check no layout shifts on theme change
4. **Accessibility**: Verify contrast ratios meet WCAG AA standards

---

## Files Modified Summary

| File | Changes |
|------|---------|
| `src/tailwind.css` | Add ~100 lines of theme variables in @layer base |
| `src/app.css` | Remove ~170 lines of [data-theme] blocks, update body styles |
| `src/app.html` | Update splash screen background to use CSS variable |

**Total Lines Changed:** ~280 lines (mostly removals and reorganization)
