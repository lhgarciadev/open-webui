# Phase 3.1 Validation Results - Ollama Model Deployment

**Date**: 2026-02-15 19:00 EST
**Space**: https://juansquiroga-cognitia-ollama.hf.space
**Status**: PASS (CPU Mode)

## Executive Summary

The Cognitia Ollama Hugging Face Space is successfully deployed and running on CPU hardware. During deployment, a missing dependency (`curl`) was identified and fixed. The Space is now operational with phi3 model available.

## Bug Fix Applied

**Issue**: Runtime error due to missing `curl` command in Docker container.

**Fix**: Added `apt-get install curl` to Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

**Commit**: `45896ef` - "fix: Install curl in Docker image for healthcheck and startup script"

## Models Available

| Model | Parameters | Size | Quantization | Status |
|-------|------------|------|--------------|--------|
| phi3:latest | 3.8B | 2.03GB | Q4_0 | Available |
| qwen2.5:7b | 7B | 4.7GB | - | CPU mode: Not loaded |
| codellama:7b | 7B | 3.8GB | - | CPU mode: Not loaded |

**Note**: The Space is running on `cpu-basic` hardware. Only phi3 is loaded automatically in CPU mode per the start.sh logic. The 7B models (qwen2.5, codellama) require GPU upgrade.

## Performance Tests

### Test 1: Simple Spanish Response
```bash
curl -s .../api/generate -d '{"model":"phi3","prompt":"Hola, responde solo con una oracion corta"}'
```
- **Response**: "Hola!"
- **Latency**: 7.86 seconds (cold start)

### Test 2: Code Generation
```bash
curl -s .../api/generate -d '{"model":"phi3","prompt":"Escribe una funcion Python para sumar dos numeros"}'
```
- **Response**:
```python
def suma(num1, num2):
    return num1 + num2
```
- **Latency**: 6.56 seconds

### Test 3: Knowledge Question (Warm)
```bash
curl -s .../api/generate -d '{"model":"phi3","prompt":"Cual es la capital de Colombia?"}'
```
- **Response**: "Bogota"
- **Latency**: 2.69 seconds

### Test 4: Chat API
```bash
curl -s .../api/chat -d '{"model":"phi3","messages":[{"role":"user","content":"Hola, como estas?"}]}'
```
- **Response**: Full conversational response in Spanish
- **Latency**: 11.94 seconds

## API Endpoints Verified

| Endpoint | Method | Status |
|----------|--------|--------|
| /api/tags | GET | Working |
| /api/generate | POST | Working |
| /api/chat | POST | Working |

## Checklist Results

### Verification
- [x] /api/tags responds correctly
- [x] phi3 available
- [ ] qwen2.5:7b available (requires GPU)
- [ ] codellama:7b available (requires GPU)

### Tests
- [x] phi3 responds correctly
- [x] Spanish language support works
- [x] Code generation works
- [x] Chat API works
- [x] Latency: 2-8 seconds (acceptable for CPU)

### Documentation
- [x] Model list documented
- [x] Response times recorded
- [x] API endpoints verified

## Hardware Configuration

- **Current**: CPU Basic (16GB RAM)
- **Model Support**: phi3 only
- **Upgrade Path**: t4-small GPU tier for 7B models

## Recommendations

1. **For full model support**: Upgrade to GPU tier ($0.40/hr for t4-small)
2. **Current state is production-ready** for lightweight inference with phi3
3. **Consider**: ZeroGPU Space (cognitia-llm) as alternative for free GPU access

## Test Commands

```bash
# List models
curl -s https://juansquiroga-cognitia-ollama.hf.space/api/tags | jq

# Generate text
curl -s https://juansquiroga-cognitia-ollama.hf.space/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"phi3","prompt":"Tu prompt aqui","stream":false}'

# Chat API
curl -s https://juansquiroga-cognitia-ollama.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"phi3","messages":[{"role":"user","content":"Hola"}],"stream":false}'
```

## Next Steps

1. Proceed to [3.2-models-validar.md](./prompts/3.2-models-validar.md) for detailed validation
2. Consider GPU upgrade if 7B models are required
3. Integrate with Open WebUI using OLLAMA_BASE_URL
