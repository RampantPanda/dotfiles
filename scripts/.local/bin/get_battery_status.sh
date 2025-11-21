#!/bin/bash
# Get battery status with sci-fi themed fuzzy naming

# Try to get battery info from /sys/class/power_supply
BATTERY_PATH="/sys/class/power_supply"
BATTERY=""

# Find battery device
for bat in BAT0 BAT1; do
    if [ -d "$BATTERY_PATH/$bat" ]; then
        BATTERY="$bat"
        break
    fi
done

if [ -z "$BATTERY" ]; then
    # Try to find any battery
    BATTERY=$(ls -1 "$BATTERY_PATH" 2>/dev/null | grep -i "bat" | head -1)
fi

if [ -z "$BATTERY" ] || [ ! -d "$BATTERY_PATH/$BATTERY" ]; then
    echo "POWER: EXTERNAL"
    exit 0
fi

# Get battery capacity and status
CAPACITY=$(cat "$BATTERY_PATH/$BATTERY/capacity" 2>/dev/null || echo "0")
STATUS=$(cat "$BATTERY_PATH/$BATTERY/status" 2>/dev/null || echo "Unknown")

# Convert capacity to integer
CAPACITY=${CAPACITY%.*}

# Determine charging status
if [ "$STATUS" = "Charging" ]; then
    CHARGE_STATUS="│ CHARGE: ACTIVE"
elif [ "$STATUS" = "Full" ]; then
    CHARGE_STATUS="│ CHARGE: COMPLETE"
elif [ "$STATUS" = "Not charging" ]; then
    CHARGE_STATUS="│ CHARGE: STANDBY"
else
    CHARGE_STATUS="│ CHARGE: DISCONNECTED"
fi

# Convert percentage to sci-fi themed state
if [ "$CAPACITY" -ge 90 ]; then
    STATE="OPTIMAL"
    LEVEL="PEAK EFFICIENCY"
elif [ "$CAPACITY" -ge 70 ]; then
    STATE="HIGH"
    LEVEL="STABLE"
elif [ "$CAPACITY" -ge 50 ]; then
    STATE="MODERATE"
    LEVEL="ADEQUATE"
elif [ "$CAPACITY" -ge 30 ]; then
    STATE="LOW"
    LEVEL="DEGRADED"
elif [ "$CAPACITY" -ge 15 ]; then
    STATE="CRITICAL"
    LEVEL="MINIMAL"
else
    STATE="EMERGENCY"
    LEVEL="FAILING"
fi

echo "POWER: $STATE │ LEVEL: $LEVEL $CHARGE_STATUS"

