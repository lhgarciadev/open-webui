# Evidencia Etapa 2.3 - Persistencia DB y migraciones

Fecha: 2026-02-13
Repositorio: open-webui (fork Cognitia)

## 1) Configuracion de despliegue persistente aplicada
- Archivo agregado: `docker-compose.persistence.yaml`
- Integracion validada con:

```bash
docker compose -f docker-compose.whitelabel.yaml -f docker-compose.persistence.yaml config
```

Resultado: `OK` (archivo compuesto generado en `/tmp/cognitia-compose-persistence-config.yaml`, 152 lineas).

## 2) Intento de migracion en entorno objetivo PostgreSQL
Comando ejecutado:

```bash
docker compose -f docker-compose.whitelabel.yaml -f docker-compose.persistence.yaml up -d postgres redis
```

Resultado en este entorno de ejecucion:

```text
Cannot connect to the Docker daemon at unix:///Users/juan.quiroga/.docker/run/docker.sock. Is the docker daemon running?
```

Nuevo intento tras activar Docker en el host:

```bash
docker info --format '{{.ServerVersion}}'
```

Resultado en este entorno de ejecucion del agente:

```text
permission denied while trying to connect to the Docker daemon socket at unix:///Users/juan.quiroga/.docker/run/docker.sock: ... connect: operation not permitted
```

## 2.1) Ejecucion exitosa en host local del usuario (Docker activo)
Comando ejecutado en host local:

```bash
docker compose -f docker-compose.whitelabel.yaml -f docker-compose.persistence.yaml up -d
docker compose -f docker-compose.whitelabel.yaml -f docker-compose.persistence.yaml logs -f cognitia-ai
```

Evidencia observada en logs:
- Contenedores `cognitia-postgres`, `cognitia-redis` y `cognitia-ai` iniciados y saludables.
- Alembic ejecutado sobre `PostgresqlImpl`.
- Secuencia completa de migraciones aplicada hasta `c440947495f3` (`Add chat_file table`).
- Backend levantado con `Started server process` y `Waiting for application startup`.

## 3) Intento alterno de ejecutar Alembic local
Comando ejecutado:

```bash
cd backend/open_webui
DATABASE_URL='sqlite:////tmp/cognitia_persist_stage23.db' ../../.venv/bin/alembic -c alembic.ini upgrade head
```

Resultado en este entorno de ejecucion:

```text
OMP: Error #179: Function Can't open SHM2 failed:
OMP: System error #2: No such file or directory
```

## 4) Comando final para ejecutar migracion cuando el entorno tenga Docker daemon activo

```bash
docker compose --env-file .env.whitelabel \
  -f docker-compose.whitelabel.yaml \
  -f docker-compose.persistence.yaml \
  up -d postgres redis cognitia-ai

# migracion explicita (opcional, si no se usa arranque automatico)
cd backend/open_webui
DATABASE_URL='postgresql://<user>:<password>@localhost:5433/<db>' ../../.venv/bin/alembic -c alembic.ini upgrade head
```
