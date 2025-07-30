# Bash shell integration for signed-bin-dir
# Add this to your ~/.bashrc or source it from there

# Function to update PATH with verified bin directories
__signed_bin_dir_update_path() {
    # Only run if we have the sign-bin-dir command available
    if ! command -v sign-bin-dir >/dev/null 2>&1; then
        return
    fi
    
    local current_dir="$(pwd)"
    
    # Use Python to check for verified bin directories and update PATH
    local new_path
    new_path=$(python3 -c "
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.expanduser('~/.local/lib/python*/site-packages'))
try:
    from signed_bin_dir.path_manager import PathManager
    pm = PathManager()
    print(pm.generate_path_string(Path('$current_dir')))
except ImportError:
    print(os.environ.get('PATH', ''))
except Exception:
    print(os.environ.get('PATH', ''))
" 2>/dev/null)
    
    # Update PATH if we got a valid result
    if [[ -n "$new_path" ]]; then
        export PATH="$new_path"
    fi
}

# Function to check if current directory has signed bin directories
__signed_bin_dir_check_current() {
    if ! command -v sign-bin-dir >/dev/null 2>&1; then
        return
    fi
    
    local current_dir="$(pwd)"
    local bin_dirs
    bin_dirs=$(python3 -c "
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.expanduser('~/.local/lib/python*/site-packages'))
try:
    from signed_bin_dir.path_manager import PathManager
    pm = PathManager()
    verified_dirs = pm.get_verified_bin_directories(Path('$current_dir'))
    for d in verified_dirs:
        print(str(d))
except:
    pass
" 2>/dev/null)
    
    if [[ -n "$bin_dirs" ]]; then
        echo "🔐 Signed bin directories added to PATH:"
        while IFS= read -r dir; do
            echo "  $dir"
        done <<< "$bin_dirs"
    fi
}

# Hook into directory changes using PROMPT_COMMAND
__signed_bin_dir_prompt_command() {
    local current_dir="$(pwd)"
    if [[ "$current_dir" != "$__SIGNED_BIN_DIR_LAST_PWD" ]]; then
        __signed_bin_dir_update_path
        __SIGNED_BIN_DIR_LAST_PWD="$current_dir"
    fi
}

# Add our function to PROMPT_COMMAND
if [[ "$PROMPT_COMMAND" != *"__signed_bin_dir_prompt_command"* ]]; then
    PROMPT_COMMAND="__signed_bin_dir_prompt_command${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
fi

# Initialize PATH for current directory when shell starts
__signed_bin_dir_update_path

# Optional: Show signed directories when entering a new directory
# Uncomment the next line if you want notifications
# __signed_bin_dir_check_current

# Convenience function to sign current directory's bin folder
sign-current-bin() {
    if [[ -d "bin" ]]; then
        sign-bin-dir sign bin
        __signed_bin_dir_update_path
        echo "✓ Signed bin directory and updated PATH"
    else
        echo "No bin directory found in current directory"
        return 1
    fi
}

# Convenience function to verify current directory's bin folder
verify-current-bin() {
    if [[ -d "bin" ]]; then
        sign-bin-dir verify bin
    else
        echo "No bin directory found in current directory"
        return 1
    fi
} 