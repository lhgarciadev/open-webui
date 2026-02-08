#!/bin/bash

# Find "Open WebUI" case-insensitive in src/
# Exclude the constants file itself to avoid false positives if I decide to reference the old name in comments there (though I shouldn't).
# Also excluding node_modules just in case, though it says src/.

echo "Verifying compliance..."
FOUND=$(grep -rEi "Open WebUI" src/ | grep -v "src/lib/constants/identity.ts")

if [ -n "$FOUND" ]; then
    echo "❌ Compliance verification FAILED. Found 'Open WebUI' in the following files:"
    echo "$FOUND"
    exit 1
else
    echo "✅ Compliance verification PASSED. No 'Open WebUI' branding found in src/."
    exit 0
fi
