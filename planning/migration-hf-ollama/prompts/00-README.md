# Prompts - Migración Ollama a Hugging Face ZeroGPU

> Estructura: 7 fases, 2 prompts por fase (ejecutar/validar) + 1 subfase UX en Fase 5.
> Objetivo: Migrar Ollama de Railway a HF Spaces con GPU H200 gratuita.
> Costo objetivo: $0 (ZeroGPU free tier) o $9/mes (PRO)

## Flujo de Ejecución

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Ejecutar   │ ──► │  Revisar    │ ──► │  Validar    │
│  X.Y-*.md   │     │  cambios    │     │  X.Y-*.md   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                          ┌───────────────────┴───────────────────┐
                          ▼                                       ▼
                    [PASS] ──► Siguiente fase             [FAIL] ──► Corregir y repetir
```

## Índice de Fases

| Fase | Descripción                      | Ejecutar                                 | Validar                                 | Estado    |
| ---- | -------------------------------- | ---------------------------------------- | --------------------------------------- | --------- |
| 0    | Prerrequisitos (cuenta HF, CLI)  | [0.1](./0.1-prereq-ejecutar.md)          | [0.2](./0.2-prereq-validar.md)          | Pendiente |
| 1    | Crear HF Space con Dockerfile    | [1.1](./1.1-space-ejecutar.md)           | [1.2](./1.2-space-validar.md)           | Pendiente |
| 2    | Configurar ZeroGPU               | [2.1](./2.1-zerogpu-ejecutar.md)         | [2.2](./2.2-zerogpu-validar.md)         | Pendiente |
| 3    | Descargar modelos opensource     | [3.1](./3.1-models-ejecutar.md)          | [3.2](./3.2-models-validar.md)          | Pendiente |
| 4    | Conectar Cognitia (Railway)      | [4.1](./4.1-connect-ejecutar.md)         | [4.2](./4.2-connect-validar.md)         | Pendiente |
| 5    | Optimización y modelos extra     | [5.1](./5.1-optimize-ejecutar.md)        | [5.2](./5.2-optimize-validar.md)        | Pendiente |
| 5.3  | UX costos y curación en Cognitia | [5.3](./5.3-cognitia-costos-ejecutar.md) | [5.4](./5.4-cognitia-costos-validar.md) | Pendiente |
| 6    | Cleanup y documentación          | [6.1](./6.1-cleanup-ejecutar.md)         | [6.2](./6.2-cleanup-validar.md)         | Pendiente |

## Orden de Ejecución

```
0. [ ] Prerrequisitos → Cuenta HF + CLI instalado
1. [ ] Crear Space   → Repositorio + Dockerfile + push
2. [ ] ZeroGPU       → Habilitar GPU gratuita
3. [ ] Modelos       → Descargar qwen2.5, phi3, codellama
4. [ ] Conectar      → Actualizar OLLAMA_BASE_URL en Railway
5. [ ] Optimizar     → Modelos extra, ajustes de performance
5.3 [ ] UX Costos    → Curación + costos COP en selector
6. [ ] Cleanup       → Desactivar Railway Ollama, documentar
```

## Dependencias entre Fases

```
Fase 0 (Prereq) ──────► Cuenta HF lista, CLI funcionando
       │
       ▼
Fase 1 (Space) ──────► Repositorio creado, build exitoso
       │
       ▼
Fase 2 (ZeroGPU) ────► GPU H200 habilitada, Space running
       │
       ▼
Fase 3 (Modelos) ────► qwen2.5:7b, phi3, codellama:7b listos
       │
       ▼
Fase 4 (Conectar) ───► Cognitia conectado a HF Space
       │
       ▼
Fase 5 (Optimizar) ──► Modelos extra, performance tuning
       │
       ▼
Fase 6 (Cleanup) ────► Railway Ollama desactivado, docs listas
```

## Modelos Objetivo

| Modelo           | Tamaño | Propósito          | Fase         |
| ---------------- | ------ | ------------------ | ------------ |
| **qwen2.5:7b**   | 4.7GB  | Chat + Coding      | 3            |
| **phi3**         | 2.3GB  | Respuestas rápidas | 3            |
| **codellama:7b** | 3.8GB  | Programación       | 3            |
| gemma2:9b        | 5.4GB  | Razonamiento       | 5 (opcional) |
| llama3.2:3b      | 2GB    | Chat ligero        | 5 (opcional) |
| mistral:7b       | 4.1GB  | Versatilidad       | 5 (opcional) |

## Archivos de Referencia

- **Plan completo:** [`../AGENTIC-PLAN.md`](../AGENTIC-PLAN.md)
- **AS-IS:** [`../AS-IS.md`](../AS-IS.md)
- **TO-BE:** [`../TO-BE.md`](../TO-BE.md)
- **GAP Analysis:** [`../GAP-ANALYSIS.md`](../GAP-ANALYSIS.md)

## Variables de Entorno

```bash
# Hugging Face
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx  # Token con permisos write

# Railway (actualizar en Fase 4)
OLLAMA_BASE_URL=https://[usuario]-cognitia-ollama.hf.space

# Opcional (para Space privado)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

## Criterios de Éxito Global

### Infraestructura

- [ ] HF Space corriendo con ZeroGPU
- [ ] 3 modelos mínimo disponibles (qwen2.5, phi3, codellama)
- [ ] Cognitia conectado y funcionando
- [ ] Latencia < 1s (vs 3-5s anterior)

### Performance

- [ ] GPU H200 activa en requests
- [ ] Tokens/segundo > 50 (vs 5-10 anterior)
- [ ] Modelos hasta 7B funcionando (vs 3.8B max anterior)

### Costos

- [ ] $0/mes (free tier) o $9/mes (PRO)
- [ ] Railway Ollama desactivado
- [ ] Sin costos ocultos

## Rollback

Si algo falla, revertir en Railway:

```bash
OLLAMA_BASE_URL=http://ollama.railway.internal:11434
```

Y reactivar servicio Ollama en Railway Dashboard.
