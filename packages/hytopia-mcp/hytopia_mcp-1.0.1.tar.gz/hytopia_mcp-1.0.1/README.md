# HYTOPIA MCP - Knowledge Assistant for HYTOPIA SDK Development

A Model Context Protocol (MCP) server that provides intelligent knowledge assistance for HYTOPIA SDK game development. This MCP helps Claude Code understand the HYTOPIA SDK deeply without generating code, following the MCP philosophy of being a context provider.

## Overview

HYTOPIA MCP is designed to help developers navigate the complex HYTOPIA SDK by providing:
- 🔍 **API Exploration** - Browse and understand SDK classes, methods, and properties
- 📖 **Pattern Analysis** - Learn common patterns and best practices
- 💡 **Concept Explanation** - Understand core HYTOPIA concepts and architecture
- 📚 **Documentation Access** - Search and retrieve SDK documentation
- 🔎 **Unified Search** - Find information across all resources
- 📦 **Example Analysis** - Study SDK examples and their implementations

## Philosophy

This MCP follows the principle: **"Teach Claude Code how to fish, don't give it fish"**

Instead of generating code, it provides:
- Understanding of SDK structure and patterns
- Knowledge about best practices and common pitfalls
- Context about how different parts work together
- Guidance on implementation approaches

## Installation

### Prerequisites

- Python 3.10 or higher
- Claude Code (Terminal version)

### Quick Install (No Download Required)

#### Option 1: Install from PyPI
```bash
# Install the package
pip install hytopia-mcp

# Add to Claude Code
claude mcp add hytopia hytopia-mcp

# Or with custom configuration
claude mcp add hytopia hytopia-mcp \
  -e CACHE_DIR=~/.cache/hytopia-mcp \
  -e SDK_AUTO_UPDATE=true \
  -e DEBUG=false
```

#### Option 2: Install from GitHub
```bash
# Install directly from GitHub
pip install git+https://github.com/AnrokX/hytopia-mcp.git

# Add to Claude Code
claude mcp add hytopia hytopia-mcp
```

#### Option 3: Using pipx (Recommended for isolation)
```bash
# Install pipx if you don't have it
python -m pip install --user pipx
python -m pipx ensurepath

# Install hytopia-mcp
pipx install hytopia-mcp

# Add to Claude Code
claude mcp add hytopia hytopia-mcp
```

### Development Setup (Clone Repository)

1. Clone the repository:
```bash
git clone https://github.com/AnrokX/hytopia-mcp.git
cd hytopia-mcp
```

2. Run the setup script:
```bash
./setup-claude-code.sh
```

Or manually:
```bash
pip install -e .
cp .env.example .env  # Optional: customize settings
```

3. Add to Claude Code:

**Option A: Using Claude CLI (Recommended)**
```bash
# Add the MCP server to Claude Code
claude mcp add hytopia python -m hytopia_mcp.server

# Or with custom Python path
claude mcp add hytopia /usr/bin/python3 -m hytopia_mcp.server

# Or with environment variables
claude mcp add hytopia python -m hytopia_mcp.server \
  -e CACHE_DIR=~/.cache/hytopia-mcp \
  -e SDK_AUTO_UPDATE=true
```

**Option B: Project-specific configuration**
Create `.mcp.json` in your project root:
```json
{
  "mcpServers": {
    "hytopia": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "hytopia_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/hytopia-mcp"
      }
    }
  }
}
```

**Option C: Global configuration**
Edit `~/.claude.json` and add under `mcpServers`:
```json
{
  "mcpServers": {
    "hytopia": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "hytopia_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/hytopia-mcp"
      }
    }
  }
}
```

5. Verify installation:
```bash
# List configured MCP servers
claude mcp list

# Check MCP status in Claude Code
/mcp
```

## Configuration

### Environment Variables

The HYTOPIA MCP can be configured using environment variables. When installed via pip, you can:

