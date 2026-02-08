# Gap Analysis

## 1. Branding & Identity Gap
| Feature | AS-IS (Open WebUI) | TO-BE (Custom Core) | Gap | Action |
| :--- | :--- | :--- | :--- | :--- |
| **Name** | "Open WebUI" everywhere | Custom Name | Complete mismatch | Rename everything visible in UI. |
| **Logo** | Open WebUI Logo (favicon, header) | [Brand Logo] | Asset replacement needed | Generate/Import new assets. |
| **Colors** | Stock Open WebUI palette | Custom Premium Palette | Visual mismatch | Update Tailwind config & CSS variables. |
| **Meta** | "Open WebUI" titles/desc | Custom SEO data | SEO mismatch | Update `index.html` & Svelte configurations. |

## 2. Technical Gap
| Feature | AS-IS | TO-BE | Gap | Action |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend Code** | Hardcoded strings in ~100+ files | Configurable / Replaced strings | High manual effort | Grep & Replace strategy + i18n review. |
| **Backend Code** | Standard FastAPI | Validated Core | Minor (Compliance check) | Add verification scripts. |
| **Planning** | None / Loose | Agentic `planning/` driven | Process missing | Enforce `task_boundary` & artifact usage. |

## 3. Compliance Gap
| Feature | AS-IS | TO-BE | Gap | Action |
| :--- | :--- | :--- | :--- | :--- |
| **License** | BSD 3-Clause (valid) | BSD 3-Clause (valid) | None | Maintain `LICENSE`. |
| **Branding Usage** | Uses "Open WebUI" | **MUST NOT** use "Open WebUI" | **CRITICAL COMPLIANCE RETROFIT** | Aggressive removal of all branding marks. |

## 4. Risks
- **Upstream Merges**: Future updates from Open WebUI might re-introduce branding.
    - *Mitigation*: Automated checks before merge/commit.
- **Missed Strings**: "Open WebUI" hidden in obscure error messages or logs.
    - *Mitigation*: Comprehensive grep search during verification.
