# AS-IS: Estado Actual de Infraestructura

## Resumen

Cognitia actualmente opera en Railway con una arquitectura de microservicios donde Ollama corre como servicio separado usando solo CPU.

---

## Arquitectura Actual

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAILWAY CLOUD                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────┐      ┌────────────────────────┐        │
│  │   COGNITIA APP         │      │   OLLAMA SERVICE       │        │
│  │   ───────────────      │      │   ──────────────       │        │
│  │   Dockerfile.railway   │◀────▶│   ollama/ollama:latest │        │
│  │   Puerto: 8080         │      │   Puerto: 11434        │        │
│  │   ~512MB-1GB RAM       │      │   ~2-4GB RAM           │        │
│  │   CPU-only             │      │   CPU-only             │        │
│  └────────────────────────┘      └────────────────────────┘        │
│            │                              │                         │
│            │          Red Interna Railway                           │
│            │    ollama.railway.internal:11434                       │
│            │                                                        │
│  ┌────────────────────────┐      ┌────────────────────────┐        │
│  │   MCPO SERVICE         │      │   POSTGRESQL           │        │
│  │   (Opcional)           │      │   (Opcional)           │        │
│  │   Puerto: 8000         │      │   Railway Postgres     │        │
│  └────────────────────────┘      └────────────────────────┘        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   USUARIOS   │
                    │   cognitia-  │
                    │   production │
                    │   .up.       │
                    │   railway.app│
                    └──────────────┘
```

---

## Componentes Detallados

### 1. Servicio Cognitia (App Principal)

**Archivo**: `Dockerfile.railway`

```dockerfile
# Características clave
USE_OLLAMA_DOCKER=false    # No incluye Ollama
USE_CUDA_DOCKER=false      # Sin GPU
USE_SLIM_DOCKER=true       # Build ligero
```

**Configuración Railway** (`railway.json`):
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.railway"
  },
  "deploy": {
    "startCommand": "bash start.sh",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

**Variables de Entorno Actuales**:
| Variable | Valor | Descripción |
|----------|-------|-------------|
| `OLLAMA_BASE_URL` | `http://ollama.railway.internal:11434` | URL interna Ollama |
| `OPENAI_API_KEY` | `sk-...` | API OpenAI (fallback) |
| `WEBUI_SECRET_KEY` | `[generado]` | JWT secret |
| `WEBUI_NAME` | `Cognitia` | Nombre de app |
| `BYPASS_MODEL_ACCESS_CONTROL` | `true` | Sin restricciones modelo |

---

### 2. Servicio Ollama

**Ubicación**: `ollama-service/`

**Dockerfile** (`ollama-service/Dockerfile`):
```dockerfile
FROM ollama/ollama:latest

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=24h
ENV OLLAMA_NUM_PARALLEL=2

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 11434

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

CMD ["/start.sh"]
```

**Script de Inicio** (`ollama-service/start.sh`):
```bash
#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve &

# Esperar inicio
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done

# Auto-descarga phi3 si no existe
if ! ollama list | grep -q "phi3"; then
    ollama pull phi3
fi

wait
```

**Configuración Railway** (`ollama-service/railway.json`):
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/api/tags",
    "healthcheckTimeout": 120
  }
}
```

---

### 3. Modelos Disponibles

| Modelo | Parámetros | Tamaño | Estado |
|--------|------------|--------|--------|
| phi3 | 3.8B | ~2.3GB | Desplegado |
| *(OpenAI fallback)* | - | - | Disponible vía API |

**Limitaciones CPU**:
- Latencia: 2-5 segundos por respuesta
- Throughput: ~5-10 tokens/segundo
- Modelos grandes (>7B): No viables

---

## Métricas Actuales

### Costos

| Recurso | Costo Estimado |
|---------|----------------|
| Railway Hobby | $5/mes base |
| Cognitia App | ~$0.50-1.00/mes |
| Ollama Service | ~$2-4/mes (CPU) |
| PostgreSQL | ~$1-2/mes |
| **Total** | **~$5-10/mes** |

### Performance

| Métrica | Valor |
|---------|-------|
| Tiempo respuesta (phi3) | 2-5s |
| Tokens/segundo | 5-10 |
| Uptime | 99%+ |
| Cold start | 30-60s |

### Recursos

| Servicio | RAM | CPU |
|----------|-----|-----|
| Cognitia | 512MB-1GB | 0.5 vCPU |
| Ollama | 2-4GB | 1-2 vCPU |

---

## Networking

### Comunicación Interna

```
Cognitia App ──► ollama.railway.internal:11434 ──► Ollama Service
                        (red privada)
```

### Endpoints Públicos

- **App**: `https://cognitia-production.up.railway.app`
- **Ollama**: No expuesto públicamente (solo interno)

---

## Limitaciones Identificadas

### 1. Sin GPU
- Inferencia lenta (CPU-only)
- Modelos limitados a <4B parámetros
- No viable para modelos de código o multimodales

### 2. Escalabilidad
- Sin auto-scaling para Ollama
- Recursos fijos por servicio
- No hay burst capacity

### 3. Modelos Grandes
- 7B+ parámetros: timeout o OOM
- No soporta Llama 3 70B, GPT-4 class
- Cuantización extrema requerida

### 4. Costos a Escala
- CPU pricing no escala bien
- Sin opción GPU en Railway
- Cada modelo adicional = más RAM

---

## Dependencias Técnicas

### Backend Python
```python
# backend/open_webui/routers/ollama.py
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
```

### Configuración
```python
# backend/open_webui/config.py
OLLAMA_BASE_URLS = [url.strip("/") for url in OLLAMA_BASE_URLS.split(";")]
```

### Health Check
```python
# Verifica conectividad con Ollama
GET /api/tags → lista modelos disponibles
```

---

## UX de Modelos (Estado Actual)

### Selector de Modelos
- No muestra costos estimados por token.
- No hay curación por categoría; lista completa visible.
- Modelos especiales (audio/realtime/imagen/search) se mezclan si existen.
- Modelos `cognitia_llm_*` no se tratan explícitamente como locales.

---

## Diagrama de Flujo de Solicitudes

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
┌───────┐ ┌───────────┐
│OpenAI │ │  Ollama   │
│ API   │ │  Service  │
│(cloud)│ │ (Railway) │
└───────┘ └───────────┘
              │
              ▼
         ┌────────┐
         │  phi3  │
         │ (CPU)  │
         └────────┘
```

---

## Archivos Clave del Estado Actual

| Archivo | Propósito |
|---------|-----------|
| `Dockerfile.railway` | Build slim para Railway |
| `ollama-service/Dockerfile` | Contenedor Ollama |
| `ollama-service/start.sh` | Auto-descarga modelos |
| `ollama-service/railway.json` | Deploy config |
| `railway.json` | Config principal |
| `RAILWAY_DEPLOY.md` | Documentación deploy |

---

## Conclusión

El estado actual funciona correctamente para demostración y uso ligero, pero presenta limitaciones significativas para escalar a modelos más grandes o aumentar el rendimiento de inferencia. La migración a Hugging Face permitirá:

1. Acceso a GPU para inferencia rápida
2. Soporte para modelos de 7B+ parámetros
3. Escalabilidad horizontal
4. Mejor relación costo/rendimiento para uso intensivo
