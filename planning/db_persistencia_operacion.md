# Persistencia DB Operacion y Recovery Basico

## Objetivo

Persistir usuarios, sesiones, chats y metadatos fuera del filesystem local del contenedor de aplicacion.

## Arquitectura elegida

- `cognitia-ai` como servicio de aplicacion.
- `postgres` (PostgreSQL 16) como base transaccional con volumen durable `cognitia-postgres-data`.
- `redis` (Redis 7) para sesiones/cache/realtime con volumen durable `cognitia-redis-data` (AOF habilitado).
- Topologia por `docker-compose.whitelabel.yaml` + `docker-compose.persistence.yaml`.

## Variables requeridas (sin hardcodear secretos)

- `SECRET_KEY`: clave obligatoria para `WEBUI_SECRET_KEY` (JWT/sesiones).
- `DATABASE_URL`: URL PostgreSQL persistente.
- `REDIS_URL`: URL Redis.
- `ENABLE_DB_MIGRATIONS=true`: aplica migraciones al arrancar backend.
- `POSTGRES_PASSWORD`: inyectada por secreto del proveedor.

Ejemplo recomendado:

```env
SECRET_KEY=<secret-manager>
POSTGRES_DB=cognitia
POSTGRES_USER=cognitia_app
POSTGRES_PASSWORD=<secret-manager>
DATABASE_URL=postgresql://cognitia_app:<secret-manager>@postgres:5432/cognitia
REDIS_URL=redis://redis:6379/0
ENABLE_DB_MIGRATIONS=true
```

## Provisionamiento

1. Definir secretos en el proveedor (o `.env.whitelabel` local para pruebas):
   - `POSTGRES_PASSWORD`
   - credenciales completas de `DATABASE_URL`
2. Levantar stack:
   ```bash
   docker compose --env-file .env.whitelabel \
     -f docker-compose.whitelabel.yaml \
     -f docker-compose.persistence.yaml \
     up -d
   ```
3. Validar salud:
   ```bash
   docker compose -f docker-compose.whitelabel.yaml -f docker-compose.persistence.yaml ps
   ```
4. Ejecutar migracion manual (si se requiere fuera del arranque automatico):
   ```bash
   cd backend
   DATABASE_URL='postgresql://...' alembic -c open_webui/alembic.ini upgrade head
   ```

## Backups y recovery basico

- PostgreSQL:
  - Backup logico: `pg_dump` diario + retencion.
  - Recovery: restaurar `pg_dump` en nueva instancia o restaurar volumen/snapshot.
- Redis:
  - AOF habilitado para reconstruccion por reinicio.
  - Para recovery total, restaurar volumen `cognitia-redis-data` o recrear cache desde PostgreSQL si aplica.

## Rollback operativo

1. Congelar trafico de escritura (mantenimiento).
2. Restaurar backup PostgreSQL previo (dump o snapshot).
3. Desplegar imagen previa de `cognitia-ai`.
4. Verificar tablas clave (`user`, `chat`, `message`, `oauth_session`).
5. Habilitar trafico y monitorear errores.

## Evidencia

- Evidencia tecnica de configuracion y ejecucion de migraciones en este entorno:
  - `evidence/db_migrations_20260213.md`
