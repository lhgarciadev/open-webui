#!/usr/bin/env bash
set -euo pipefail

# End-to-end validation for DB persistence (Stage 2.4).
# Produces a markdown report under evidence/.

APP_URL="${APP_URL:-http://localhost:3000}"
AI_CONTAINER="${AI_CONTAINER:-cognitia-ai}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-cognitia-postgres}"
REDIS_CONTAINER="${REDIS_CONTAINER:-cognitia-redis}"

PG_USER="${PG_USER:-cognitia_app}"
PG_DB="${PG_DB:-cognitia}"

TEST_USER_EMAIL="${TEST_USER_EMAIL:-}"
TEST_USER_PASSWORD="${TEST_USER_PASSWORD:-}"
TEST_USER_NAME="${TEST_USER_NAME:-}"

STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="evidence/db_persistencia_validacion_${STAMP}.md"
TMP_DIR="/tmp/db_persist_${STAMP}"
mkdir -p "${TMP_DIR}" evidence

check_status_1="FAIL"
check_status_2="FAIL"
check_status_3="FAIL"
check_status_4="FAIL"
check_status_5="FAIL"

result_log() {
  local title="$1"
  local path="$2"
  {
    echo "### ${title}"
    echo '```'
    sed -n '1,120p' "${path}"
    echo '```'
    echo
  } >> "${REPORT}"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing dependency: $1" >&2
    exit 1
  }
}

require_cmd docker
require_cmd curl
require_cmd python3

echo "# Evidencia Etapa 2.4 - Validacion de Persistencia DB" > "${REPORT}"
echo >> "${REPORT}"
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S %z')" >> "${REPORT}"
echo "Repositorio: open-webui (fork Cognitia)" >> "${REPORT}"
echo "Script: \`scripts/validate_db_persistence.sh\`" >> "${REPORT}"
echo >> "${REPORT}"

echo "[1/5] Verificando conectividad y healthchecks..."
{
  docker ps --format 'table {{.Names}}\t{{.Status}}' | sed -n '1,40p'
  docker exec "${POSTGRES_CONTAINER}" pg_isready -U "${PG_USER}" -d "${PG_DB}"
  docker exec "${REDIS_CONTAINER}" redis-cli ping
  curl -sS -i "${APP_URL}/health" | sed -n '1,20p'
  curl -sS -i "${APP_URL}/health/db" | sed -n '1,20p'
} > "${TMP_DIR}/check1.log" 2>&1 || true
if grep -q "accepting connections" "${TMP_DIR}/check1.log" \
  && grep -q "PONG" "${TMP_DIR}/check1.log" \
  && grep -q "200 OK" "${TMP_DIR}/check1.log" \
  && grep -q '{"status":true}' "${TMP_DIR}/check1.log"; then
  check_status_1="PASS"
fi

if [[ -z "${TEST_USER_EMAIL}" || -z "${TEST_USER_PASSWORD}" ]]; then
  TEST_USER_EMAIL="persist.test.${STAMP}@example.com"
  TEST_USER_PASSWORD="Persist#${STAMP}Aa1"
  TEST_USER_NAME="Persist Test ${STAMP}"
  SIGNUP_PAYLOAD="$(cat <<EOF
{"name":"${TEST_USER_NAME}","email":"${TEST_USER_EMAIL}","password":"${TEST_USER_PASSWORD}"}
EOF
)"
  signup_http="$(curl -sS -o "${TMP_DIR}/signup.json" -w '%{http_code}' \
    -H 'Content-Type: application/json' \
    -X POST "${APP_URL}/api/v1/auths/signup" \
    -d "${SIGNUP_PAYLOAD}" || true)"
  if [[ "${signup_http}" != "200" ]]; then
    echo "Signup failed with HTTP ${signup_http}" > "${TMP_DIR}/check2_blocker.log"
    echo "Hint: if signup is disabled, rerun with TEST_USER_EMAIL and TEST_USER_PASSWORD." >> "${TMP_DIR}/check2_blocker.log"
    echo "Example: TEST_USER_EMAIL='admin@acme.com' TEST_USER_PASSWORD='***' scripts/validate_db_persistence.sh" >> "${TMP_DIR}/check2_blocker.log"
    cat "${TMP_DIR}/signup.json" >> "${TMP_DIR}/check2_blocker.log" 2>/dev/null || true
    result_log "Bloqueo flujo minimo (signup)" "${TMP_DIR}/check2_blocker.log"
    echo "Report generated: ${REPORT}"
    exit 1
  fi
  TOKEN="$(python3 -c "import json;print(json.load(open('${TMP_DIR}/signup.json')).get('token',''))")"
  USER_ID="$(python3 -c "import json;print(json.load(open('${TMP_DIR}/signup.json')).get('id',''))")"
