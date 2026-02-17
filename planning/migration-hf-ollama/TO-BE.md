# TO-BE: Estado Objetivo con Hugging Face

## Resumen

Migrar el servicio Ollama a Hugging Face Spaces con **ZeroGPU** (GPU H200 gratuita), manteniendo Cognitia en Railway como frontend y conectando ambos servicios vía API HTTPS.

---

## Opción Recomendada: ZeroGPU (GRATIS)

Hugging Face ofrece **ZeroGPU**, una infraestructura compartida que proporciona acceso gratuito a GPUs NVIDIA H200 (~70GB VRAM) bajo demanda.

| Característica | Free Tier         | PRO ($9/mes)     |
| -------------- | ----------------- | ---------------- |
| GPU            | H200 (compartida) | H200 (prioridad) |
| VRAM           | ~70GB             | ~70GB            |
| Cuota diaria   | Base              | **8x más**       |
| Prioridad cola | Normal            | **Alta**         |
| Costo          | **$0**            | **$9/mes**       |

**Modelos Recomendados para Free Tier**:
| Modelo | Parámetros | Calidad | Uso |
|--------|------------|---------|-----|
| **Qwen2.5-7B** | 7B | ⭐⭐⭐⭐⭐ | Chat + Coding |
| **phi3** | 3.8B | ⭐⭐⭐⭐ | Respuestas rápidas |
| **CodeLlama-7B** | 7B | ⭐⭐⭐⭐ | Programación |
| **Llama3.2-3B** | 3B | ⭐⭐⭐⭐ | Chat ligero |
| **Gemma2-9B** | 9B | ⭐⭐⭐⭐⭐ | Razonamiento |

> **Recomendación**: Comenzar con Free Tier. Si la cuota se agota frecuentemente, upgrade a PRO por $9/mes.

---

## Arquitectura Objetivo

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAILWAY CLOUD                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────┐      ┌────────────────────────┐        │
│  │   COGNITIA APP         │      │   POSTGRESQL           │        │
│  │   ───────────────      │      │   ──────────────       │        │
│  │   Dockerfile.railway   │      │   Railway Postgres     │        │
│  │   Puerto: 8080         │      │   Datos persistentes   │        │
│  └────────────────────────┘      └────────────────────────┘        │
│            │                                                        │
│            │ HTTPS (API pública o Inference Endpoint)               │
│            │                                                        │
└────────────┼────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      HUGGING FACE                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │   OLLAMA SPACE + ZeroGPU                                    │    │
│  │   ───────────────────────────────────────────────────────   │    │
│  │   Docker SDK                                                │    │
│  │   GPU: H200 (~70GB VRAM) - GRATIS con cuota diaria         │    │
│  │   Modelos: qwen2.5:7b, phi3, codellama:7b, gemma2:9b       │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    HUGGING FACE HUB                         │    │
│  │   Modelos: phi3, llama3, mistral, codellama, qwen2.5       │    │
│  │   Acceso directo desde Space o Endpoint                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Opciones de Implementación

### Opción A: Hugging Face Space con Docker (Recomendada)

**Ventajas**:

- Control total sobre el contenedor
- Compatible con Ollama existente
- GPU dedicada o compartida
- Costo predecible

**Implementación**:

```dockerfile
# Dockerfile para HF Space
FROM ollama/ollama:latest

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=24h
ENV OLLAMA_NUM_PARALLEL=4

# Modelo pre-cargado
RUN ollama pull phi3
RUN ollama pull llama3.2:3b

EXPOSE 7860
CMD ["ollama", "serve"]
```

**Hardware HF Spaces**:
| Tier | GPU | RAM | Costo |
|------|-----|-----|-------|
| CPU Basic | - | 2GB | Gratis |
| CPU Upgrade | - | 8GB | $0.03/hr |
| T4 Small | T4 (16GB) | 16GB | $0.60/hr |
| T4 Medium | T4 (16GB) | 32GB | $0.90/hr |
| A10G Small | A10G (24GB) | 24GB | $1.50/hr |
| A10G Large | A10G (24GB) | 72GB | $3.50/hr |
| A100 Large | A100 (80GB) | 142GB | $8.00/hr |

---

