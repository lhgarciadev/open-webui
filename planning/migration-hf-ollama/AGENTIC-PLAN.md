# Plan Agéntico: Migración Ollama a Hugging Face

## Definición del Agente de Migración

**Objetivo**: Migrar el servicio Ollama desde Railway a Hugging Face Spaces con ZeroGPU, habilitando inferencia GPU gratuita para modelos LLM.

**Entradas**:
- Configuración Docker actual (`ollama-service/`)
- Variables de entorno Railway
- Modelos actuales (phi3)

**Salidas**:
- HF Space con Ollama funcionando
- Modelos opensource descargados
- Cognitia conectado a HF Space
- Documentación actualizada

---

## Fase 0: Preparación y Validación

### 0.1 Verificar Prerrequisitos

**Ejecutar**:
```bash
# Verificar cuenta HF
# Ir a https://huggingface.co/settings/tokens
# Crear token con permisos: write

# Verificar HF CLI instalado
pip install -U huggingface_hub

# Login
huggingface-cli login
# Ingresar token cuando se solicite
```

**Validar**:
```bash
# Confirmar login exitoso
huggingface-cli whoami
# Debe mostrar tu usuario
```

### 0.2 Documentar Estado Actual

**Ejecutar**:
```bash
# Desde el directorio del proyecto
cd /Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui

# Listar configuración Ollama actual
cat ollama-service/Dockerfile
cat ollama-service/start.sh
cat ollama-service/railway.json

# Capturar variables de Railway (desde dashboard)
# OLLAMA_BASE_URL=http://ollama.railway.internal:11434
# Otros relevantes...
```

**Validar**:
- [ ] Dockerfile documentado
- [ ] Variables de entorno listadas
- [ ] Modelos actuales identificados (phi3)

---

## Fase 1: Crear Hugging Face Space

### 1.1 Crear Repositorio Space

**Ejecutar** (opción CLI):
```bash
# Crear Space con Docker SDK
huggingface-cli repo create cognitia-ollama \
  --type space \
  --space-sdk docker

# Clonar repositorio
git clone https://huggingface.co/spaces/[TU_USUARIO]/cognitia-ollama
cd cognitia-ollama
```

**Ejecutar** (opción Web):
1. Ir a https://huggingface.co/new-space
2. Nombre: `cognitia-ollama`
3. SDK: `Docker`
4. Hardware: `CPU basic` (ZeroGPU se configura después)
5. Visibilidad: `Public` (o Private si prefieres)
6. Crear Space

### 1.2 Crear Dockerfile para HF

**Crear archivo** `Dockerfile`:
```dockerfile
FROM ollama/ollama:latest

# Configuración para ZeroGPU
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=24h
ENV OLLAMA_NUM_PARALLEL=4
ENV OLLAMA_FLASH_ATTENTION=1

# Puerto estándar HF Spaces
ENV PORT=7860
ENV OLLAMA_PORT=7860

# Crear directorio de trabajo
WORKDIR /app

# Copiar scripts
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:7860/api/tags || exit 1

# Exponer puerto
EXPOSE 7860

# Iniciar
CMD ["/app/start.sh"]
```

### 1.3 Crear Script de Inicio

