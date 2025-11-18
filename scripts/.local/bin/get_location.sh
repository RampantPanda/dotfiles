#!/bin/bash
# Get location based on IP address

set -euo pipefail

get_location() {
    local url="$1"
    local response=$(curl -s --max-time 3 "$url" 2>/dev/null || true)
    
    [ -z "$response" ] && return 1
    
    # Use jq if available (more reliable than grep)
    if command -v jq &> /dev/null; then
        local city=$(echo "$response" | jq -r '.city // empty' 2>/dev/null || echo "")
        local region=$(echo "$response" | jq -r '.regionName // .region // empty' 2>/dev/null || echo "")
        local country=$(echo "$response" | jq -r '.country // empty' 2>/dev/null || echo "")
        
        if [ -n "$city" ] && [ -n "$region" ]; then
            echo "$city, $region" | tr '[:lower:]' '[:upper:]'
            return 0
        elif [ -n "$city" ] && [ -n "$country" ]; then
            echo "$city, $country" | tr '[:lower:]' '[:upper:]'
            return 0
        elif [ -n "$country" ]; then
            echo "$country" | tr '[:lower:]' '[:upper:]'
            return 0
        fi
    fi
    
    return 1
}

# Try primary service, then fallback
get_location "http://ip-api.com/json/?fields=city,regionName,country" || \
get_location "https://ipinfo.io/json" || \
echo "UNKNOWN"

