#!/bin/bash
# Calculate system lifespan from install date

set -euo pipefail

get_install_date() {
    if [ -f /var/log/pacman.log ]; then
        head -1 /var/log/pacman.log | grep -oP '\[\K[^\]]+' | head -1 || stat -c %y /etc | cut -d' ' -f1
    else
        stat -c %y /etc | cut -d' ' -f1
    fi
}

INSTALL_DATE=$(get_install_date)
[ -z "$INSTALL_DATE" ] && { echo "UNKNOWN"; exit 0; }

INSTALL_SECONDS=$(date -d "$INSTALL_DATE" +%s 2>/dev/null || echo "")
[ -z "$INSTALL_SECONDS" ] && { echo "UNKNOWN"; exit 0; }

CURRENT_SECONDS=$(date +%s)
DIFF_SECONDS=$((CURRENT_SECONDS - INSTALL_SECONDS))

# Calculate time components
YEARS=$((DIFF_SECONDS / 31536000))
REMAINING=$((DIFF_SECONDS % 31536000))
MONTHS=$((REMAINING / 2592000))
REMAINING=$((REMAINING % 2592000))
DAYS=$((REMAINING / 86400))

# Build output string
OUTPUT=""
[ $YEARS -gt 0 ] && OUTPUT="${YEARS} year$([ $YEARS -ne 1 ] && echo s)"
[ $MONTHS -gt 0 ] && OUTPUT="${OUTPUT}${OUTPUT:+ }${MONTHS} month$([ $MONTHS -ne 1 ] && echo s)"
[ $DAYS -gt 0 ] && OUTPUT="${OUTPUT}${OUTPUT:+ }${DAYS} day$([ $DAYS -ne 1 ] && echo s)"

echo "${OUTPUT:-less than 1 day}"

