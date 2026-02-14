# Evidencia Etapa 2.4 - Validacion de Persistencia DB

Fecha: 2026-02-13 14:17:08 -0500
Repositorio: open-webui (fork Cognitia)
Script: `scripts/validate_db_persistence.sh`

## Resultado por check

1. Conectividad y healthcheck PostgreSQL/Redis/backend: **PASS**
2. Flujo minimo de persistencia (crear usuario/chat y lectura): **PASS**
3. Reinicio de aplicacion y persistencia post-reinicio: **PASS**
4. Estado de migraciones en base destino (version al dia): **PASS**
5. Backup/recovery basico (snapshot manual exitoso): **PASS**

Veredicto final: `PERSISTENCIA OK`

### Check 1 - Conectividad y healthchecks
```
NAMES               STATUS
cognitia-ai         Up 6 minutes (healthy)
cognitia-ollama     Up 17 minutes (unhealthy)
cognitia-redis      Up 17 minutes (healthy)
cognitia-postgres   Up 17 minutes (healthy)
/var/run/postgresql:5432 - accepting connections
PONG
HTTP/1.1 200 OK
date: Fri, 13 Feb 2026 19:17:08 GMT
server: uvicorn
content-length: 15
content-type: application/json
x-process-time: 0

{"status":true}HTTP/1.1 200 OK
date: Fri, 13 Feb 2026 19:17:08 GMT
server: uvicorn
content-length: 15
content-type: application/json
x-process-time: 0

{"status":true}```

### Check 2 - Flujo minimo de persistencia
```
CHAT_CREATE_HTTP=200
CHAT_ID=13c3f80b-0fd2-4b34-9776-3d5d6fc53c85
CHAT_GET_BEFORE_HTTP=200
CHAT_GET_BEFORE_TITLE=Persistencia 20260213_141708
13c3f80b-0fd2-4b34-9776-3d5d6fc53c85|2b2b4836-a595-4645-b273-0ba9cc97873b|Persistencia 20260213_141708
```

### Check 3 - Persistencia post-reinicio
```
cognitia-ai
HEALTH_AFTER_HTTP=200
SIGNIN_AFTER_HTTP=200
CHAT_GET_AFTER_HTTP=200
CHAT_GET_AFTER_TITLE=Persistencia 20260213_141708
CHAT_GET_AFTER_USER_ID=2b2b4836-a595-4645-b273-0ba9cc97873b
```

### Check 4 - Migraciones
```
ALEMBIC_VERSION_TABLE=c440947495f3
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
c440947495f3 (head)
c440947495f3 (head)
```

### Check 5 - Backup basico
```
-rw-r--r--@ 1 juan.quiroga  wheel    38K Feb 13 14:17 /tmp/cognitia_backup_20260213_141708.sql
cea2fffbc392b45c4ca2158fd6221274015319f4462d5fae9bbf481ac6804cd8  /tmp/cognitia_backup_20260213_141708.sql
--
-- PostgreSQL database dump
--

\restrict 8qyodwGDQTvQEHblEgdwVbm8u1LcQt4P04rln2b03XnaJWRb8DO156L56AhPMF2

-- Dumped from database version 16.12
-- Dumped by pg_dump version 16.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

```

## Identificadores de prueba

- TEST_USER_EMAIL: `persist.test.20260213141033@example.com`
- TEST_USER_ID: `2b2b4836-a595-4645-b273-0ba9cc97873b`
- TEST_CHAT_ID: `13c3f80b-0fd2-4b34-9776-3d5d6fc53c85`
- BACKUP_FILE: `/tmp/cognitia_backup_20260213_141708.sql`

