#!/usr/bin/env python3
"""
HYTOPIA MCP Server - Main server implementation
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastmcp import FastMCP, Context
from dotenv import load_dotenv

from .config import config

from .tools.api_explorer import APIExplorerTools
from .tools.pattern_analyzer import PatternAnalyzerTools
from .tools.example_analyzer import ExampleAnalyzerTools
from .tools.documentation import DocumentationTools
from .tools.sdk_updater import SDKUpdaterTools
from .tools.search_tools import SearchTools
from .tools.concept_explainer import ConceptExplainerTools
from .resources.api_resources import APIResources
from .utils.cache_manager import CacheManager
from .utils.sdk_analyzer import SDKAnalyzer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file) if config.log_file else logging.NullHandler(),
        logging.StreamHandler(sys.stdout) if config.debug else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("HYTOPIA SDK Assistant 🎮")
mcp.description = """
A knowledge assistant MCP server for HYTOPIA SDK development.
Provides context and understanding about the SDK without generating code.
Helps Claude Code understand patterns, best practices, and API structure.
"""

# Initialize managers
cache_manager = CacheManager()
sdk_analyzer = SDKAnalyzer(cache_manager)

# Initialize tool categories
api_explorer = APIExplorerTools(mcp, sdk_analyzer)
pattern_analyzer = PatternAnalyzerTools(mcp, sdk_analyzer)
example_analyzer = ExampleAnalyzerTools(mcp, sdk_analyzer)
concept_explainer = ConceptExplainerTools(mcp, sdk_analyzer)
documentation = DocumentationTools(mcp, sdk_analyzer)
sdk_updater = SDKUpdaterTools(mcp, cache_manager, sdk_analyzer)
search_tools = SearchTools(mcp, sdk_analyzer)

# Initialize resources
api_resources = APIResources(mcp, sdk_analyzer)

# Root level tools
@mcp.tool()
async def hytopia_overview(context: Context = None) -> Dict[str, Any]:
    """
    Get a comprehensive overview of HYTOPIA SDK capabilities and architecture.
    Use this as a starting point to understand what's available.
    """
    if context:
        await context.info("Generating HYTOPIA SDK overview...")
    
    return {
        "sdk_version": await sdk_analyzer.get_sdk_version(),
        "last_updated": await sdk_analyzer.get_last_update(),
        "architecture": {
            "core_systems": [
                "World Management",
                "Entity System",
                "Physics Engine",
                "Terrain System",
                "Player Management",
                "Audio System",
                "Lighting System",
                "UI System",
                "Chat & Commands",
                "Persistence"
            ],
            "key_concepts": [
                "Server-authoritative architecture",
                "Event-driven design",
                "Type-safe TypeScript API",
                "Modular component system",
                "Extensible base classes"
            ]
        },
        "development_workflow": {
            "setup": "npm create hytopia@latest",
            "run": "npm run dev",
            "test": "Multiplayer testing with multiple browser tabs",
            "deploy": "Deploy to HYTOPIA platform"
        },
        "available_tools": {
            "api_navigation": [
                "hytopia_list_modules",
                "hytopia_explore_class",
                "hytopia_get_methods",
                "hytopia_get_method_details"
            ],
            "pattern_analysis": [
                "hytopia_entity_patterns",
                "hytopia_controller_patterns",
                "hytopia_world_patterns",
                "hytopia_game_patterns"
            ],
            "concept_explanation": [
                "hytopia_explain_concept",
                "hytopia_explain_architecture",
                "hytopia_explain_lifecycle",
                "hytopia_compare_approaches"
            ],
            "examples": [
                "hytopia_find_example_patterns",
                "hytopia_analyze_example",
                "hytopia_list_examples_by_topic"
            ],
            "search": [
                "hytopia_search_all",
                "hytopia_find_related",
                "hytopia_search_by_use_case"
            ]
        },
        "quick_start_tips": [
            "Use 'hytopia_list_modules' to explore API structure",
            "Use 'hytopia_entity_patterns' to understand entity patterns",
            "Use 'hytopia_find_example_patterns' to find relevant examples",
            "Use search tools to find specific functionality"
        ]
    }

@mcp.tool()
async def hytopia_quick_help(topic: str = None, context: Context = None) -> Dict[str, Any]:
    """
    Get quick help on common HYTOPIA development topics.
    Topics: entities, physics, world, player, ui, audio, blocks, networking
    """
    help_topics = {
        "entities": {
            "description": "Game objects in HYTOPIA",
            "key_classes": ["Entity", "BlockEntity", "ModelEntity", "PlayerEntity"],
            "common_tasks": [
                "Creating entities: world.entityManager.spawn()",
                "Moving entities: entity.setPosition()",
                "Entity controllers: entity.setController()",
                "Entity events: entity.on('despawn', handler)"
            ],
            "learn_more": "hytopia_entity_patterns('basic')"
        },
        "physics": {
            "description": "Physics simulation in HYTOPIA",
            "key_classes": ["RigidBody", "Collider", "Simulation"],
            "common_tasks": [
                "Add physics: entity.setRigidBody()",
                "Collision detection: collider.onCollision()",
                "Forces: rigidBody.applyImpulse()",
                "Raycasting: world.simulation.raycast()"
            ],
            "learn_more": "hytopia_find_example_patterns('physics')"
        },
        "world": {
            "description": "Game world management",
            "key_classes": ["World", "WorldManager", "ChunkLattice"],
            "common_tasks": [
                "Access world: startServer((world) => {})",
                "World events: world.on('playerJoin', handler)",
                "Terrain: world.chunkLattice.setBlock()",
                "Multiple worlds: worldManager.createWorld()"
            ],
            "learn_more": "hytopia_world_patterns('initialization')"
        },
        "player": {
            "description": "Player management and input",
            "key_classes": ["Player", "PlayerEntity", "PlayerInput", "PlayerCamera"],
            "common_tasks": [
                "Player events: player.on('join', handler)",
                "Input handling: player.input.mouseLeft",
                "Camera control: player.camera.setMode()",
                "UI interaction: player.ui.load()"
            ],
            "learn_more": "hytopia_controller_patterns('player')"
        },
        "ui": {
            "description": "User interface system",
            "key_classes": ["PlayerUI", "SceneUI"],
            "common_tasks": [
                "Load UI: player.ui.load('ui.html')",
                "Send data: player.ui.sendData()",
                "Scene UI: world.sceneUIManager.spawn()",
                "UI events: player.ui.on('data', handler)"
            ],
            "learn_more": "hytopia_ui_patterns('hud')"
        },
        "audio": {
            "description": "Audio and sound effects",
            "key_classes": ["Audio", "AudioManager"],
            "common_tasks": [
                "Play sound: world.audioManager.play()",
                "3D audio: audio.setPosition()",
                "Looping: audio.loop = true",
                "Volume: audio.setVolume()"
            ],
            "learn_more": "hytopia_find_example_patterns('audio')"
        },
        "blocks": {
            "description": "Voxel terrain system",
            "key_classes": ["Block", "BlockType", "Chunk", "ChunkLattice"],
            "common_tasks": [
                "Place block: world.chunkLattice.setBlock()",
                "Create block type: blockTypeRegistry.registerBlockType()",
                "Get block: world.chunkLattice.getBlock()",
                "Block events: blockType.on('entityCollision', handler)"
            ],
            "learn_more": "hytopia_find_example_patterns('blocks')"
        },
        "networking": {
            "description": "Multiplayer and networking",
            "key_concepts": ["Server-authoritative", "Automatic sync", "Player input"],
            "common_tasks": [
                "All logic runs on server",
                "Entity positions auto-sync",
                "Handle input: controller.tickWithPlayerInput()",
                "Chat: world.chatManager.sendMessage()"
            ],
            "learn_more": "hytopia_world_patterns('multiplayer')"
        }
    }
    
    if not topic:
        return {
            "available_topics": list(help_topics.keys()),
            "usage": "Specify a topic to get detailed help",
            "example": "hytopia_quick_help('entities')"
        }
    
    topic = topic.lower()
    if topic not in help_topics:
        return {
            "error": f"Unknown topic: {topic}",
            "available_topics": list(help_topics.keys())
        }
    
    return help_topics[topic]

@mcp.prompt()
def hytopia_starter_prompt() -> str:
    """
    Prompt template for starting a new HYTOPIA game project
    """
    return """I'm starting a new HYTOPIA game project. Please help me:

