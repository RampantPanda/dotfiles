# RampantVibe - Cyberpunk 1980s Retrofuturistic Dotfiles

A complete Hyprland configuration with a cyberpunk aesthetic, featuring Blade Runner-inspired theming, neon colors, and a fully functional tiling window manager setup.

## 🎨 Theme Overview

This dotfile collection provides:
- **Cyberpunk 1980s Retrofuturistic** color scheme (neon cyan, magenta, green)
- **Blade Runner-inspired** lockscreen with dynamic system information
- **Transparent waybar** with workspace indicators
- **Custom GTK themes** for applications
- **Neon terminal** styling

## 📋 Prerequisites

- Arch Linux (or Arch-based distribution)
- Hyprland compositor
- GNU Stow (for managing dotfiles)
- Root/sudo access for package installation

## 🚀 Installation

### 1. Install Required Packages

Run the installation script to install all necessary packages:

```bash
./pacman.sh
```

This will install:
- **Window Manager**: Hyprland, waybar, hypridle, hyprlock
- **Utilities**: grim, slurp, swappy, wofi, foot, mako, cliphist, wl-clipboard
- **Applications**: thunar, geany, firedragon, thunderbird, and more
- **Fonts**: JetBrains Mono, Orbitron, Rajdhani, Exo, Audiowide, oldschool-pc-fonts
- **System**: network-manager-applet, polkit-gnome, brightnessctl, pamixer, playerctl

### 2. Clone and Setup Dotfiles

```bash
# Clone the repository
git clone <repository-url> ~/.dotfiles
cd ~/.dotfiles

# Install GNU Stow if not already installed
sudo pacman -S stow

# Stow all configuration directories
stow */
```

### 3. Make Scripts Executable

```bash
chmod +x ~/.local/bin/*.sh
```

### 4. Install Cursor Theme (Optional)

The configuration uses Sweet-cursors. If you want to use it:

```bash
# Install from AUR or your preferred method
yay -S sweet-cursors
```

### 5. Restart Hyprland

Log out and log back in, or restart your Hyprland session to apply all changes.

## ⌨️ Keyboard Shortcuts

**Main Modifier**: `SUPER` (Windows key)

### Window Management

| Shortcut | Action |
|----------|--------|
| `SUPER + Q` | Close active window |
| `SUPER + M` | Toggle fullscreen (maximize) |
| `SUPER + F` | Toggle fullscreen (windowed) |
| `SUPER + SHIFT + F` | Toggle fullscreen state |
| `SUPER + SPACE` | Toggle floating window |
| `SUPER + R` | Enter resize mode (use arrow keys, ESC to exit) |
| `SUPER + SHIFT + Arrow Keys` / `HJKL` | Move window |
| `SUPER + Mouse Drag` | Move window |
| `SUPER + Right Mouse Drag` | Resize window |

### Workspace Navigation

| Shortcut | Action |
|----------|--------|
| `SUPER + 1-9, 0` | Switch to workspace 1-10 |
| `SUPER + SHIFT + 1-9, 0` | Move window to workspace 1-10 |
| `ALT + SHIFT + 1-9, 0` | Move focused container to workspace |
| `SUPER + Mouse Scroll` | Switch workspaces |
| `SUPER + SHIFT + S` | Toggle special workspace |

### Focus Movement

| Shortcut | Action |
|----------|--------|
| `SUPER + Arrow Keys` / `HJKL` | Move focus (left/down/up/right) |
| `SUPER + H` | Move focus left |
| `SUPER + J` | Move focus down |
| `SUPER + K` | Move focus up |
| `SUPER + L` | Move focus right |

### Application Launchers

| Shortcut | Action |
|----------|--------|
| `SUPER` (hold) | Application launcher (wofi) |
| `SUPER + D` | Application drawer (nwg-drawer) |
| `SUPER + M` | Power menu (nwgbar) |
| `SUPER + ENTER` | Terminal (foot) |
| `SUPER + E` | File manager (thunar) |

### Application Shortcuts (Function Keys)

| Shortcut | Application |
|----------|-------------|
| `SUPER + F1` | Firedragon (browser) |
| `SUPER + F2` | Thunderbird (email) |
| `SUPER + F3` | Thunar (file manager) |
| `SUPER + F4` | Geany (text editor) |
| `SUPER + F5` | GitHub Desktop |
| `SUPER + F6` | GParted (disk manager) |
| `SUPER + F7` | Inkscape |
| `SUPER + F8` | Blender |
| `SUPER + F9` | Meld (diff tool) |
| `SUPER + F10` | Joplin Desktop |
| `SUPER + F11` | Snapper Tools |
| `SUPER + F12` | Calculator |

### Screenshots

| Shortcut | Action |
|----------|--------|
| `Print` | Screenshot current display |
| `SHIFT + Print` | Screenshot active window |
| `CTRL + Print` | Screenshot selected area |

### Media Controls

| Shortcut | Action |
|----------|--------|
| `Media Key 172` | Play/Pause |
| `Media Key 171` | Next track |
| `Media Key 173` | Previous track |

### Audio Controls

| Shortcut | Action |
|----------|--------|
| `F10` | Decrease volume |
| `F11` | Increase volume |
| `F9` | Toggle mute |
| `XF86AudioMicMute` | Toggle microphone mute |

### Brightness Controls

| Shortcut | Action |
|----------|--------|
| `F6` | Decrease brightness |
| `F7` | Increase brightness |

