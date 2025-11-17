#!/bin/bash
# Get system installation date

if [ -f /var/log/pacman.log ]; then
    INSTALL_DATE=$(head -1 /var/log/pacman.log | grep -oP '\[\K[^\]]+' | head -1)
    if [ -n "$INSTALL_DATE" ]; then
        date -d "$INSTALL_DATE" +"%B %d, %Y" 2>/dev/null | tr '[:lower:]' '[:upper:]' || echo "$INSTALL_DATE"
    else
        stat -c %y /etc | cut -d' ' -f1 | xargs -I {} date -d {} +"%B %d, %Y" 2>/dev/null | tr '[:lower:]' '[:upper:]' || echo "UNKNOWN"
    fi
else
    stat -c %y /etc | cut -d' ' -f1 | xargs -I {} date -d {} +"%B %d, %Y" 2>/dev/null | tr '[:lower:]' '[:upper:]' || echo "UNKNOWN"
fi