1. **Pass variables directly to Claude Code:**
```bash
claude mcp add hytopia hytopia-mcp \
  -e CACHE_DIR=~/.cache/hytopia-mcp \
  -e SDK_AUTO_UPDATE=true \
  -e DEBUG=false
```

2. **Create a global configuration file:**
Create `~/.hytopia-mcp.env`:
```bash
# Cache Configuration
CACHE_DIR=~/.cache/hytopia-mcp
CACHE_MAX_SIZE_MB=500
CACHE_TTL_HOURS=24

# SDK Configuration  
SDK_AUTO_UPDATE=false
SDK_UPDATE_CHECK_INTERVAL_HOURS=6

# Development
DEBUG=false
LOG_LEVEL=info
```

3. **Get help with configuration:**
```bash
# Show setup instructions
hytopia-mcp help

# Check version
hytopia-mcp --version
```

### Available Settings

See `.env.example` for all available configuration options:
- **Cache**: Directory, size limits, TTL
- **SDK Updates**: Auto-update, check intervals
- **Performance**: Search limits, caching behavior
- **Development**: Debug mode, logging

## Available Tools

### API Navigation
- `hytopia_list_modules` - Browse SDK modules by category
- `hytopia_explore_class` - Deep dive into specific classes
- `hytopia_get_methods` - List and filter class methods
- `hytopia_get_method_details` - Get detailed method information
- `hytopia_get_properties` - List class properties
- `hytopia_get_interfaces` - Browse available interfaces
- `hytopia_get_enums` - List enums and their values

### Pattern Analysis
- `hytopia_entity_patterns` - Learn entity implementation patterns
- `hytopia_controller_patterns` - Understand controller patterns
- `hytopia_world_patterns` - World setup and management patterns
- `hytopia_game_patterns` - Common game implementation patterns
- `hytopia_ui_patterns` - UI implementation strategies
- `hytopia_best_practices` - Best practices for various topics
- `hytopia_common_pitfalls` - Avoid common mistakes

### Concept Explanation
- `hytopia_explain_concept` - Understand core concepts (server-authoritative, entity-system, etc.)
- `hytopia_explain_architecture` - Learn about architectural components
- `hytopia_explain_lifecycle` - Understand various lifecycles
- `hytopia_compare_approaches` - Compare implementation approaches

### Example Analysis
- `hytopia_find_example_patterns` - Find examples by pattern
- `hytopia_analyze_example` - Analyze specific examples
- `hytopia_list_examples_by_topic` - Browse examples by category
- `hytopia_get_example_structure` - Understand example organization

### Documentation
- `hytopia_get_guide` - Access specific guides
- `hytopia_search_docs` - Search documentation
- `hytopia_get_tutorial` - Get step-by-step tutorials
- `hytopia_get_api_docs` - API reference documentation
- `hytopia_get_best_practices` - Topic-specific best practices

### Search
- `hytopia_search_all` - Search across all resources
- `hytopia_find_related` - Find related items
- `hytopia_search_by_use_case` - Search by what you want to accomplish

### SDK Management
- `hytopia_check_updates` - Check for SDK updates
- `hytopia_update_sdk` - Update local SDK cache
- `hytopia_get_changelog` - View recent changes
- `hytopia_sdk_status` - Check cache and system status

## Usage Examples

### Getting Started
```
User: How do I create an NPC in HYTOPIA?

Claude will use:
1. hytopia_explain_concept("entity-system")
2. hytopia_entity_patterns("npc")
3. hytopia_find_example_patterns("npc")
4. hytopia_explore_class("ModelEntity")

Then provide a comprehensive explanation of NPC creation patterns.
```

### Understanding Concepts
```
User: Explain server-authoritative architecture

Claude will use:
1. hytopia_explain_concept("server-authoritative")
2. hytopia_find_related("concept", "server-authoritative")
3. hytopia_best_practices("networking")

Then explain the concept with context and implications.
```

### Finding Examples
```
User: Show me physics examples

Claude will use:
1. hytopia_find_example_patterns("physics")
2. hytopia_analyze_example("physics-basic")
3. hytopia_controller_patterns("physics")

Then explain the physics patterns found in examples.
```

