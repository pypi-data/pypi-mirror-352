# Fish shell integration for signed-bin-dir
# Add this to your ~/.config/fish/config.fish or source it from there

# Function to update PATH with verified bin directories
function __signed_bin_dir_update_path
    # Only run if we have the sign-bin-dir command available
    if not command -v sign-bin-dir >/dev/null 2>&1
        return
    end
    
    # Get current directory
    set current_dir (pwd)
    
    # Find all bin directories with signed manifests in current and parent directories
    set verified_dirs
    set check_dir $current_dir
    
    # Check current directory and all parent directories
    while test "$check_dir" != "/"
        if test -d "$check_dir/bin" -a -f "$check_dir/bin/.signed-manifest.json"
            # Verify the signatures using the CLI tool
            if sign-bin-dir verify "$check_dir/bin" >/dev/null 2>&1
                set verified_dirs $verified_dirs "$check_dir/bin"
            end
        end
        set check_dir (dirname "$check_dir")
    end
    
    # Build new PATH with verified directories at the front
    set new_path_parts $verified_dirs
    
    # Add existing PATH parts, excluding any previously managed paths
    for path_part in (string split : $PATH)
        set is_managed false
        for managed_path in $verified_dirs
            if test "$path_part" = "$managed_path"
                set is_managed true
                break
            end
        end
        if not $is_managed
            set new_path_parts $new_path_parts $path_part
        end
    end
    
    # Update PATH
    set -gx PATH (string join : $new_path_parts)
end

# Function to check if current directory has signed bin directories
function __signed_bin_dir_check_current
    if not command -v sign-bin-dir >/dev/null 2>&1
        return
    end
    
    set current_dir (pwd)
    set verified_dirs
    set check_dir $current_dir
    
    # Check current directory and all parent directories
    while test "$check_dir" != "/"
        if test -d "$check_dir/bin" -a -f "$check_dir/bin/.signed-manifest.json"
            # Verify the signatures using the CLI tool
            if sign-bin-dir verify "$check_dir/bin" >/dev/null 2>&1
                set verified_dirs $verified_dirs "$check_dir/bin"
            end
        end
        set check_dir (dirname "$check_dir")
    end
    
    if test (count $verified_dirs) -gt 0
        echo "🔐 Signed bin directories added to PATH:"
        for dir in $verified_dirs
            echo "  $dir"
        end
    end
end

# Hook into directory changes
function __signed_bin_dir_cd_hook --on-variable PWD
    __signed_bin_dir_update_path
end

# Initialize PATH for current directory when shell starts
__signed_bin_dir_update_path

# Optional: Show signed directories when entering a new directory
# Uncomment the next line if you want notifications
# __signed_bin_dir_check_current

# Convenience function to sign current directory's bin folder
function sign-current-bin
    if test -d bin
        sign-bin-dir sign bin
        __signed_bin_dir_update_path
        echo "✓ Signed bin directory and updated PATH"
    else
        echo "No bin directory found in current directory"
        return 1
    end
end

# Convenience function to verify current directory's bin folder
function verify-current-bin
    if test -d bin
        sign-bin-dir verify bin
    else
        echo "No bin directory found in current directory"
        return 1
    end
end 