#!/bin/bash
echo "========================================"
echo "Building image..."
echo "========================================"
docker build -t gist-api:local ./gist-api

echo ""
echo "========================================"
echo "Scanning image with Trivy..."
echo "========================================"
trivy image --severity CRITICAL,HIGH gist-api:local

echo ""
echo "========================================"
echo "Scanning filesystem with Trivy..."
echo "========================================"
trivy fs --severity CRITICAL,HIGH ./gist-api

echo ""
echo "========================================"
echo "Scanning for secrets with Gitleaks..."
echo "========================================"
gitleaks detect --source . --verbose

echo ""
echo "========================================"
echo "Scan complete"
echo "========================================"
