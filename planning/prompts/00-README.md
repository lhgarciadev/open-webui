# Prompts - Plan de Correccion (Tools + Presentaciones + Tema)

> Estructura base: 9 etapas, 2 prompts por etapa (ejecutar/validar).
> Extension activa: etapa 2.3/2.4 para persistencia de base de datos (post-etapa 2).
> Extension activa: etapa 4.3/4.4 para saneamiento de errores preexistentes de tipado/check (post-etapa 4).

## Flujo

1. Ejecutar `X.1-...-ejecutar.md`
2. Revisar diff
3. Ejecutar `X.2-...-validar.md`
4. Si PASS: avanzar; si FAIL: corregir y repetir etapa

## Indice

| Etapa                                 | Ejecutar                                 | Validar                                 |
| ------------------------------------- | ---------------------------------------- | --------------------------------------- |
| 0. Diagnostico                        | [0.1](./0.1-legal-ejecutar.md)           | [0.2](./0.2-legal-validar.md)           |
| 1. Function Calling                   | [1.1](./1.1-assets-ejecutar.md)          | [1.2](./1.2-assets-validar.md)          |
| 2. Presentations Tool                 | [2.1](./2.1-config-ejecutar.md)          | [2.2](./2.2-config-validar.md)          |
| 2.3 Persistencia DB (post-etapa 2)    | [2.3](./2.3-db-persistencia-ejecutar.md) | [2.4](./2.4-db-persistencia-validar.md) |
| 3. Story Spec Gamma-like              | [3.1](./3.1-estilos-ejecutar.md)         | [3.2](./3.2-estilos-validar.md)         |
| 4. Theme Selector UX                  | [4.1](./4.1-componentes-ejecutar.md)     | [4.2](./4.2-componentes-validar.md)     |
| 4.3 Saneamiento Tipado (post-etapa 4) | [4.3](./4.3-tipado-ejecutar.md)          | [4.4](./4.4-tipado-validar.md)          |
| 5. Theme Contrast Tokens              | [5.1](./5.1-docker-ejecutar.md)          | [5.2](./5.2-docker-validar.md)          |
| 6. Railway Deploy                     | [6.1](./6.1-mcp-ejecutar.md)             | [6.2](./6.2-mcp-validar.md)             |
| 7. QA y Cierre                        | [7.1](./7.1-qa-ejecutar.md)              | [7.2](./7.2-qa-validar.md)              |
