# Etapa 7: Despliegue de Ollama + Phi3 para Pruebas Locales

## Objetivo

Configurar un entorno de pruebas con Ollama corriendo modelos locales (Phi3) para validar seguridad y funcionamiento sin depender de APIs externas.

---

## Justificacion

### Por que modelos locales?

1. **Seguridad:** Datos sensibles no salen de la red local
2. **Privacidad:** Sin telemetria a terceros
3. **Costo:** $0 por inferencia
4. **Latencia:** Sin dependencia de internet
5. **Testing:** Pruebas sin consumir creditos de API

### Por que Phi3?

- Modelo pequeno pero capaz (3.8B parametros)
- Funciona en hardware modesto (8GB RAM)
- Buen balance rendimiento/recursos
- Licencia permisiva (MIT)
- Soporta tool calling basico

---

## Pre-requisitos

### Hardware Minimo

| Componente | Minimo      | Recomendado |
| ---------- | ----------- | ----------- |
| RAM        | 8 GB        | 16 GB       |
| Disco      | 10 GB libre | 50 GB SSD   |
| CPU        | 4 cores     | 8 cores     |
| GPU        | Opcional    | NVIDIA 8GB+ |

### Software

- macOS 12+, Linux, o Windows 11
- Docker (opcional, para contenedor)
- Open WebUI corriendo localmente

---

## Instalacion de Ollama

### Opcion A: Instalacion Directa (Recomendada para Mac)

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verificar instalacion
ollama --version
```

### Opcion B: Docker

```bash
# Crear directorio para modelos
mkdir -p ~/ollama

# Correr Ollama en Docker
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ~/ollama:/root/.ollama \
  ollama/ollama

# Con GPU NVIDIA
docker run -d \
  --name ollama \
  --gpus all \
  -p 11434:11434 \
  -v ~/ollama:/root/.ollama \
  ollama/ollama
```

### Opcion C: Docker Compose (con Open WebUI)

```yaml
# docker-compose.ollama.yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - '11434:11434'
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    # GPU support (uncomment if NVIDIA GPU available)
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - '3000:8080'
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - open_webui_data:/app/backend/data
    depends_on:
      - ollama
    restart: unless-stopped

volumes:
  ollama_data:
  open_webui_data:
```

```bash
docker-compose -f docker-compose.ollama.yaml up -d
```

---

## Descarga de Modelos

### Phi3 (Recomendado para inicio)

```bash
# Modelo base (3.8B) - ~2.3GB
ollama pull phi3

# Verificar descarga
ollama list
```

### Modelos Alternativos para Testing

```bash
# Llama 3.2 (3B) - Rapido, bueno para chat
ollama pull llama3.2

# Mistral (7B) - Mas capaz, mas lento
ollama pull mistral

# DeepSeek Coder (6.7B) - Especializado en codigo
ollama pull deepseek-coder

# Qwen2.5 (7B) - Bueno para espanol
ollama pull qwen2.5
```

### Tabla de Modelos

| Modelo         | Tamano | RAM Requerida | Uso Principal         |
| -------------- | ------ | ------------- | --------------------- |
| phi3           | 2.3 GB | 4 GB          | General, rapido       |
| llama3.2       | 2.0 GB | 4 GB          | Chat, instrucciones   |
| mistral        | 4.1 GB | 8 GB          | General, razonamiento |
| deepseek-coder | 3.8 GB | 8 GB          | Codigo                |
| qwen2.5        | 4.4 GB | 8 GB          | Multilingue           |

---

## Configuracion en Open WebUI

### Variables de Entorno

```bash
# .env o variables de entorno
OLLAMA_BASE_URL=http://localhost:11434

# Si Ollama esta en otra maquina
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### Verificar Conexion

```bash
# Test directo a Ollama
curl http://localhost:11434/api/tags

# Deberia retornar lista de modelos instalados
```

### En la UI

1. Ir a Settings > Connections
2. Verificar que Ollama URL este configurado
3. Los modelos deberian aparecer en el selector

---

## Pruebas de Seguridad

### Test 1: Datos Sensibles No Salen

```bash
# Monitorear trafico de red mientras usas el chat
# En otra terminal:
sudo tcpdump -i any port 443 or port 80

# Usar el chat con Phi3
# Verificar que NO hay trafico a APIs externas
```

### Test 2: Funcionamiento Offline

```bash
# Desconectar internet
networksetup -setairportpower en0 off  # Mac
# o desconectar cable/WiFi

# Verificar que chat con Phi3 sigue funcionando
```

### Test 3: Aislamiento de Datos

```bash
# Verificar donde se guardan los datos
ls -la ~/ollama/
ls -la ~/.ollama/

# Los modelos y cache estan en tu maquina local
```

### Test 4: Tool Calling (Presentations)

```python
# Test que presentations funciona con modelo local
# En el chat de Open WebUI con Phi3 seleccionado:

"Genera una presentacion de 3 slides sobre seguridad informatica"

# Verificar:
# - La tool se invoca correctamente
# - La presentacion se genera
# - No hay errores de timeout
```

---

## Optimizacion de Rendimiento

### Ajustar Contexto

```bash
# Crear Modelfile con parametros custom
cat > Modelfile << 'EOF'
FROM phi3
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF

# Crear modelo custom
ollama create phi3-custom -f Modelfile
```

### Monitorear Recursos

```bash
# CPU y RAM
htop  # o Activity Monitor en Mac

# GPU (si tienes NVIDIA)
nvidia-smi -l 1

# Uso de Ollama especificamente
ollama ps
```

---

## Troubleshooting

### Problema: Modelo muy lento

```bash
# Verificar que no hay otros procesos pesados
ollama ps

# Reducir contexto
# En Modelfile: PARAMETER num_ctx 2048
```

### Problema: Out of Memory

```bash
# Usar modelo mas pequeno
ollama pull phi3:mini

# O ajustar parametros
# PARAMETER num_gpu 0  # Solo CPU
```

### Problema: Ollama no conecta

```bash
# Verificar servicio
ollama serve  # Si no esta corriendo

# Verificar puerto
lsof -i :11434

# Logs
journalctl -u ollama -f  # Linux
# o ver Console.app en Mac
```

---

## Checklist de Validacion

```
INSTALACION
[ ] Ollama instalado y corriendo
[ ] Phi3 descargado exitosamente
[ ] ollama list muestra el modelo

CONEXION
[ ] Open WebUI detecta Ollama
[ ] Modelos aparecen en selector
[ ] Chat funciona con Phi3

SEGURIDAD
[ ] No hay trafico a APIs externas
[ ] Funciona sin internet
[ ] Datos permanecen locales

RENDIMIENTO
[ ] Respuesta en <10 segundos
[ ] RAM uso estable
[ ] Sin crashes

INTEGRACION
[ ] Presentations tool funciona
[ ] Otros tools funcionan
[ ] Sin errores en logs
```

---

## Siguiente Paso

Una vez validado el entorno local:

1. Ejecutar prompts 4.3 y 4.4 con modelo local
2. Validar que todas las features funcionan offline
3. Documentar diferencias de rendimiento vs APIs externas

---

## Recursos

- [Ollama Docs](https://ollama.com/docs)
- [Phi3 Model Card](https://ollama.com/library/phi3)
- [Open WebUI + Ollama Guide](https://docs.openwebui.com/getting-started/integrations/ollama)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
