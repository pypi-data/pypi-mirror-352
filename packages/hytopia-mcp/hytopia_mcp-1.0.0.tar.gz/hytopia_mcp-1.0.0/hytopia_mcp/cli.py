#!/usr/bin/env python3
"""
CLI wrapper for HYTOPIA MCP Server
This allows the package to be run as 'hytopia-mcp' when installed
"""

import sys
import os
from pathlib import Path

def print_setup_instructions():
    """Print setup instructions for Claude Code"""
    print("""
🎮 HYTOPIA MCP Server
====================

To use with Claude Code:

1. Add to Claude Code:
   claude mcp add hytopia hytopia-mcp

2. With custom configuration:
   claude mcp add hytopia hytopia-mcp \\
     -e CACHE_DIR=~/.cache/hytopia-mcp \\
     -e SDK_AUTO_UPDATE=true

3. Verify installation:
   claude mcp list

4. In Claude Code, check status:
   /mcp

Available environment variables:
- CACHE_DIR: Cache directory (default: ~/.cache/hytopia-mcp)
- SDK_AUTO_UPDATE: Auto-update SDK on startup (default: false)
- DEBUG: Enable debug logging (default: false)
- CACHE_MAX_SIZE_MB: Maximum cache size (default: 500)

For more options, see: https://github.com/hytopia/hytopia-mcp
""")

def find_env_example():
    """Find .env.example file in the package"""
    # Try to find in package data
    import pkg_resources
    try:
        return pkg_resources.resource_filename('hytopia_mcp', '../.env.example')
    except:
        pass
    
    # Try relative to this file
    potential_paths = [
        Path(__file__).parent.parent / '.env.example',
        Path(__file__).parent / '.env.example',
    ]
    
    for path in potential_paths:
        if path.exists():
            return str(path)
    
    return None

def setup_env():
    """Set up environment from .env file if it exists"""
    from dotenv import load_dotenv
    
    # Load from current directory .env
    if Path('.env').exists():
        load_dotenv('.env')
        return
    
    # Load from user's .env if exists
    user_env = Path.home() / '.hytopia-mcp.env'
    if user_env.exists():
        load_dotenv(user_env)
        return
    
    # Create user env from example if doesn't exist
    if not user_env.exists():
        example_path = find_env_example()
        if example_path and Path(example_path).exists():
            print(f"Creating default configuration at {user_env}")
            user_env.write_text(Path(example_path).read_text())
            load_dotenv(user_env)

def main():
    """Main entry point"""
    # Handle help/setup commands
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help', 'setup']:
            print_setup_instructions()
            return 0
        elif sys.argv[1] == '--version':
            from . import __version__
            print(f"hytopia-mcp version {__version__}")
            return 0
    
    # Set up environment
    setup_env()
    
    # Import and run the server
    from .server import main as server_main
    return server_main()

if __name__ == "__main__":
    sys.exit(main())