**Crear archivo** `start.sh`:
```bash
#!/bin/bash
set -e

echo "========================================="
echo "  Cognitia Ollama - Hugging Face Space"
echo "========================================="

# Configurar puerto para HF Spaces
export OLLAMA_HOST=0.0.0.0:7860

echo "[1/4] Iniciando servidor Ollama..."
ollama serve &
OLLAMA_PID=$!

echo "[2/4] Esperando que Ollama esté listo..."
MAX_ATTEMPTS=60
ATTEMPT=0
until curl -s http://localhost:7860/api/tags > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "ERROR: Ollama no inició después de ${MAX_ATTEMPTS} intentos"
        exit 1
    fi
    echo "  Esperando... intento $ATTEMPT/$MAX_ATTEMPTS"
    sleep 2
done
echo "  Ollama está listo!"

echo "[3/4] Descargando modelos recomendados..."

# Modelo 1: Qwen2.5 7B - Mejor balance calidad/eficiencia
if ! ollama list | grep -q "qwen2.5:7b"; then
    echo "  Descargando qwen2.5:7b (~4.7GB)..."
    ollama pull qwen2.5:7b
else
    echo "  qwen2.5:7b ya está disponible"
fi

# Modelo 2: Phi-3 Mini - Rápido, bajo consumo
if ! ollama list | grep -q "phi3"; then
    echo "  Descargando phi3 (~2.3GB)..."
    ollama pull phi3
else
    echo "  phi3 ya está disponible"
fi

# Modelo 3: CodeLlama 7B - Para programación
if ! ollama list | grep -q "codellama:7b"; then
    echo "  Descargando codellama:7b (~3.8GB)..."
    ollama pull codellama:7b
else
    echo "  codellama:7b ya está disponible"
fi

echo "[4/4] Modelos disponibles:"
ollama list

echo ""
echo "========================================="
echo "  Ollama listo en puerto 7860"
echo "  Modelos: qwen2.5:7b, phi3, codellama:7b"
echo "========================================="

# Mantener proceso activo
wait $OLLAMA_PID
```

### 1.4 Crear README.md (Metadata HF)

**Crear archivo** `README.md`:
```yaml
---
title: Cognitia Ollama
emoji: 🦙
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
suggested_hardware: zero-a10g
pinned: false
license: mit
---

# Cognitia Ollama Service

Servicio Ollama con modelos LLM opensource para Cognitia.

## Modelos Disponibles

| Modelo | Parámetros | Uso |
|--------|------------|-----|
| qwen2.5:7b | 7B | Chat general, coding |
| phi3 | 3.8B | Respuestas rápidas |
| codellama:7b | 7B | Programación |

## API

```bash
# Listar modelos
curl https://[usuario]-cognitia-ollama.hf.space/api/tags

# Generar respuesta
curl https://[usuario]-cognitia-ollama.hf.space/api/generate \
  -d '{"model": "qwen2.5:7b", "prompt": "Hola, cómo estás?"}'
```

## Hardware

Este Space usa ZeroGPU para inferencia acelerada por GPU.
```

### 1.5 Push al Space

**Ejecutar**:
```bash
cd cognitia-ollama

# Agregar archivos
git add Dockerfile start.sh README.md

# Commit
git commit -m "feat: Initial Ollama setup with ZeroGPU support"

# Push
git push origin main
```

**Validar**:
1. Ir a `https://huggingface.co/spaces/[TU_USUARIO]/cognitia-ollama`
2. Verificar que el build inicie
3. Esperar a que el Space esté "Running"

---

## Fase 2: Configurar ZeroGPU

### 2.1 Habilitar ZeroGPU

**Ejecutar** (desde HF Web):
1. Ir a Settings del Space
2. En "Space Hardware", seleccionar `ZeroGPU`
3. Guardar cambios
4. El Space se reiniciará automáticamente

**Nota**: ZeroGPU es gratuito pero tiene cuota diaria. Para 8x más cuota, upgrade a PRO ($9/mes).

### 2.2 Verificar Hardware

**Ejecutar**:
```bash
# Verificar que el Space tiene GPU
curl https://[usuario]-cognitia-ollama.hf.space/api/tags

# Respuesta esperada:
# {"models":[{"name":"qwen2.5:7b",...},{"name":"phi3",...}]}
```

---

## Fase 3: Probar Conexión

### 3.1 Test Local

**Ejecutar**:
```bash
# Test desde terminal local
export HF_SPACE_URL="https://[usuario]-cognitia-ollama.hf.space"

# Listar modelos
curl $HF_SPACE_URL/api/tags | jq

# Generar respuesta simple
curl $HF_SPACE_URL/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3",
    "prompt": "¿Cuál es la capital de Colombia?",
    "stream": false
  }' | jq

# Test con modelo más potente
curl $HF_SPACE_URL/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b",
    "prompt": "Escribe una función Python que calcule fibonacci",
    "stream": false
  }' | jq
```

