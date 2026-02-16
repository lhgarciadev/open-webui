# GAP Analysis: Railway → Hugging Face

## Resumen Ejecutivo

Este documento analiza las brechas entre el estado actual (Railway CPU) y el estado objetivo (Hugging Face ZeroGPU/Spaces) para el servicio Ollama de Cognitia.

---

## Matriz de Brechas

| Categoría | AS-IS (Railway) | TO-BE (Hugging Face) | Gap | Criticidad |
|-----------|-----------------|----------------------|-----|------------|
| **Cómputo** | CPU-only | GPU H200 (ZeroGPU) | Alto | 🔴 Crítica |
| **VRAM** | N/A | ~70GB (ZeroGPU) | Alto | 🔴 Crítica |
| **Modelos** | phi3 (3.8B) | Hasta 70B | Alto | 🟡 Media |
| **Latencia** | 2-5s | 0.3-0.8s | Alto | 🔴 Crítica |
| **Costo** | $5-10/mes | $0-9/mes | Bajo | 🟢 Baja |
| **Networking** | Interno Railway | HTTPS público | Medio | 🟡 Media |
| **Deployment** | Railway CLI | HF Space/Git | Bajo | 🟢 Baja |
| **Autenticación** | Interna | HF Token | Medio | 🟡 Media |
| **UX Modelos** | Selector sin costos | Costos COP + curación | Medio | 🟡 Media |

---

## Análisis Detallado por Categoría

### 1. Cómputo y Hardware

**Gap**: Railway no ofrece GPU; HF ofrece ZeroGPU gratuito

| Aspecto | Railway | Hugging Face | Acción |
|---------|---------|--------------|--------|
| GPU | No disponible | H200 (ZeroGPU) gratis | Migrar a HF Space |
| CPU | 1-2 vCPU | 2 vCPU (free) | Mantener para fallback |
| RAM | 2-4GB | ~16GB (con GPU) | Aprovechar HF |
| VRAM | N/A | ~70GB compartida | Habilitar modelos grandes |

**Solución**: Usar ZeroGPU de Hugging Face (gratis para todos, 8x cuota con PRO $9/mes)

---

### 2. Modelos Soportados

**Gap**: Railway limita a modelos <4B; HF permite hasta 70B+

#### Modelos Recomendados para ZeroGPU (Gratis)

| Modelo | Parámetros | Calidad | Uso Recomendado |
|--------|------------|---------|-----------------|
| **phi-3-mini** | 3.8B | ⭐⭐⭐⭐ | Chat general, razonamiento |
| **Llama-3.2-3B** | 3B | ⭐⭐⭐⭐ | Chat rápido, multiusos |
| **Qwen2.5-7B** | 7B | ⭐⭐⭐⭐⭐ | Mejor calidad, coding |
| **Mistral-7B** | 7B | ⭐⭐⭐⭐ | Balance calidad/velocidad |
| **Gemma-2-9B** | 9B | ⭐⭐⭐⭐⭐ | Razonamiento avanzado |
| **CodeLlama-7B** | 7B | ⭐⭐⭐⭐ | Programación |

#### Modelos Premium (PRO recomendado por cuota)

| Modelo | Parámetros | Calidad | Uso Recomendado |
|--------|------------|---------|-----------------|
| **Llama-3.1-70B** | 70B | ⭐⭐⭐⭐⭐ | Máxima calidad |
| **Qwen2.5-72B** | 72B | ⭐⭐⭐⭐⭐ | Coding enterprise |
| **Mixtral-8x7B** | 47B | ⭐⭐⭐⭐⭐ | MoE eficiente |

**Recomendación**: Comenzar con tier gratuita + phi-3 y Qwen2.5-7B. Si la cuota se agota frecuentemente, upgrade a PRO ($9/mes).

---

### 3. Networking y Conectividad

**Gap**: Comunicación interna vs API pública HTTPS

| Aspecto | Railway | Hugging Face | Impacto |
|---------|---------|--------------|---------|
| Protocolo | HTTP interno | HTTPS público | +seguridad |
| URL | `ollama.railway.internal` | `*.hf.space` | Cambio config |
| Latencia red | <1ms | ~50-100ms | Mínimo |
| Autenticación | Ninguna | HF Token opcional | +seguridad |

**Acciones**:
1. Actualizar `OLLAMA_BASE_URL` en Railway
2. Agregar `HF_TOKEN` si Space es privado
3. Modificar headers en `ollama.py` si es necesario

---

### 4. Deployment y CI/CD

**Gap**: Railway CLI vs HF Git-based deployment

| Aspecto | Railway | Hugging Face |
|---------|---------|--------------|
| CLI | `railway up` | `git push` o HF CLI |
| Config | `railway.json` | `README.md` YAML |
| Docker | `Dockerfile` | `Dockerfile` (compatible) |
| Variables | Railway Dashboard | HF Space Settings |

