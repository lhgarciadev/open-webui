# Legal Validation: Branding & License Implications

## Executive Summary
> [!CAUTION]
> **CRITICAL CONFLICT DETECTED**: The project goal to "completely remove" Open WebUI branding (**Project Requirement**) is in direct conflict with **Clause 4** of the included `LICENSE` file (**Legal Requirement**), unless a specific exemption applies.

## 1. The Conflict Analysis

### A. The License Constraint (Clause 4)
The `LICENSE` file states:
> *"licensees are **strictly prohibited from altering, removing, obscuring, or replacing** any 'Open WebUI' branding... in any deployment or distribution... except as explicitly set forth in Clauses 5 and 6."*

This is a **restrictive covenant**. Unlike standard open source licenses that prevent you from *using* a trademark (passing off), this license **forces** you to display the trademark.

### B. The Project Requirement (`planning/base.md`)
The planning document states:
> *"El frontend debe ser completamente distinto... No uses el nombre 'Open WebUI' ni el logo... Si se detecta algún branding de Open WebUI, se debe eliminar"*

### C. The Implication
Proceeding with the "Clean Slate" rebranding plan (removing the logo/name) constitutes a **Material Breach of License** unless you qualify for an exemption.

## 2. Exemption Analysis (Clause 5)
You can only legally proceed with the rebranding if you meet one of these criteria:

1.  **Small Scale Deployment**:
    - *Condition*: Total end users < 50 (rolling 30-day period).
    - *Implication*: If this is for internal use, a small team, or personal use, **you are compliant**. You can remove the branding.

2.  **Official Contributor**:
    - *Condition*: You have merged code into the official repo AND have written permission.
    - *Implication*: Unlikely standard case.

3.  **Enterprise License**:
    - *Condition*: You have a paid/signed agreement with the Open WebUI creators.
    - *Implication*: If you have this, **you are compliant**.

## 3. Recommended Action Path

### Scenario A: You have < 50 Users (or Enterprise License)
- **Status**: ✅ Safe to Proceed.
- **Action**: Continue with `planning/init.md` and `implementation_plan.md` as written. The license permits removal for your use case.

### Scenario B: You plan to distribute widely / > 50 Users
- **Status**: 🛑 **STOP**. High Legal Risk.
- **Action**:
    1.  **Do NOT remove** the "Powered by Open WebUI" text or the logo from the footer/about section.
    2.  **Adapt the Plan**: Change "Removal" to "Co-existence". Create your own brand identity (Theme, Layout, Name) but **retain the attribution** required by the license in a visible spot (e.g., "Built on Open WebUI").
    3.  **Revised Goal**: "Visual Distinction without White-labeling".

## 4. Backend vs Frontend
- **Backend (BSD 3-Clause)**: The source code copyright headers MUST remain. This is non-negotiable and compatible with our plan.
- **Frontend**: The visual branding is the only point of contention.

## 5. Conclusion for "Director Creativo"
To fulfill the request lawfully, we must know the **deployment scale**.
- If **Internal/Small**: We burn the branding down. (Plan remains valid).
- If **Public/Large**: We must keep a "Powered by" watermark. (Plan needs adjustment).

## Decision Gate (Required)
Before any branding removal work starts, the team must record one of the following:
- **Path A (Allowed to remove branding)**: Deployment is strictly limited to < 50 end users in any rolling 30-day period, or there is a signed enterprise agreement.
- **Path B (Branding must remain visible)**: Deployment may exceed 50 users or will be distributed widely.

This decision must be documented in the PR description or a planning update before Phase 1 work proceeds.
