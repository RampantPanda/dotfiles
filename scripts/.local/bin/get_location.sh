#!/bin/bash
# Get location based on IP address

# Try to get location from IP geolocation service
# Using ip-api.com (free, no API key required)
LOCATION=$(curl -s --max-time 3 "http://ip-api.com/json/?fields=city,regionName,country" 2>/dev/null)

if [ -n "$LOCATION" ] && echo "$LOCATION" | grep -q "city"; then
    CITY=$(echo "$LOCATION" | grep -oP '"city":"\K[^"]*')
    REGION=$(echo "$LOCATION" | grep -oP '"regionName":"\K[^"]*')
    COUNTRY=$(echo "$LOCATION" | grep -oP '"country":"\K[^"]*')
    
    if [ -n "$CITY" ] && [ -n "$REGION" ]; then
        echo "$CITY, $REGION" | tr '[:lower:]' '[:upper:]'
    elif [ -n "$CITY" ] && [ -n "$COUNTRY" ]; then
        echo "$CITY, $COUNTRY" | tr '[:lower:]' '[:upper:]'
    elif [ -n "$COUNTRY" ]; then
        echo "$COUNTRY" | tr '[:lower:]' '[:upper:]'
    else
        echo "UNKNOWN"
    fi
else
    # Fallback: try ipinfo.io
    LOCATION=$(curl -s --max-time 3 "https://ipinfo.io/json" 2>/dev/null)
    if [ -n "$LOCATION" ] && echo "$LOCATION" | grep -q "city"; then
        CITY=$(echo "$LOCATION" | grep -oP '"city":"\K[^"]*')
        REGION=$(echo "$LOCATION" | grep -oP '"region":"\K[^"]*')
        COUNTRY=$(echo "$LOCATION" | grep -oP '"country":"\K[^"]*')
        
        if [ -n "$CITY" ] && [ -n "$REGION" ]; then
            echo "$CITY, $REGION" | tr '[:lower:]' '[:upper:]'
        elif [ -n "$CITY" ] && [ -n "$COUNTRY" ]; then
            echo "$CITY, $COUNTRY" | tr '[:lower:]' '[:upper:]'
        elif [ -n "$COUNTRY" ]; then
            echo "$COUNTRY" | tr '[:lower:]' '[:upper:]'
        else
            echo "UNKNOWN"
        fi
    else
        echo "UNKNOWN"
    fi
fi