## Architecture

```
hytopia-mcp/
├── hytopia_mcp/
│   ├── server.py           # Main MCP server
│   ├── tools/              # Knowledge tools
│   │   ├── api_explorer.py
│   │   ├── pattern_analyzer.py
│   │   ├── concept_explainer.py
│   │   ├── example_analyzer.py
│   │   ├── documentation.py
│   │   ├── search_tools.py
│   │   └── sdk_updater.py
│   ├── resources/          # Static resources
│   │   └── api_resources.py
│   └── utils/              # Helper utilities
│       ├── cache_manager.py
│       └── sdk_analyzer.py
```

## Key Features

### 🧠 Knowledge-First Approach
- Provides understanding, not code generation
- Explains patterns and best practices
- Teaches concepts and architecture

### 🚀 Performance Optimized
- Local caching for fast responses
- Efficient search algorithms
- Minimal network requests

### 📊 Comprehensive Coverage
- Complete API exploration
- Pattern documentation
- Concept explanations
- Example analysis

### 🔄 Always Up-to-Date
- SDK update checking
- Cache refresh capabilities
- Version tracking

## Scripts

### Setup Scripts
- `./setup-claude-code.sh` - Automated setup for Claude Code
- `./run-mcp-server.sh` - Run the MCP server directly (for testing)
- `./uninstall-claude-code.sh` - Remove from Claude Code

### Managing the MCP

```bash
# Check if installed
claude mcp list

# Remove from Claude Code
claude mcp remove hytopia

# Re-add with different settings
claude mcp add hytopia python -m hytopia_mcp.server \
  -e SDK_AUTO_UPDATE=false \
  -e CACHE_DIR=/custom/cache/path
```

## Development

### Running Locally
```bash
# Using the helper script
./run-mcp-server.sh

# Or directly
python -m hytopia_mcp.server
```

### Running Tests
```bash
pytest tests/
```

### Adding New Tools

1. Create new tool file in `hytopia_mcp/tools/`
2. Register tools using `@mcp.tool()` decorator
3. Import in `server.py`
4. Document in README

## Troubleshooting

### MCP Not Appearing in Claude Code
- Run `claude mcp list` to check if configured
- Check MCP status with `/mcp` command in Claude Code
- Ensure Python is in PATH: `which python`
- Try with full Python path: `claude mcp add hytopia /usr/bin/python3 -m hytopia_mcp.server`

### Common Issues

**"Module not found" error**
- Ensure PYTHONPATH includes the project directory
- Use the setup script which handles this automatically
- Or manually: `claude mcp add hytopia python -m hytopia_mcp.server -e PYTHONPATH=/path/to/hytopia-mcp`

**MCP server fails to start**
- Check Python version: `python --version` (needs 3.10+)
- Install dependencies: `pip install -e .`
- Check logs: Run `./run-mcp-server.sh` to see errors

**Permission denied**
- Make scripts executable: `chmod +x *.sh`
- Use `pip install --user -e .` if pip install fails

### Cache Issues
- Clear cache: Delete `~/.cache/hytopia-mcp/`
- Force update: Use `hytopia_update_sdk(force=True)`
- Check cache status: `hytopia_sdk_status`

### Performance Issues
- Disable cache preloading in .env: `CACHE_PRELOAD=false`
- Reduce cache size: `CACHE_MAX_SIZE_MB=200`
- Check memory usage with `hytopia_sdk_status`

## Contributing

1. Fork the repository
2. Create feature branch
3. Follow knowledge-first philosophy
4. Add tests for new features
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- HYTOPIA team for the amazing SDK
- Anthropic for the MCP specification
- FastMCP for the excellent framework

## Support

- GitHub Issues: [Report bugs or request features]
- Documentation: [HYTOPIA Docs](https://docs.hytopia.com)
- Community: [HYTOPIA Discord]

---

Built with ❤️ for the HYTOPIA developer community