### Opción B: Inference Endpoints (Serverless)

**Ventajas**:

- Sin gestión de infraestructura
- Auto-scaling automático
- Pay-per-request
- Modelos pre-optimizados

**Implementación**:

```python
# Usar API de HF Inference
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="microsoft/phi-3-mini-4k-instruct",
    token="hf_..."
)

response = client.text_generation(
    prompt="Hello, how are you?",
    max_new_tokens=100
)
```

**Pricing Inference Endpoints**:
| Modelo | GPU | $/1K tokens |
|--------|-----|-------------|
| phi-3-mini | T4 | ~$0.0002 |
| llama-3-8b | A10G | ~$0.0005 |
| llama-3-70b | A100 | ~$0.002 |

---

## Arquitectura Detallada (Opción A)

### 1. Hugging Face Space - Ollama

**Configuración Space** (`README.md` en HF):

```yaml
---
title: Cognitia Ollama
emoji: 🦙
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 11434
suggested_hardware: t4-small
---
```

**Dockerfile**:

```dockerfile
FROM ollama/ollama:latest

# Configuración para GPU
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=24h
ENV OLLAMA_NUM_PARALLEL=4
ENV OLLAMA_FLASH_ATTENTION=1
ENV CUDA_VISIBLE_DEVICES=0

# Pre-descargar modelos populares
COPY download_models.sh /download_models.sh
RUN chmod +x /download_models.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Exponer puerto estándar de Ollama
EXPOSE 11434

# Script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
```

**Script de Inicio**:

```bash
#!/bin/bash
set -e

# Iniciar Ollama
ollama serve &

# Esperar inicio
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done

# Descargar modelos si no existen
if ! ollama list | grep -q "phi3"; then
    ollama pull phi3
fi

if ! ollama list | grep -q "llama3.2"; then
    ollama pull llama3.2:3b
fi

echo "Ollama ready with GPU acceleration"
wait
```

---

### 2. Conexión Cognitia → HF Space

**Variables de Entorno** (Railway):

```bash
# Cambiar de Railway interno a HF público
OLLAMA_BASE_URL=https://[usuario]-cognitia-ollama.hf.space

# Autenticación HF (opcional para Spaces privados)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

### 2.1 UX de Costos y Curación en Cognitia

**Objetivo**: Mejorar la selección de modelos con costos educativos en COP y curación por categoría.

**Capacidades**:

- Costos estimados en COP (1 USD = 4000 COP) visibles en el selector.
- Curación por categoría (1–9 modelos) por defecto.
- “Ver todos” expone modelos especiales (audio/realtime/imagen/search).
- Modelos `cognitia_llm_*` tratados como locales (sin costo API).

**Variables de Entorno**:

```bash
PRICEPERTOKEN_MCP_URL=https://api.pricepertoken.com/mcp/mcp
PRICING_REFRESH_INTERVAL_SECONDS=43200   # 12h
PRICING_CACHE_TTL_SECONDS=86400          # 24h
```

**Endpoints**:

- `GET /api/v1/pricing/models`
- `POST /api/v1/pricing/refresh`
- `GET /api/v1/pricing/debug/sample` (solo admin, temporal)

**Modificación Backend** (`backend/open_webui/routers/ollama.py`):

```python
# Agregar soporte para autenticación HF
import os

HF_TOKEN = os.getenv("HF_TOKEN", "")

async def get_ollama_headers():
    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    return headers
```

---

### 3. Modelos Disponibles

| Modelo        | Parámetros | VRAM Requerida | Tier HF  |
| ------------- | ---------- | -------------- | -------- |
| phi3          | 3.8B       | ~4GB           | CPU o T4 |
| llama3.2:3b   | 3B         | ~3GB           | CPU o T4 |
| llama3.1:8b   | 8B         | ~8GB           | T4       |
| mistral:7b    | 7B         | ~6GB           | T4       |
| codellama:13b | 13B        | ~12GB          | T4       |
| llama3.1:70b  | 70B        | ~45GB          | A100     |

---

## Configuración de Seguridad

### Opción 1: Space Privado

```yaml
# En HF Space settings
private: true
```

**Acceso**:

```bash
# Requiere HF_TOKEN en Cognitia
curl -H "Authorization: Bearer hf_xxx" \
     https://user-space.hf.space/api/tags
