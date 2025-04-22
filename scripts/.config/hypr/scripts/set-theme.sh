#!/bin/bash

WALLPAPER="$1"

if [[ ! -f "$WALLPAPER" ]]; then
    echo "⛔ That's not valid, go fuck yourself."
    exit 1
fi

# Generate pywal theme
wal -i "$WALLPAPER" --backend wal --saturate 0.7

# Load pywal color variables into environment
source ~/.cache/wal/colors.sh

# 1. Set wallpaper (assuming you use swww)
swww img "$(realpath "$WALLPAPER")"

# 2. Reload Waybar (assumes it uses pywal templates/colors)
killall -q waybar && waybar &

# 3. Update Foot config (from template)
envsubst < ~/.config/foot/foot.ini.tpl > ~/.config/foot/foot.ini

# 4. Update Wofi CSS (from template)
envsubst < ~/.config/wofi/style.css.tpl > ~/.config/wofi/style.css

# 5. Update nwg-drawer color scheme
cp ~/.cache/wal/colors.css ~/.config/nwg-drawer/colors.css

# 6. Restart mako to pick up colors
killall -q mako && mako &

# Done
notify-send "🎨 Theme updated!" "Using wallpaper: $(basename "$WALLPAPER")"
