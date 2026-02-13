#!/bin/bash
# ==============================================================================
# build-whitelabel.sh - Cognitia White-Label Docker Build Script
# ==============================================================================
# Usage: ./scripts/build-whitelabel.sh
# With custom settings: BRAND_NAME="MyBrand" VERSION="1.0.0" ./scripts/build-whitelabel.sh

set -e

# Configuration
BRAND_NAME="${BRAND_NAME:-Cognitia}"
VERSION="${VERSION:-$(git describe --tags --always 2>/dev/null || echo 'dev')}"
REGISTRY="${REGISTRY:-local}"
USE_CUDA="${USE_CUDA:-false}"
USE_OLLAMA="${USE_OLLAMA:-false}"
USE_SLIM="${USE_SLIM:-false}"
BUILD_HASH="${BUILD_HASH:-$(git rev-parse --short HEAD 2>/dev/null || echo 'dev')}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=============================================="
echo "  Cognitia White-Label Docker Build"
echo "=============================================="
echo -e "${NC}"
echo -e "  Brand:    ${GREEN}${BRAND_NAME}${NC}"
echo -e "  Version:  ${GREEN}${VERSION}${NC}"
echo -e "  Hash:     ${GREEN}${BUILD_HASH}${NC}"
echo -e "  Registry: ${GREEN}${REGISTRY}${NC}"
echo -e "  CUDA:     ${YELLOW}${USE_CUDA}${NC}"
echo -e "  Ollama:   ${YELLOW}${USE_OLLAMA}${NC}"
echo -e "  Slim:     ${YELLOW}${USE_SLIM}${NC}"
echo "=============================================="
echo ""

# Validate we're in the correct directory
if [ ! -f "Dockerfile.whitelabel" ]; then
    echo -e "${RED}Error: Dockerfile.whitelabel not found.${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Build the image
echo -e "${BLUE}Building Docker image...${NC}"
echo ""

docker build \
    --build-arg BRAND_NAME="${BRAND_NAME}" \
    --build-arg BUILD_HASH="${BUILD_HASH}" \
    --build-arg USE_CUDA="${USE_CUDA}" \
    --build-arg USE_OLLAMA="${USE_OLLAMA}" \
    --build-arg USE_SLIM="${USE_SLIM}" \
    -f Dockerfile.whitelabel \
    -t "${REGISTRY}/cognitia-ai:${VERSION}" \
    -t "${REGISTRY}/cognitia-ai:latest" \
    .

echo ""
echo -e "${GREEN}=============================================="
echo "  Build Complete!"
echo "==============================================${NC}"
echo ""
echo "  Image: ${REGISTRY}/cognitia-ai:${VERSION}"
echo "  Image: ${REGISTRY}/cognitia-ai:latest"
echo ""
echo -e "${BLUE}To run:${NC}"
echo "  docker-compose -f docker-compose.whitelabel.yaml up -d"
echo ""
echo -e "${BLUE}To run with custom env:${NC}"
echo "  docker-compose --env-file .env.whitelabel -f docker-compose.whitelabel.yaml up -d"
echo ""