1. Set up the initial project structure
2. Create a basic game world with terrain
3. Add a player with default controls
4. Implement a simple game mechanic

Game concept: [Describe your game idea here]

Please use the HYTOPIA MCP tools to:
- Understand the relevant patterns and best practices
- Find relevant examples
- Provide implementation guidance"""

@mcp.prompt()
def hytopia_feature_prompt() -> str:
    """
    Prompt template for implementing a specific game feature
    """
    return """I need to implement the following feature in my HYTOPIA game:

Feature: [Describe the feature]
Current setup: [Describe your current game setup]

Please help me:
1. Find relevant API methods and classes
2. Look for similar examples in the SDK examples
3. Understand the implementation patterns
4. Handle any edge cases

Use the HYTOPIA MCP tools to provide a complete solution."""

@mcp.prompt()
def hytopia_debug_prompt() -> str:
    """
    Prompt template for debugging HYTOPIA game issues
    """
    return """I'm experiencing an issue in my HYTOPIA game:

Issue: [Describe the problem]
Expected behavior: [What should happen]
Actual behavior: [What actually happens]
Relevant code: [Paste your code]

Please help me:
1. Identify the root cause
2. Find the correct API usage
3. Provide a working solution
4. Suggest best practices

Use the HYTOPIA MCP tools to investigate and solve this issue."""

def create_server():
    """Create and return the MCP server instance"""
    return mcp

def main():
    """Main entry point"""
    import asyncio
    
    logger.info("Starting HYTOPIA MCP Server...")
    logger.debug(f"Configuration: {config.to_dict()}")
    
    # Check for updates on startup if enabled
    if config.sdk_auto_update:
        async def startup():
            try:
                logger.info("Checking for SDK updates...")
                updater = SDKUpdaterTools(mcp, cache_manager, sdk_analyzer)
                update_result = await updater._check_and_update()
                if update_result.get("updated"):
                    logger.info(f"SDK updated to version {update_result['new_version']}")
                    print(f"✅ HYTOPIA SDK updated to version {update_result['new_version']}")
                else:
                    logger.info(f"SDK is up to date (version {update_result.get('current_version', 'unknown')})")
                    print(f"✅ HYTOPIA SDK is up to date (version {update_result.get('current_version', 'unknown')})")
            except Exception as e:
                logger.error(f"Failed to check for SDK updates: {e}")
                print(f"⚠️  Failed to check for SDK updates: {e}")
        
        # Run startup task
        asyncio.run(startup())
    else:
        logger.info("Auto-update is disabled")
        print("ℹ️  Auto-update is disabled. Use 'hytopia_check_updates' to check manually.")
    
    # Preload cache if enabled
    if config.cache_preload:
        async def preload():
            try:
                logger.info("Preloading SDK cache...")
                await sdk_analyzer.initialize()
                logger.info("SDK cache preloaded successfully")
            except Exception as e:
                logger.error(f"Failed to preload cache: {e}")
        
        asyncio.run(preload())
    
    # Start server
    print("🎮 Starting HYTOPIA MCP Server...")
    print("📚 Use 'hytopia_overview' to get started")
    print("🔍 Use 'hytopia_quick_help' for topic-specific help")
    print(f"⚙️  Cache: {'enabled' if config.enable_caching else 'disabled'}")
    print(f"📁 Cache directory: {config.cache_dir}")
    
    mcp.run()

if __name__ == "__main__":
    main()