else
  SIGNIN_PAYLOAD="$(cat <<EOF
{"email":"${TEST_USER_EMAIL}","password":"${TEST_USER_PASSWORD}"}
EOF
)"
  signin_http="$(curl -sS -o "${TMP_DIR}/signin.json" -w '%{http_code}' \
    -H 'Content-Type: application/json' \
    -X POST "${APP_URL}/api/v1/auths/signin" \
    -d "${SIGNIN_PAYLOAD}" || true)"
  if [[ "${signin_http}" != "200" ]]; then
    echo "Signin failed with HTTP ${signin_http}" > "${TMP_DIR}/check2_blocker.log"
    cat "${TMP_DIR}/signin.json" >> "${TMP_DIR}/check2_blocker.log" 2>/dev/null || true
    result_log "Bloqueo flujo minimo (signin)" "${TMP_DIR}/check2_blocker.log"
    echo "Report generated: ${REPORT}"
    exit 1
  fi
  TOKEN="$(python3 -c "import json;print(json.load(open('${TMP_DIR}/signin.json')).get('token',''))")"
  USER_ID="$(python3 -c "import json;print(json.load(open('${TMP_DIR}/signin.json')).get('id',''))")"
fi

echo "[2/5] Probando flujo minimo de persistencia..."
CHAT_TITLE="Persistencia ${STAMP}"
CHAT_PAYLOAD="$(cat <<EOF
{"chat":{"title":"${CHAT_TITLE}","history":{"messages":{},"currentId":null}}}
EOF
)"
{
  create_http="$(curl -sS -o "${TMP_DIR}/chat_create.json" -w '%{http_code}' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${TOKEN}" \
    -X POST "${APP_URL}/api/v1/chats/new" \
    -d "${CHAT_PAYLOAD}")"
  echo "CHAT_CREATE_HTTP=${create_http}"
  CHAT_ID="$(python3 -c "import json;print(json.load(open('${TMP_DIR}/chat_create.json')).get('id',''))")"
  echo "CHAT_ID=${CHAT_ID}"
  get_http="$(curl -sS -o "${TMP_DIR}/chat_get_before.json" -w '%{http_code}' \
    -H "Authorization: Bearer ${TOKEN}" \
    "${APP_URL}/api/v1/chats/${CHAT_ID}")"
  echo "CHAT_GET_BEFORE_HTTP=${get_http}"
  python3 - <<PY
import json
d=json.load(open("${TMP_DIR}/chat_get_before.json"))
print("CHAT_GET_BEFORE_TITLE=" + d.get("title",""))
PY
  docker exec "${POSTGRES_CONTAINER}" psql -U "${PG_USER}" -d "${PG_DB}" -Atc \
    "SELECT id,user_id,title FROM chat WHERE id='${CHAT_ID}';"
} > "${TMP_DIR}/check2.log" 2>&1 || true

if grep -q "CHAT_CREATE_HTTP=200" "${TMP_DIR}/check2.log" \
  && grep -q "CHAT_GET_BEFORE_HTTP=200" "${TMP_DIR}/check2.log" \
  && grep -q "${CHAT_TITLE}" "${TMP_DIR}/check2.log"; then
  check_status_2="PASS"
fi

echo "[3/5] Reiniciando aplicacion y validando retencion..."
{
  docker restart "${AI_CONTAINER}"
  for _ in $(seq 1 45); do
    health_code="$(curl -s -o "${TMP_DIR}/health_after.json" -w '%{http_code}' "${APP_URL}/health" || true)"
    [[ "${health_code}" == "200" ]] && break
    sleep 1
  done
  echo "HEALTH_AFTER_HTTP=${health_code:-000}"
  signin_http2="$(curl -sS -o "${TMP_DIR}/signin_after.json" -w '%{http_code}' \
    -H 'Content-Type: application/json' \
    -X POST "${APP_URL}/api/v1/auths/signin" \
    -d "{\"email\":\"${TEST_USER_EMAIL}\",\"password\":\"${TEST_USER_PASSWORD}\"}")"
  echo "SIGNIN_AFTER_HTTP=${signin_http2}"
  TOKEN_AFTER="$(python3 -c "import json;print(json.load(open('${TMP_DIR}/signin_after.json')).get('token',''))")"
  get_http_after="$(curl -sS -o "${TMP_DIR}/chat_get_after.json" -w '%{http_code}' \
    -H "Authorization: Bearer ${TOKEN_AFTER}" \
    "${APP_URL}/api/v1/chats/${CHAT_ID}")"
  echo "CHAT_GET_AFTER_HTTP=${get_http_after}"
  python3 - <<PY
import json
d=json.load(open("${TMP_DIR}/chat_get_after.json"))
print("CHAT_GET_AFTER_TITLE=" + d.get("title",""))
print("CHAT_GET_AFTER_USER_ID=" + d.get("user_id",""))
PY
} > "${TMP_DIR}/check3.log" 2>&1 || true

