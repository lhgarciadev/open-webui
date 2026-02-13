#!/bin/bash
# ==============================================================================
# verify_compliance.sh - Verificacion de cumplimiento de marca blanca
# ==============================================================================
# Este script verifica que no existan referencias a "Open WebUI" en el codigo
# fuente del frontend, archivos estaticos y configuraciones.
#
# Exclusiones permitidas:
# - LICENSE (atribucion legal requerida)
# - planning/ (documentacion interna)
# - README.md (puede contener referencias historicas)
# - node_modules/ (dependencias externas)
# - .git/ (historial de git)
# ==============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
ERRORS=0
WARNINGS=0

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}     VERIFICACION DE COMPLIANCE - MARCA BLANCA${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# ==============================================================================
# 1. Verificar codigo fuente (src/)
# ==============================================================================
echo -e "${YELLOW}[1/5] Verificando codigo fuente (src/)...${NC}"

FOUND_SRC=$(grep -rEi "Open WebUI" src/ 2>/dev/null \
    | grep -v "node_modules" \
    | grep -v ".svelte-kit" \
    || true)

if [ -n "$FOUND_SRC" ]; then
    echo -e "${RED}  ❌ Encontrado 'Open WebUI' en src/:${NC}"
    echo "$FOUND_SRC" | head -20
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ Limpio${NC}"
fi

# ==============================================================================
# 2. Verificar archivos estaticos (static/)
# ==============================================================================
echo -e "${YELLOW}[2/5] Verificando archivos estaticos (static/)...${NC}"

# Verificar manifest.json
if [ -f "static/manifest.json" ]; then
    FOUND_MANIFEST=$(grep -i "Open WebUI" static/manifest.json 2>/dev/null || true)
    if [ -n "$FOUND_MANIFEST" ]; then
        echo -e "${RED}  ❌ Encontrado 'Open WebUI' en static/manifest.json${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ manifest.json limpio${NC}"
    fi
fi

# Verificar site.webmanifest del backend
if [ -f "backend/open_webui/static/site.webmanifest" ]; then
    FOUND_WEBMANIFEST=$(grep -i "Open WebUI" backend/open_webui/static/site.webmanifest 2>/dev/null || true)
    if [ -n "$FOUND_WEBMANIFEST" ]; then
        echo -e "${RED}  ❌ Encontrado 'Open WebUI' en backend site.webmanifest${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ site.webmanifest limpio${NC}"
    fi
fi

# ==============================================================================
# 3. Verificar HTML principal
# ==============================================================================
echo -e "${YELLOW}[3/5] Verificando HTML principal...${NC}"

if [ -f "src/app.html" ]; then
    FOUND_HTML=$(grep -i "Open WebUI" src/app.html 2>/dev/null || true)
    if [ -n "$FOUND_HTML" ]; then
        echo -e "${RED}  ❌ Encontrado 'Open WebUI' en src/app.html${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ app.html limpio${NC}"
    fi
fi

# ==============================================================================
# 4. Verificar archivos de localizacion (i18n)
# ==============================================================================
echo -e "${YELLOW}[4/5] Verificando archivos de localizacion...${NC}"

if [ -d "src/lib/i18n" ]; then
    FOUND_I18N=$(grep -rEi "Open WebUI" src/lib/i18n/ 2>/dev/null | head -5 || true)
    if [ -n "$FOUND_I18N" ]; then
        echo -e "${YELLOW}  ⚠ Encontrado 'Open WebUI' en archivos i18n (puede requerir revision):${NC}"
        echo "$FOUND_I18N"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}  ✓ Archivos i18n limpios${NC}"
    fi
fi

# ==============================================================================
# 5. Verificar build output
# ==============================================================================
echo -e "${YELLOW}[5/5] Verificando build output (si existe)...${NC}"

if [ -d "build" ]; then
    FOUND_BUILD=$(grep -rEi "Open WebUI" build/ 2>/dev/null | head -5 || true)
    if [ -n "$FOUND_BUILD" ]; then
        echo -e "${YELLOW}  ⚠ Encontrado 'Open WebUI' en build/:${NC}"
        echo "$FOUND_BUILD"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}  ✓ Build output limpio${NC}"
    fi
else
    echo -e "${BLUE}  - Build no existe (ejecutar npm run build)${NC}"
fi

# ==============================================================================
# Resumen
# ==============================================================================
echo ""
echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}     RESUMEN${NC}"
echo -e "${BLUE}================================================================${NC}"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}  ERRORES:    $ERRORS${NC}"
fi
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}  ADVERTENCIAS: $WARNINGS${NC}"
fi

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}  ✓ COMPLIANCE VERIFICADO - Sin problemas encontrados${NC}"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}  ⚠ COMPLIANCE CON ADVERTENCIAS - Revisar manualmente${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}  ❌ COMPLIANCE FALLIDO - $ERRORS errores encontrados${NC}"
    echo ""
    echo "Ejecute las siguientes acciones:"
    echo "  1. Revisar archivos reportados"
    echo "  2. Reemplazar referencias a 'Open WebUI' con APP_NAME"
    echo "  3. Ejecutar este script nuevamente"
    echo ""
    exit 1
fi
