#!/bin/bash
# Get system installation date

set -euo pipefail

if [ -f /var/log/pacman.log ]; then
    INSTALL_DATE=$(head -1 /var/log/pacman.log | grep -oP '\[\K[^\]]+' | head -1 || echo "")
    [ -z "$INSTALL_DATE" ] && INSTALL_DATE=$(stat -c %y /etc | cut -d' ' -f1)
else
    INSTALL_DATE=$(stat -c %y /etc | cut -d' ' -f1)
fi

if [ -n "$INSTALL_DATE" ]; then
    date -d "$INSTALL_DATE" +"%B %d, %Y" 2>/dev/null | tr '[:lower:]' '[:upper:]' || echo "$INSTALL_DATE"
else
    echo "UNKNOWN"
fi

