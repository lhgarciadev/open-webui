# Decision Legal: Branding y Licencia

> **Estado**: APROBADO
> **Fecha**: 2026-02-12
> **Version**: 1.0

---

## Decision

**Path Seleccionado**: **A** (Permitido remover branding)

---

## Justificacion

El proyecto cumple con los criterios de la Clausula 5 de la licencia BSD de Open WebUI:

| Criterio               | Requisito                  | Estado |
| ---------------------- | -------------------------- | ------ |
| **Usuarios finales**   | < 50 en periodo de 30 dias | CUMPLE |
| **Tipo de deployment** | Interno/privado            | CUMPLE |
| **Distribucion**       | No es distribucion amplia  | CUMPLE |

---

## Implicaciones

### Permitido:

- Remover completamente el logo de Open WebUI
- Remover el nombre "Open WebUI" de la interfaz visible
- Reemplazar favicon, splash screen, y assets visuales
- Usar nombre de marca propio en toda la UI
- Crear identidad visual completamente nueva

### Requerido (No Negociable):

- Mantener avisos de copyright BSD en el codigo fuente del backend
- Mantener archivo LICENSE original
- No remover atribuciones en archivos de codigo fuente

### Prohibido:

- Exceder 50 usuarios finales sin obtener licencia Enterprise
- Remover avisos de copyright del codigo fuente
- Distribuir ampliamente sin ajustar el path legal

---

## Validacion

```
Pregunta: El deployment tendra menos de 50 usuarios finales?
Respuesta: SI

Pregunta: Es un deployment interno/privado?
Respuesta: SI

Pregunta: Se planea distribucion amplia (SaaS publico, redistribucion)?
Respuesta: NO

Resultado: PATH A APLICA
```

---

## Compromiso

Al proceder con Path A, el equipo se compromete a:

1. **Monitorear usuarios**: No exceder 50 usuarios en ningun periodo de 30 dias
2. **Escalar apropiadamente**: Si se requieren mas usuarios, obtener licencia Enterprise antes de deployment
3. **Mantener compliance**: Preservar avisos BSD en codigo fuente del backend
4. **Documentar cambios**: Registrar todos los cambios de branding realizados

---

## Registro de Aprobacion

| Rol                 | Fecha      | Estado      |
| ------------------- | ---------- | ----------- |
| Product Owner       | 2026-02-12 | APROBADO    |
| Arquitecto (Claude) | 2026-02-12 | DOCUMENTADO |
| Tech Lead           | Pendiente  | -           |

---

## Referencias

- Licencia original: `LICENSE`
- Analisis legal completo: `planning/legal_compliance.md`
- Plan de implementacion: `planning/agentic_master_plan.md`

---

> Este documento debe ser revisado si cambian las condiciones de deployment.
