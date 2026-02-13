# Cognitia Brand Assets

> Generated: 2026-02-12
> Brand: Cognitia
> Status: Stage 1 Complete

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Primary | `#3b82f6` | Main brand color (blue-500) |
| Primary Light | `#60a5fa` | Accents, secondary elements (blue-400) |
| Primary Dark | `#1e40af` | Dark accents (blue-800) |
| Surface | `#0f172a` | Dark mode background (slate-900) |
| Surface Light | `#f8fafc` | Light mode background (slate-50) |
| Text Primary | `#f8fafc` | Primary text on dark (slate-50) |
| Text Dark | `#0f172a` | Primary text on light (slate-900) |

## Logo Design

The Cognitia logo features a hexagonal neural network symbol representing:
- **Hexagon**: Stability, efficiency, interconnection
- **Neural nodes**: AI/cognitive intelligence
- **Connections**: Knowledge networks, data flow

## Assets Generated

### Source Files (`branding/source/`)
| File | Description |
|------|-------------|
| `favicon.svg` | Favicon with dark background (192x192 viewBox) |
| `favicon-dark.svg` | Favicon variant for dark contexts |
| `logo.svg` | Full logo with icon and text |
| `splash.svg` | Splash screen - light mode |
| `splash-dark.svg` | Splash screen - dark mode |

### Output Files (`branding/output/`)
| File | Dimensions | Usage |
|------|------------|-------|
| `favicon.png` | 192x192 | Primary favicon |
| `favicon-dark.png` | 192x192 | Dark mode favicon |
| `favicon-96x96.png` | 96x96 | Small favicon |
| `favicon.ico` | Multi | Legacy browsers |
| `apple-touch-icon.png` | 180x180 | iOS home screen |
| `web-app-manifest-192x192.png` | 192x192 | PWA icon |
| `web-app-manifest-512x512.png` | 512x512 | PWA icon large |
| `logo.png` | 512x512 | General logo use |
| `splash.png` | 512x512 | Light mode splash |
| `splash-dark.png` | 512x512 | Dark mode splash |

### Deployed to `static/static/`
All assets above have been copied to their final locations.

## Conversion Script

Use `branding/convert-assets.mjs` to regenerate PNGs from SVG sources:

```bash
node branding/convert-assets.mjs
```

## Next Steps

- [ ] Stage 2: Update configuration files (identity.ts, manifest.json)
- [ ] Stage 3: Implement CSS color system
- [ ] Stage 4: Update component text references

## Design Guidelines

- Maintain minimum 44px touch targets for interactive elements
- Ensure WCAG AA contrast ratio (4.5:1 for normal text)
- Use `#3b82f6` as primary action color
- Dark mode default: `#0f172a` background