```

### Opción 2: Space con Token Personalizado

```python
# En el Space, validar token personalizado
import os
from fastapi import Header, HTTPException

API_TOKEN = os.getenv("COGNITIA_API_TOKEN")

async def verify_token(authorization: str = Header(None)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401)
```

---

## Monitoreo y Observabilidad

### Métricas HF Spaces

- **Dashboard**: Uso de GPU, RAM, requests
- **Logs**: Streaming en tiempo real
- **Alertas**: Configurables por email

### Integración con Cognitia

```python
# Agregar logging de latencia
import time
import logging

async def call_ollama(prompt):
    start = time.time()
    response = await ollama_client.generate(prompt)
    latency = time.time() - start
    logging.info(f"Ollama latency: {latency:.2f}s, GPU: HF Space")
    return response
```

---

## Estructura de Archivos HF Space

```
cognitia-ollama/
├── README.md           # Metadata del Space
├── Dockerfile          # Contenedor Ollama
├── start.sh            # Script de inicio
├── download_models.sh  # Pre-descarga modelos
└── .env.example        # Variables de ejemplo
```

---

## Estimación de Costos

### Escenario: Uso Moderado (8 hrs/día)

| Componente         | Tier     | Costo Mensual               |
| ------------------ | -------- | --------------------------- |
| HF Space T4        | T4 Small | $0.60 × 8h × 30d = **$144** |
| Railway Cognitia   | Hobby    | **$5**                      |
| Railway PostgreSQL | Addon    | **$2**                      |
| **Total**          |          | **~$151/mes**               |

### Escenario: Uso Bajo (2 hrs/día)

| Componente         | Tier     | Costo Mensual              |
| ------------------ | -------- | -------------------------- |
| HF Space T4        | T4 Small | $0.60 × 2h × 30d = **$36** |
| Railway Cognitia   | Hobby    | **$5**                     |
| Railway PostgreSQL | Addon    | **$2**                     |
| **Total**          |          | **~$43/mes**               |

### Escenario: Sleep Mode (on-demand)

| Componente       | Tier              | Costo Mensual   |
| ---------------- | ----------------- | --------------- |
| HF Space T4      | Sleep cuando idle | ~$10-20         |
| Railway Cognitia | Hobby             | **$5**          |
| **Total**        |                   | **~$15-25/mes** |

---

## Beneficios del Estado Objetivo

### 1. Performance

| Métrica            | Railway (CPU) | HF (GPU T4) | Mejora    |
| ------------------ | ------------- | ----------- | --------- |
| Latencia           | 2-5s          | 0.3-0.8s    | **5-10x** |
| Tokens/s           | 5-10          | 50-100      | **10x**   |
| Modelos soportados | <4B           | <15B        | **3-4x**  |

### 2. Escalabilidad

- Upgrade a A10G/A100 sin cambios de código
- Múltiples réplicas (HF Spaces Pro)
- Auto-scaling con Inference Endpoints

### 3. Flexibilidad

- Sleep mode para ahorro de costos
- GPU on-demand vs dedicada
- Cambio de modelos en caliente

### 4. Ecosistema

- Acceso directo a HF Hub
- Modelos optimizados (GGUF, AWQ, GPTQ)
- Comunidad y soporte

---

## Diagrama de Flujo de Solicitudes (TO-BE)

```
Usuario
   │
   ▼
┌──────────────────┐
│  Cognitia App    │
│  (Railway)       │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────────────────┐
│OpenAI │ │  Ollama Space     │
│ API   │ │  (Hugging Face)   │
│(cloud)│ │  ┌─────────────┐  │
└───────┘ │  │ GPU T4/A10G │  │
          │  └─────────────┘  │
          │        │          │
          │  ┌─────┴─────┐    │
          │  ▼           ▼    │
          │ phi3    llama3.1  │
          │ (fast)   (8B)     │
          └───────────────────┘
```

---

## Próximos Pasos

Ver [GAP-ANALYSIS.md](./GAP-ANALYSIS.md) para el análisis de brechas y [AGENTIC-PLAN.md](./AGENTIC-PLAN.md) para el plan de migración detallado.