### System

| Shortcut | Action |
|----------|--------|
| `SUPER + SHIFT + R` | Reload Hyprland configuration |
| `ALT + L` | Lock screen (hyprlock) |
| `SUPER + V` | Clipboard manager |
| `SUPER + SHIFT + C` | Restart wallpaper daemon (wpaperd) |
| `SUPER + O` | Open browser (firedragon) |

### Resize Mode

Enter resize mode with `SUPER + R`, then:
- `Arrow Keys` / `HJKL` - Resize window
- `ESC` - Exit resize mode

## 🎯 Features

### Waybar

- **Workspace Indicators**: 8 persistent workspaces with custom icons
  - Purple: Active workspace
  - Green: Inactive (occupied) workspaces
  - Cyan: Empty workspaces
- **System Monitoring**: CPU, memory, temperature, battery
- **Audio Control**: Click to open pavucontrol
- **Network Status**: WiFi/Ethernet indicators
- **Transparent Background**: 30% opacity for a modern look

### Lockscreen (Hyprlock)

- **Blade Runner Theme**: Cyberpunk aesthetic with neon green terminal styling
- **Dynamic Information**:
  - System installation date
  - System lifespan (days since install)
  - Current location (based on IP geolocation)
  - Memory and disk usage
  - Current date and time
- **Screenshot Background**: Blurred screenshot of current screen

### Applications

- **Terminal**: Foot with cyberpunk color scheme
- **File Manager**: Thunar with transparency
- **Text Editor**: Geany with custom cyberpunk color scheme
- **Launcher**: Wofi with cyberpunk styling
- **Screenshot Tool**: Grim + Slurp + Swappy integration

### Clipboard Manager

- Automatic text and image clipboard history
- Access with `SUPER + V`
- Uses cliphist for management

## 🎨 Customization

### Changing Colors

The color scheme is defined in multiple places:
- **Waybar**: `waybar/.config/waybar/style.css`
- **Geany**: `geany/.config/geany/colorschemes/cyberpunk.conf`
- **Terminal**: `alacritty/.config/alacritty/alacritty.toml` or `foot/.config/foot/foot.ini`

### Changing Wallpapers

Wallpapers are managed by `wpaperd`. Configure in `wpaperd/.config/wpaperd/`.

### Modifying Keybindings

Edit `hyprland/.config/hypr/hyprland.conf` and reload with `SUPER + SHIFT + R`.

### Waybar Configuration

- **Config**: `waybar/.config/waybar/config`
- **Style**: `waybar/.config/waybar/style.css`

## 📁 Directory Structure

```
.dotfiles/
├── alacritty/          # Alacritty terminal config
├── cava/              # Audio visualizer
├── foot/              # Foot terminal config
├── geany/             # Geany editor config and theme
├── gtk/               # GTK theme settings
├── hypridle/          # Idle management
├── hyprland/          # Hyprland window manager config
├── hyprlock/          # Lockscreen configuration
├── hyprstart/         # Startup environment variables
├── mako/              # Notification daemon
├── nwg-launchers/     # Application launchers
├── scripts/           # Helper scripts
├── starship/          # Shell prompt
├── swappy/            # Screenshot editor
├── wal/               # Wallpaper utilities
├── waybar/            # Status bar
├── wofi/              # Application launcher
├── wpaperd/           # Wallpaper daemon
├── yazi/              # File manager
├── pacman.sh          # Package installation script
└── README.md          # This file
```

## 🔧 Troubleshooting

### Waybar Not Showing

```bash
# Check if waybar is running
killall waybar && waybar &
```

### Cursor Theme Warning

The configuration uses Adwaita cursor theme for GTK applications. If you see warnings, ensure:
- GTK settings are stowed: `stow gtk`
- Environment variables are set in `hyprland.conf`

### Screenshots Not Working

Ensure these packages are installed:
- `grim` (screenshot tool)
- `slurp` (region selector)
- `swappy` (screenshot editor)

### Applications Not Launching

Check if the application is installed:
```bash
pacman -Qs <package-name>
```

### Stow Conflicts

If stow reports conflicts:
```bash
# Use --adopt to adopt existing files
stow --adopt <directory>

# Or manually remove conflicting files first
```

## 📝 Notes

- The configuration assumes a Finnish keyboard layout (`kb_layout = fi`). Change in `hyprland.conf` if needed.
- Monitor configuration is set for `eDP-1` at 1920x1080@60Hz. Adjust in `hyprland.conf` for your setup.
- Some applications (like firedragon, github-desktop) may need to be installed from AUR or alternative sources.

## 🎮 Workspace Icons

The waybar shows 8 workspaces with custom icons:
1. 🎞️ (Media)
2. 📹 (Video)
3. 📁 (Files)
4. 🎬 (Projects)
5. 🎵 (Music)
6. 🎮 (Games)
7. 📧 (Communication)
8. ⚡ (Utilities)

## 🔄 Updating

After pulling updates:

```bash
cd ~/.dotfiles
git pull
stow */
```

Then reload Hyprland: `SUPER + SHIFT + R`

## 📄 License

See LICENSE file for details.

## 🙏 Credits

- **Hyprland**: https://hyprland.org/
- **Waybar**: https://github.com/Alexays/Waybar
- **Theme Inspiration**: Blade Runner (1982), Cyberpunk 1980s aesthetic

---

**Enjoy your cyberpunk desktop experience!** 🚀✨
