#!/bin/sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$REPO_ROOT/.githooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Check if .git directory exists
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo -e "${RED}Error: .git/hooks directory not found.${NC}"
    echo "Make sure you're running this script from a git repository."
    exit 1
fi

# Check if hooks directory exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "${RED}Error: .githooks directory not found.${NC}"
    echo "Make sure you have the .githooks directory in your repository."
    exit 1
fi

# Install each hook
for hook in "$HOOKS_DIR"/*; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        target="$GIT_HOOKS_DIR/$hook_name"
        
        # Make the hook executable
        chmod +x "$hook"
        
        # Create a symlink
        ln -sf "$hook" "$target"
        echo "Installed $hook_name"
    fi
done

echo -e "${GREEN}Git hooks installed successfully!${NC}" 