### 3.2 Medir Latencia

**Ejecutar**:
```bash
# Medir tiempo de respuesta
time curl -s $HF_SPACE_URL/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "phi3", "prompt": "Hola", "stream": false}' > /dev/null

# Comparar con Railway (si aún está activo)
time curl -s http://ollama.railway.internal:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "phi3", "prompt": "Hola", "stream": false}' > /dev/null
```

**Validar**:
- [ ] HF responde en <2s (vs 3-5s Railway)
- [ ] Modelos listados correctamente
- [ ] Respuestas coherentes

---

## Fase 4: Conectar Cognitia

### 4.1 Actualizar Variables Railway

**Ejecutar** (desde Railway Dashboard):
1. Ir al servicio `cognitia`
2. Variables → Editar
3. Actualizar:
   ```
   OLLAMA_BASE_URL=https://[usuario]-cognitia-ollama.hf.space
   ```
4. Guardar y redesplegar

**O vía CLI**:
```bash
# Si tienes Railway CLI configurado
railway variables set OLLAMA_BASE_URL="https://[usuario]-cognitia-ollama.hf.space"
railway up
```

### 4.2 Modificar Backend (si Space es privado)

**Solo si el Space es privado**, modificar `backend/open_webui/routers/ollama.py`:

```python
# Agregar soporte para HF Token
import os

HF_TOKEN = os.getenv("HF_TOKEN", "")

# En las funciones que hacen requests a Ollama, agregar header:
headers = {"Content-Type": "application/json"}
if HF_TOKEN:
    headers["Authorization"] = f"Bearer {HF_TOKEN}"
```

### 4.3 Validar Conexión End-to-End

**Ejecutar**:
1. Ir a `https://cognitia-production.up.railway.app`
2. Iniciar sesión
3. Crear nuevo chat
4. Seleccionar modelo `qwen2.5:7b` o `phi3`
5. Enviar mensaje de prueba
6. Verificar respuesta

**Validar**:
- [ ] Modelos aparecen en selector
- [ ] Respuestas se generan correctamente
- [ ] Latencia mejorada vs Railway CPU

---

## Fase 5: Optimización

### 5.1 Agregar Más Modelos (Opcional)

**Modificar** `start.sh` para agregar modelos adicionales:

```bash
# Modelos adicionales recomendados

# Gemma 2 9B - Razonamiento avanzado
if ! ollama list | grep -q "gemma2:9b"; then
    echo "  Descargando gemma2:9b (~5.4GB)..."
    ollama pull gemma2:9b
fi

# Llama 3.2 3B - Ultra rápido
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "  Descargando llama3.2:3b (~2GB)..."
    ollama pull llama3.2:3b
fi

# Mistral 7B - Popular y versátil
if ! ollama list | grep -q "mistral:7b"; then
    echo "  Descargando mistral:7b (~4.1GB)..."
    ollama pull mistral:7b
fi
```

### 5.2 Configurar Auto-Sleep

HF Spaces entran en sleep después de inactividad. Para ZeroGPU esto es normal y ahorra cuota.

**Opciones**:
1. **Aceptar sleep** (recomendado): Cold start ~30s, ahorra cuota
2. **Keep alive** (PRO): Requiere upgrade, más cuota

### 5.3 Monitorear Uso

**Verificar cuota**:
1. Ir a https://huggingface.co/settings/billing
2. Ver "ZeroGPU Usage"
3. Si se agota frecuentemente, considerar PRO ($9/mes)

### 5.4 UX de Costos y Curación en Cognitia

**Objetivo**: Mostrar costos estimados en COP y reducir ruido con curación de modelos.

**Ejecutar**:
1. Configurar variables de entorno:
   - `PRICEPERTOKEN_MCP_URL=https://api.pricepertoken.com/mcp/mcp`
   - `PRICING_REFRESH_INTERVAL_SECONDS=43200`
   - `PRICING_CACHE_TTL_SECONDS=86400`
