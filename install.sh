#!/bin/bash
# RampantVibe - Complete Installation Script

set -euo pipefail  # Exit on error, undefined vars, pipe failures

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$HOME/.dotfiles"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}ℹ${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}❌${NC} $*"
}

log_success() {
    echo -e "${GREEN}✅${NC} $*"
}

echo "🎨 RampantVibe Dotfiles Installation"
echo "====================================="
echo ""

# Check prerequisites
log_info "Checking prerequisites..."
if ! command -v stow >/dev/null 2>&1; then
    log_error "stow is required. Install with: sudo pacman -S stow"
    exit 1
fi
log_success "Prerequisites OK"

# Install packages
if [ -f "$SCRIPT_DIR/pacman.sh" ]; then
    log_info "Installing packages..."
    echo ""
    bash "$SCRIPT_DIR/pacman.sh"
    echo ""
else
    log_warn "pacman.sh not found. Skipping package installation."
fi

# Stow all configurations
log_info "Linking dotfiles..."
cd "$SCRIPT_DIR"
STOWED=0
SKIPPED=0

for dir in */; do
    if [ -d "$dir" ] && [ "$dir" != ".git/" ]; then
        dirname="${dir%/}"
        if stow --adopt "$dirname" 2>/dev/null || stow "$dirname" 2>/dev/null; then
            log_success "Stowed ${dirname}"
            ((STOWED++))
        else
            log_warn "Skipped ${dirname} (conflicts)"
            ((SKIPPED++))
        fi
    fi
done

echo ""
log_info "Stowed: $STOWED directories"
[ $SKIPPED -gt 0 ] && log_warn "Skipped: $SKIPPED directories (use --adopt to override)"

# Make scripts executable
log_info "Making scripts executable..."
if [ -d "$HOME/.local/bin" ]; then
    find "$HOME/.local/bin" -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    log_success "Scripts are executable"
else
    log_warn ".local/bin directory not found"
fi

echo ""
log_success "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Log out and log back in to apply changes"
echo "  2. Or reload Hyprland: SUPER + SHIFT + R"
echo ""