**Acciones**:
1. Crear repositorio HF Space
2. Adaptar Dockerfile actual
3. Configurar variables de entorno

---

### 5. Costos

**Gap**: Modelo de pricing diferente

| Escenario | Railway | HF Free | HF PRO |
|-----------|---------|---------|--------|
| Ollama CPU | $5-10/mes | $0 | $0 |
| Ollama GPU | N/A | $0 (cuota) | $9/mes |
| **Total con GPU** | N/A | **$0** | **$9/mes** |

**Ahorro potencial**: $0-10/mes (gratis) o mismo costo con GPU ($9 PRO vs $5-10 Railway)

---

### 5.1 UX de Costos y Curación (Cognitia)

**Gap**: El selector actual no educa sobre costos y muestra demasiados modelos.

| Aspecto | AS-IS | TO-BE | Impacto |
|---------|-------|-------|---------|
| Costos | No visibles | COP estimado (1 USD = 4000) | Medio |
| Curación | Todos los modelos | 1–9 por categoría | Alto |
| Especiales | Mezclados | Solo con “Ver todos” | Medio |
| Local | `cognitia_llm_*` como externo | `cognitia_llm_*` local | Medio |

**Mitigación**:
- Cache de precios con pricepertoken (MCP)
- Curación por categoría con toggle “Ver todos”
- Etiquetas Local (Cognitia/Ollama) sin costo API

---

### 6. Disponibilidad y SLA

**Gap**: Modelo de disponibilidad diferente

| Aspecto | Railway | HF ZeroGPU |
|---------|---------|------------|
| Uptime | 99%+ | Variable (compartido) |
| Cold start | 30-60s | 10-30s |
| Cuota | Ilimitada | Diaria (gratis) |
| Prioridad | Igual para todos | PRO tiene prioridad |

**Mitigación**:
- Mantener OpenAI como fallback
- Implementar retry logic
- Considerar PRO para prioridad

---

## Análisis de Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cuota ZeroGPU agotada | Media | Alto | PRO o fallback OpenAI |
| Latencia red aumentada | Baja | Bajo | CDN, retry logic |
| HF Space caído | Baja | Alto | Fallback, health checks |
| Modelo no compatible | Baja | Medio | Testing previo |
| Token comprometido | Baja | Alto | Rotación, Space privado |

---

## Dependencias Técnicas

### Código a Modificar

```python
# backend/open_webui/routers/ollama.py
# Líneas a actualizar:

# 1. Variable de entorno
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
# Nuevo valor: "https://[usuario]-cognitia-ollama.hf.space"

# 2. Headers (si Space privado)
HF_TOKEN = os.getenv("HF_TOKEN", "")
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
```

### Variables de Entorno

| Variable | Valor Actual | Valor Nuevo |
|----------|--------------|-------------|
| `OLLAMA_BASE_URL` | `http://ollama.railway.internal:11434` | `https://user-cognitia-ollama.hf.space` |
| `HF_TOKEN` | (nuevo) | `hf_xxxx` (si Space privado) |

---

## Checklist de Migración

### Pre-migración
- [ ] Crear cuenta Hugging Face (si no existe)
- [ ] Evaluar si necesita PRO ($9/mes)
- [ ] Documentar modelos actuales en uso
- [ ] Backup de configuración Railway

### Migración
- [ ] Crear HF Space con Dockerfile
- [ ] Configurar ZeroGPU
- [ ] Descargar modelos recomendados
- [ ] Probar endpoints desde local
- [ ] Actualizar OLLAMA_BASE_URL en Railway
- [ ] Probar conexión Cognitia → HF
- [ ] Validar funcionamiento end-to-end

### Post-migración
- [ ] Monitorear uso de cuota ZeroGPU
- [ ] Evaluar necesidad de PRO
- [ ] Documentar nuevos endpoints
- [ ] Eliminar servicio Ollama de Railway (opcional)

---

## Recomendación Final

**Tier recomendada**: Comenzar con **Free + ZeroGPU**

**Justificación**:
1. ZeroGPU ofrece GPU H200 gratis (la más potente disponible)
2. Cuota diaria suficiente para uso moderado
3. Si se agota, upgrade a PRO ($9/mes) es económico
4. Fallback a OpenAI siempre disponible

**Modelos iniciales recomendados**:
1. **Qwen2.5-7B-Instruct** - Mejor balance calidad/eficiencia
2. **phi-3-mini** - Respuestas rápidas, bajo consumo cuota
3. **CodeLlama-7B** - Para tareas de programación

---

## Fuentes

- [Hugging Face Pricing](https://huggingface.co/pricing)
- [ZeroGPU Documentation](https://huggingface.co/docs/hub/en/spaces-zerogpu)
- [Spaces GPU Guide](https://huggingface.co/docs/hub/en/spaces-gpus)
