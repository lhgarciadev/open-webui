# Evidencia Etapa 2.4 - Validacion de Persistencia DB

Fecha: 2026-02-13
Repositorio: open-webui (fork Cognitia)
Prompt ejecutado: `planning/prompts/2.4-db-persistencia-validar.md`

## Resultado por check

1. Conectividad y healthcheck PostgreSQL/Redis/backend: **PASS**
2. Flujo minimo de persistencia (crear usuario/chat y lectura): **PASS**
3. Reinicio de aplicacion y persistencia post-reinicio: **PASS**
4. Estado de migraciones en base destino (version al dia): **PASS**
5. Backup/recovery basico (snapshot manual exitoso): **PASS**

Veredicto final: `PERSISTENCIA OK`

## Evidencias tecnicas (resumen)

### 1) Conectividad y healthcheck

Comandos:

```bash
docker compose ps
docker exec cognitia-postgres pg_isready -U cognitia_app -d cognitia
docker exec cognitia-redis redis-cli ping
curl -i http://localhost:3000/health
curl -i http://localhost:3000/health/db
```

Resultados clave:

- `cognitia-postgres`: `healthy`
- `cognitia-redis`: `healthy`
- `pg_isready`: `accepting connections`
- `redis-cli ping`: `PONG`
- `GET /health`: `200 {"status":true}`
- `GET /health/db`: `200 {"status":true}`

### 2) Flujo minimo de persistencia (usuario + chat + lectura)

Comandos API:

```bash
POST /api/v1/auths/signup
POST /api/v1/chats/new
GET  /api/v1/chats/{id}
```

Resultados clave:

- Signup: `200` con usuario creado `id=2b2b4836-a595-4645-b273-0ba9cc97873b`
- Crear chat: `200` con chat `id=68e35e23-a513-4c70-8fc5-eb355bd4b7d0`
- Lectura de chat antes de reinicio: `200`, titulo `Persistencia 20260213141033`

Verificacion SQL en PostgreSQL:

```bash
SELECT id,email,role FROM "user" WHERE id='2b2b4836-a595-4645-b273-0ba9cc97873b';
SELECT id,user_id,title FROM chat WHERE id='68e35e23-a513-4c70-8fc5-eb355bd4b7d0';
```

Resultado:

- Usuario y chat presentes en base con relacion correcta `chat.user_id = user.id`.

### 3) Persistencia tras reinicio

Comandos:

```bash
docker restart cognitia-ai
POST /api/v1/auths/signin
GET  /api/v1/chats/{id}
```

Resultados clave:

- Reinicio backend exitoso (`cognitia-ai` vuelve a `healthy`).
- Signin post-reinicio: `200` para el usuario creado en prueba.
- Lectura del chat post-reinicio: `200`, mismo `chat_id` y mismo titulo.

### 4) Migraciones en base destino

Comandos:

```bash
docker exec cognitia-ai sh -lc 'cd /app/backend/open_webui && WEBUI_SECRET_KEY=tempkey alembic -c alembic.ini current'
docker exec cognitia-ai sh -lc 'cd /app/backend/open_webui && WEBUI_SECRET_KEY=tempkey alembic -c alembic.ini heads'
docker exec cognitia-postgres psql -U cognitia_app -d cognitia -Atc "SELECT version_num FROM alembic_version;"
```

Resultados clave:

- `alembic current`: `c440947495f3 (head)`
- `alembic heads`: `c440947495f3 (head)`
- Tabla `alembic_version`: `c440947495f3`

### 5) Backup/recovery basico

Comando:

```bash
docker exec cognitia-postgres sh -lc 'pg_dump -U cognitia_app -d cognitia' > /tmp/cognitia_backup_20260213_141120.sql
```

Resultados clave:

- Backup generado: `/tmp/cognitia_backup_20260213_141120.sql`
- Tamano: `37K`
- SHA256: `3a615eaceef428c57c8d13451efe89e993656a19247d331a4efae09c87f67e50`
- Header valido de dump PostgreSQL presente.

## Riesgos abiertos y accion correctiva inmediata

- Riesgo: `WEBUI_SECRET_KEY` aparece vacio en entorno del contenedor (`cognitia-ai`), lo que obliga override manual para ejecutar Alembic desde shell.
- Impacto: riesgo de seguridad y friccion operativa para tareas de mantenimiento.
- Accion inmediata:
  1. Definir `WEBUI_SECRET_KEY` no vacio en secretos de despliegue.
  2. Reiniciar servicio.
  3. Revalidar `alembic current` sin override temporal.
