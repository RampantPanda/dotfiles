#!/bin/bash
# Toggle hypridle (idle inhibitor)

set -euo pipefail

if pidof hypridle &>/dev/null; then
    killall -9 hypridle
    notify-send "idle inhibitor activated"
else
    hypridle &> /dev/null &
    notify-send "idle inhibitor deactivated"
fi