2. Aplicar migraciones del backend.
3. Verificar endpoint admin:
   - `GET /api/v1/pricing/debug/sample?limit=1`
4. Activar refresh on-demand:
   - `POST /api/v1/pricing/refresh` con IDs de modelos visibles.

**Validar**:
- [ ] Nota educativa de precios visible (COP)
- [ ] Curación activa por defecto
- [ ] “Ver todos” muestra categoría Especiales
- [ ] `cognitia_llm_*` aparece como Local (sin costo API)

---

## Fase 6: Cleanup y Documentación

### 6.1 Desactivar Ollama en Railway (Opcional)

**Ejecutar** (solo después de validar HF funciona):
```bash
# Opción 1: Pausar servicio (reversible)
# En Railway Dashboard: Ollama Service → Settings → Pause

# Opción 2: Eliminar servicio (irreversible)
# En Railway Dashboard: Ollama Service → Settings → Delete
```

### 6.2 Actualizar Documentación

**Actualizar** `RAILWAY_DEPLOY.md`:
```markdown
## Servicios

### Cognitia App (Railway)
- URL: https://cognitia-production.up.railway.app
- Dockerfile: Dockerfile.railway

### Ollama Service (Hugging Face)
- URL: https://[usuario]-cognitia-ollama.hf.space
- Hardware: ZeroGPU (H200)
- Modelos: qwen2.5:7b, phi3, codellama:7b
```

### 6.3 Commit Cambios

```bash
git add .
git commit -m "feat: Migrate Ollama to Hugging Face Spaces with ZeroGPU"
git push
```

---

## Checklist Final

### Migración Completada
- [ ] HF Space creado y funcionando
- [ ] ZeroGPU habilitado
- [ ] Modelos descargados (qwen2.5:7b, phi3, codellama:7b)
- [ ] Cognitia conectado a HF Space
- [ ] Tests end-to-end exitosos
- [ ] Documentación actualizada
- [ ] Ollama Railway desactivado (opcional)

### Métricas de Éxito
- [ ] Latencia: <1s (vs 3-5s anterior)
- [ ] Modelos: 3+ disponibles (vs 1 anterior)
- [ ] Costo: $0-9/mes (vs $5-10 anterior)
- [ ] GPU: Disponible (vs ninguna anterior)

---

## Rollback Plan

Si algo falla, revertir a Railway:

```bash
# En Railway Dashboard:
# 1. Reactivar Ollama Service (si fue pausado)
# 2. Actualizar variable:
railway variables set OLLAMA_BASE_URL="http://ollama.railway.internal:11434"
railway up
```

---

## Modelos Recomendados - Resumen

### Tier Gratuito (ZeroGPU Free)

| Modelo | Tamaño | Mejor Para | Cuota/Request |
|--------|--------|------------|---------------|
| **phi3** | 2.3GB | Respuestas rápidas | Baja |
| **llama3.2:3b** | 2GB | Chat ligero | Baja |
| **qwen2.5:7b** | 4.7GB | Balance calidad | Media |
| **codellama:7b** | 3.8GB | Programación | Media |

### Tier PRO ($9/mes)

Con PRO tienes 8x más cuota, permitiendo:

| Modelo | Tamaño | Mejor Para |
|--------|--------|------------|
| **gemma2:9b** | 5.4GB | Razonamiento |
| **mistral:7b** | 4.1GB | Versatilidad |
| **llama3.1:70b** | 40GB | Máxima calidad |
| **qwen2.5:72b** | 41GB | Coding avanzado |

---

## Soporte

- **HF Docs**: https://huggingface.co/docs/hub/spaces
- **ZeroGPU**: https://huggingface.co/docs/hub/spaces-zerogpu
- **Ollama**: https://ollama.ai/library

---

*Plan generado: 2026-02-15*
*Versión: 1.0*
