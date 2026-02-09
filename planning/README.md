# Planning README (Workflow y Ruta)

## 1. Que es este proyecto
- Objetivo: Transformar el fork de Open WebUI en una plataforma con identidad propia y enfoque agentic.
- Alcance: Rebranding del frontend, preservando el backend y sus avisos de licencia.

## 2. Reglas criticas (no negociables)
- Gate legal obligatorio antes de remover branding: ver [planning/legal_compliance.md](planning/legal_compliance.md).
- Compliance de branding y QA antes de merge: ver [planning/compliance_checklist.md](planning/compliance_checklist.md).
- El backend conserva avisos BSD originales: ver [planning/base.md](planning/base.md).

## 3. Workflow (camino feliz)
1. Leer base y contexto:
   - [planning/base.md](planning/base.md)
   - [planning/context.md](planning/context.md)
2. Confirmar Gate Legal (Path A o Path B):
   - [planning/legal_compliance.md](planning/legal_compliance.md)
3. Ejecutar plan de implementacion:
   - [planning/implementation_plan.md](planning/implementation_plan.md)
4. Validar con checklist (bloqueante):
   - [planning/compliance_checklist.md](planning/compliance_checklist.md)
5. Si hay sync upstream, seguir el playbook:
   - [planning/upstream_sync_playbook.md](planning/upstream_sync_playbook.md)

## 4. Documentos clave (orden recomendado)
- [planning/base.md](planning/base.md)
- [planning/legal_compliance.md](planning/legal_compliance.md)
- [planning/init.md](planning/init.md)
- [planning/implementation_plan.md](planning/implementation_plan.md)
- [planning/compliance_checklist.md](planning/compliance_checklist.md)
- [planning/upstream_sync_playbook.md](planning/upstream_sync_playbook.md)
- [planning/specs.md](planning/specs.md)
- [planning/as_is_to_be.md](planning/as_is_to_be.md)
- [planning/gap_analysis.md](planning/gap_analysis.md)
- [planning/context.md](planning/context.md)
- [planning/agentic_prompts.md](planning/agentic_prompts.md)

## 5. Guia rapida para nuevos devs
- Lectura minima:
  - [planning/base.md](planning/base.md)
  - [planning/legal_compliance.md](planning/legal_compliance.md)
  - [planning/implementation_plan.md](planning/implementation_plan.md)
  - [planning/compliance_checklist.md](planning/compliance_checklist.md)
- Si hay conflictos de branding, detenerse y validar Path A o Path B.
- Si hay conflictos con upstream, seguir el orden de prioridad del playbook.

## 6. Mantenimiento
- Cadencia sugerida de sync upstream: cada 2-4 semanas.
- Nunca hacer merge a `main` sin pasar el checklist.
- Registrar el Path legal elegido en el PR o en planning/.
