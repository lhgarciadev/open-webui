# Migración Ollama: Railway → Hugging Face Spaces

## Resumen Ejecutivo

Este directorio contiene la documentación completa para migrar el servicio Ollama desde Railway hacia Hugging Face Spaces con **ZeroGPU**, habilitando GPU H200 (~70GB VRAM) **GRATIS** para inferencia de modelos LLM.

## Documentos

| Documento | Descripción |
|-----------|-------------|
| [AS-IS.md](./AS-IS.md) | Estado actual de la infraestructura (Railway CPU) |
| [TO-BE.md](./TO-BE.md) | Estado objetivo (Hugging Face ZeroGPU) |
| [GAP-ANALYSIS.md](./GAP-ANALYSIS.md) | Análisis de brechas y modelos recomendados |
| [AGENTIC-PLAN.md](./AGENTIC-PLAN.md) | **Plan agéntico por fases** (ejecutar) |
| [prompts/](./prompts/00-README.md) | Prompts por fase (incluye UX de costos/curación) |

## Evaluación Final

**Puntuación: 8/10** ⬆️ (mejorada por ZeroGPU gratuito)

### Comparación

| Factor | Railway (Actual) | HF ZeroGPU (Objetivo) |
|--------|------------------|------------------------|
| GPU | No disponible | **H200 (70GB VRAM)** |
| Costo | $5-10/mes | **$0** (o $9 PRO) |
| Latencia | 2-5s | **0.3-0.8s** |
| Modelos | <4B params | **Hasta 70B** |
| Complejidad | Baja | Media |

### Modelos Recomendados (Free Tier)

| Modelo | Params | Calidad | Uso Principal |
|--------|--------|---------|---------------|
| **Qwen2.5-7B** | 7B | ⭐⭐⭐⭐⭐ | Chat + Coding |
| **phi3** | 3.8B | ⭐⭐⭐⭐ | Respuestas rápidas |
| **CodeLlama-7B** | 7B | ⭐⭐⭐⭐ | Programación |
| **Gemma2-9B** | 9B | ⭐⭐⭐⭐⭐ | Razonamiento |

### Beneficios Clave

1. **GPU GRATIS**: ZeroGPU ofrece H200 sin costo (con cuota diaria)
2. **10x más rápido**: Inferencia en 0.3-0.8s vs 2-5s
3. **Modelos grandes**: Soporta hasta 70B parámetros
4. **PRO opcional**: $9/mes para 8x más cuota y prioridad
5. **UX mejorado**: Costos en COP y curación de modelos en Cognitia

## Decisión

✅ **Proceder con migración a Hugging Face ZeroGPU**

- GPU H200 gratuita (mejor que T4/A10G pagados)
- Cognitia permanece en Railway (sin cambios)
- Solo Ollama migra a HF Space
- Fallback a OpenAI siempre disponible

## Próximo Paso

Ejecutar [AGENTIC-PLAN.md](./AGENTIC-PLAN.md) fase por fase.

---

- **Proyecto**: Cognitia
- **Fecha**: 2026-02-15
- **Estado**: Listo para ejecutar
