# Fastfetch Configuration

This directory contains the fastfetch configuration for displaying system information with images.

## Installation

1. Install fastfetch and chafa (image backend):
   ```bash
   sudo pacman -S fastfetch chafa
   ```

2. Stow the configuration:
   ```bash
   cd ~/.dotfiles
   stow fastfetch
   ```

## Usage

Simply run:
```bash
fastfetch
```

## Customizing Images

### Using a Custom Image

To use a custom image instead of the auto-detected logo:

1. Place your image in `~/.config/fastfetch/` (e.g., `logo.png`)

2. Update the config to use your image:
   ```json
   "display": {
       "image": {
           "type": "chafa",
           "source": "/home/$USER/.config/fastfetch/logo.png",
           "width": 30,
           "height": 15,
           "gap": 3
       }
   }
   ```

### Adjusting Image Size

Modify the `width` and `height` values in the config:
- Larger values = bigger image (but takes more terminal space)
- Smaller values = smaller image (more compact)

### Changing Image Backend

If chafa doesn't work, you can try other backends:
- `kitty` - For kitty terminal
- `iterm2` - For iTerm2
- `sixel` - For terminals with sixel support

Change the `"type"` field in the config accordingly.

## Configuration File

The config file is located at: `~/.config/fastfetch/config.jsonc`

## Tips

- Use PNG or JPEG images for best results
- Images with transparent backgrounds work well
- Cyberpunk-themed images match the overall dotfile aesthetic!

