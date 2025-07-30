#!/bin/bash

# Installation script for the vaahai detect-language command
# This script creates the necessary symlinks to make the command available

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're installing locally or system-wide
LOCAL_INSTALL=false
for arg in "$@"; do
    if [ "$arg" == "--local" ]; then
        LOCAL_INSTALL=true
        break
    fi
done

# Function to create symlinks
create_symlinks() {
    local target_dir="$1"
    
    # Create target directory if it doesn't exist
    mkdir -p "$target_dir"
    
    # Create symlink for the script
    ln -sf "$SCRIPT_DIR/vaahai-detect-language-script" "$target_dir/vaahai-detect-language-script"
    
    # Create wrapper script for 'vaahai detect-language' command
    cat > "$target_dir/vaahai-detect-language-wrapper" << 'EOF'
#!/bin/bash
# Wrapper script for vaahai detect-language command
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
"$SCRIPT_DIR/vaahai-detect-language-script" "$@"
EOF
    
    # Make the wrapper script executable
    chmod +x "$target_dir/vaahai-detect-language-wrapper"
    
    # Create symlink for the vaahai command
    if [ -e "$target_dir/vaahai" ]; then
        echo -e "${YELLOW}Note: 'vaahai' command already exists in $target_dir${NC}"
    else
        # Create a basic vaahai command if it doesn't exist
        cat > "$target_dir/vaahai" << 'EOF'
#!/bin/bash
# Vaahai command wrapper
COMMAND="$1"
shift

if [ "$COMMAND" == "detect-language" ]; then
    "$(dirname "$0")/vaahai-detect-language-wrapper" "$@"
else
    echo "Unknown command: $COMMAND"
    echo "Available commands: detect-language"
    exit 1
fi
EOF
        chmod +x "$target_dir/vaahai"
        echo -e "${GREEN}Created 'vaahai' command in $target_dir${NC}"
    fi
}

if [ "$LOCAL_INSTALL" = true ]; then
    # Local installation
    LOCAL_BIN_DIR="$PROJECT_ROOT/local/bin"
    
    echo -e "${GREEN}Installing vaahai detect-language command locally...${NC}"
    create_symlinks "$LOCAL_BIN_DIR"
    
    echo -e "${GREEN}Installation complete!${NC}"
    echo -e "${YELLOW}To use the command, add the following to your PATH:${NC}"
    echo "export PATH=\"$LOCAL_BIN_DIR:\$PATH\""
    echo
    echo -e "${GREEN}Then you can use:${NC}"
    echo "vaahai detect-language path/to/file_or_directory"
else
    # System-wide installation
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Error: System-wide installation requires root privileges.${NC}"
        echo -e "${YELLOW}Run with sudo or use --local for a local installation.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Installing vaahai detect-language command system-wide...${NC}"
    create_symlinks "/usr/local/bin"
    
    echo -e "${GREEN}Installation complete!${NC}"
    echo -e "${GREEN}You can now use:${NC}"
    echo "vaahai detect-language path/to/file_or_directory"
fi
