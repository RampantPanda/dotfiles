#!/bin/bash
# Set wallpaper and update theme colors

set -euo pipefail

WALLPAPER="${1:-}"

if [ -z "$WALLPAPER" ] || [ ! -f "$WALLPAPER" ]; then
    echo "Error: Invalid wallpaper file: ${WALLPAPER:-<none>}" >&2
    exit 1
fi

# Generate pywal theme
wal -i "$WALLPAPER" --backend wal --saturate 0.7

# Load pywal color variables into environment
[ -f ~/.cache/wal/colors.sh ] && source ~/.cache/wal/colors.sh

# 1. Set wallpaper (assuming you use swww)
swww img "$(realpath "$WALLPAPER")"

# 2. Reload Waybar (assumes it uses pywal templates/colors)
killall -q waybar && waybar &

# 3. Update Alacritty config (from template if exists)
[ -f ~/.config/alacritty/alacritty.toml.tpl ] && \
    envsubst < ~/.config/alacritty/alacritty.toml.tpl > ~/.config/alacritty/alacritty.toml

# 4. Update Wofi CSS (from template)
[ -f ~/.config/wofi/style.css.tpl ] && \
    envsubst < ~/.config/wofi/style.css.tpl > ~/.config/wofi/style.css

# 5. Update nwg-drawer color scheme
[ -f ~/.cache/wal/colors.css ] && \
    cp ~/.cache/wal/colors.css ~/.config/nwg-drawer/colors.css

# 6. Restart mako to pick up colors
killall -q mako && mako &

# Done
notify-send "🎨 Theme updated!" "Using wallpaper: $(basename "$WALLPAPER")"
