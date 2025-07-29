#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    """
    Entry point wrapper that prevents shell glob expansion for flort.
    """
    # Check if running in a bash-like shell
    shell = os.environ.get('SHELL', '')
    
    if 'bash' in shell or 'zsh' in shell or 'sh' in shell:
        # Create a modified command that disables globbing before running flort
        args_quoted = ' '.join(f'"{arg}"' for arg in sys.argv[1:])
        script = f"set -f; python -m flort.__main__ {args_quoted}; set +f"
        
        # Execute the modified command in a new shell
        result = subprocess.run(['bash', '-c', script], check=False)
        sys.exit(result.returncode)
    else:
        # For non-bash shells, just import and run the normal entry point
        from flort.__main__ import main as flort_main
        flort_main()

if __name__ == "__main__":
    main()