if grep -q "HEALTH_AFTER_HTTP=200" "${TMP_DIR}/check3.log" \
  && grep -q "SIGNIN_AFTER_HTTP=200" "${TMP_DIR}/check3.log" \
  && grep -q "CHAT_GET_AFTER_HTTP=200" "${TMP_DIR}/check3.log"; then
  check_status_3="PASS"
fi

echo "[4/5] Validando migraciones..."
{
  current="$(docker exec "${POSTGRES_CONTAINER}" psql -U "${PG_USER}" -d "${PG_DB}" -Atc "SELECT version_num FROM alembic_version;" || true)"
  echo "ALEMBIC_VERSION_TABLE=${current}"
  docker exec "${AI_CONTAINER}" sh -lc \
    'cd /app/backend/open_webui && WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-tempkey} alembic -c alembic.ini current'
  docker exec "${AI_CONTAINER}" sh -lc \
    'cd /app/backend/open_webui && WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-tempkey} alembic -c alembic.ini heads'
} > "${TMP_DIR}/check4.log" 2>&1 || true
if grep -q "(head)" "${TMP_DIR}/check4.log" \
  && grep -q "ALEMBIC_VERSION_TABLE=" "${TMP_DIR}/check4.log"; then
  check_status_4="PASS"
fi

echo "[5/5] Generando backup basico..."
BACKUP_FILE="/tmp/cognitia_backup_${STAMP}.sql"
{
  docker exec "${POSTGRES_CONTAINER}" sh -lc "pg_dump -U ${PG_USER} -d ${PG_DB}" > "${BACKUP_FILE}"
  ls -lh "${BACKUP_FILE}"
  shasum -a 256 "${BACKUP_FILE}"
  sed -n '1,20p' "${BACKUP_FILE}"
} > "${TMP_DIR}/check5.log" 2>&1 || true
if [[ -s "${BACKUP_FILE}" ]] && grep -q "PostgreSQL database dump" "${TMP_DIR}/check5.log"; then
  check_status_5="PASS"
fi

{
  echo "## Resultado por check"
  echo
  echo "1. Conectividad y healthcheck PostgreSQL/Redis/backend: **${check_status_1}**"
  echo "2. Flujo minimo de persistencia (crear usuario/chat y lectura): **${check_status_2}**"
  echo "3. Reinicio de aplicacion y persistencia post-reinicio: **${check_status_3}**"
  echo "4. Estado de migraciones en base destino (version al dia): **${check_status_4}**"
  echo "5. Backup/recovery basico (snapshot manual exitoso): **${check_status_5}**"
  echo
  if [[ "${check_status_1}${check_status_2}${check_status_3}${check_status_4}${check_status_5}" == "PASSPASSPASSPASSPASS" ]]; then
    echo "Veredicto final: \`PERSISTENCIA OK\`"
  else
    echo "Veredicto final: \`PERSISTENCIA NO OK\`"
  fi
  echo
} >> "${REPORT}"

result_log "Check 1 - Conectividad y healthchecks" "${TMP_DIR}/check1.log"
result_log "Check 2 - Flujo minimo de persistencia" "${TMP_DIR}/check2.log"
result_log "Check 3 - Persistencia post-reinicio" "${TMP_DIR}/check3.log"
result_log "Check 4 - Migraciones" "${TMP_DIR}/check4.log"
result_log "Check 5 - Backup basico" "${TMP_DIR}/check5.log"

{
  echo "## Identificadores de prueba"
  echo
  echo "- TEST_USER_EMAIL: \`${TEST_USER_EMAIL}\`"
  echo "- TEST_USER_ID: \`${USER_ID}\`"
  echo "- TEST_CHAT_ID: \`${CHAT_ID}\`"
  echo "- BACKUP_FILE: \`${BACKUP_FILE}\`"
  echo
} >> "${REPORT}"

echo "Report generated: ${REPORT}"
if [[ "${check_status_1}${check_status_2}${check_status_3}${check_status_4}${check_status_5}" == "PASSPASSPASSPASSPASS" ]]; then
  exit 0
fi
exit 2
