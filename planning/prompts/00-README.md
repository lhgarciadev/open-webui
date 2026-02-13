# Prompts Agenticos - Indice

> **Total**: 14 prompts (7 etapas x 2)
> **Path Legal**: A (< 50 usuarios) - CONFIRMADO
> **Marca**: Cognitia
> **Estado**: LISTO PARA EJECUCION

## Flujo de Ejecucion

```
Para cada etapa:
  1. Ejecutar prompt de EJECUCION (X.1)
  2. Revisar cambios generados
  3. Ejecutar prompt de VALIDACION (X.2)
  4. Si PASS → siguiente etapa
  5. Si FAIL → corregir y repetir
```

## Indice de Prompts

| Etapa | Ejecucion | Validacion |
|-------|-----------|------------|
| 0. Gate Legal | [0.1](./0.1-legal-ejecutar.md) | [0.2](./0.2-legal-validar.md) |
| 1. Assets | [1.1](./1.1-assets-ejecutar.md) | [1.2](./1.2-assets-validar.md) |
| 2. Config | [2.1](./2.1-config-ejecutar.md) | [2.2](./2.2-config-validar.md) |
| 3. Estilos | [3.1](./3.1-estilos-ejecutar.md) | [3.2](./3.2-estilos-validar.md) |
| 4. Componentes | [4.1](./4.1-componentes-ejecutar.md) | [4.2](./4.2-componentes-validar.md) |
| 5. Docker | [5.1](./5.1-docker-ejecutar.md) | [5.2](./5.2-docker-validar.md) |
| 6. MCP | [6.1](./6.1-mcp-ejecutar.md) | [6.2](./6.2-mcp-validar.md) |
| 7. QA Final | [7.1](./7.1-qa-ejecutar.md) | [7.2](./7.2-qa-validar.md) |

## Notas

- **Etapa 0**: Obligatoria antes de cualquier cambio
- **Etapa 6**: Opcional (nice to have)
- **Etapa 7**: Obligatoria antes de release

## Variables Configuradas

| Variable | Valor |
|----------|-------|
| `BRAND_NAME` | Cognitia |
| `BRAND_SHORT` | Cognitia |
| `brand` | cognitia |
| `BRAND_COLOR` | #3b82f6 |
