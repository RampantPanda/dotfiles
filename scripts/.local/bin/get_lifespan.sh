#!/bin/bash
# Calculate system lifespan from install date

# Get install date
if [ -f /var/log/pacman.log ]; then
    INSTALL_DATE=$(head -1 /var/log/pacman.log | grep -oP '\[\K[^\]]+' | head -1)
    if [ -z "$INSTALL_DATE" ]; then
        INSTALL_DATE=$(stat -c %y /etc | cut -d' ' -f1)
    fi
else
    INSTALL_DATE=$(stat -c %y /etc | cut -d' ' -f1)
fi

# Calculate difference
if [ -n "$INSTALL_DATE" ]; then
    # Convert install date to seconds since epoch
    INSTALL_SECONDS=$(date -d "$INSTALL_DATE" +%s 2>/dev/null)
    CURRENT_SECONDS=$(date +%s)
    
    if [ -n "$INSTALL_SECONDS" ] && [ -n "$CURRENT_SECONDS" ]; then
        DIFF_SECONDS=$((CURRENT_SECONDS - INSTALL_SECONDS))
        
        # Calculate years, months, days
        YEARS=$((DIFF_SECONDS / 31536000))
        REMAINING=$((DIFF_SECONDS % 31536000))
        MONTHS=$((REMAINING / 2592000))
        REMAINING=$((REMAINING % 2592000))
        DAYS=$((REMAINING / 86400))
        
        # Format output similar to uptime -p
        if [ $YEARS -gt 0 ]; then
            if [ $YEARS -eq 1 ]; then
                OUTPUT="${YEARS} year"
            else
                OUTPUT="${YEARS} years"
            fi
            if [ $MONTHS -gt 0 ]; then
                if [ $MONTHS -eq 1 ]; then
                    OUTPUT="${OUTPUT} ${MONTHS} month"
                else
                    OUTPUT="${OUTPUT} ${MONTHS} months"
                fi
            fi
            if [ $DAYS -gt 0 ]; then
                if [ $DAYS -eq 1 ]; then
                    OUTPUT="${OUTPUT} ${DAYS} day"
                else
                    OUTPUT="${OUTPUT} ${DAYS} days"
                fi
            fi
        elif [ $MONTHS -gt 0 ]; then
            if [ $MONTHS -eq 1 ]; then
                OUTPUT="${MONTHS} month"
            else
                OUTPUT="${MONTHS} months"
            fi
            if [ $DAYS -gt 0 ]; then
                if [ $DAYS -eq 1 ]; then
                    OUTPUT="${OUTPUT} ${DAYS} day"
                else
                    OUTPUT="${OUTPUT} ${DAYS} days"
                fi
            fi
        elif [ $DAYS -gt 0 ]; then
            if [ $DAYS -eq 1 ]; then
                OUTPUT="${DAYS} day"
            else
                OUTPUT="${DAYS} days"
            fi
        else
            OUTPUT="less than 1 day"
        fi
        
        echo "$OUTPUT"
    else
        echo "UNKNOWN"
    fi
else
    echo "UNKNOWN"
fi

