"""
API Resources - MCP resource endpoints for HYTOPIA SDK knowledge
"""

from typing import Dict, Any
from fastmcp import FastMCP

class APIResources:
    def __init__(self, mcp: FastMCP, sdk_analyzer):
        self.mcp = mcp
        self.sdk_analyzer = sdk_analyzer
        self._register_resources()
    
    def _register_resources(self):
        @self.mcp.resource("resource://hytopia/api/overview")
        async def api_overview() -> Dict[str, Any]:
            """Overview of HYTOPIA SDK API structure"""
            return {
                "name": "HYTOPIA SDK API Overview",
                "mimeType": "application/json",
                "content": {
                    "description": "HYTOPIA SDK provides a comprehensive API for multiplayer voxel game development",
                    "namespaces": {
                        "core": {
                            "description": "Core game systems",
                            "key_classes": ["World", "GameServer", "WorldManager"]
                        },
                        "entities": {
                            "description": "Entity system for game objects",
                            "key_classes": ["Entity", "ModelEntity", "BlockEntity", "PlayerEntity"]
                        },
                        "physics": {
                            "description": "Physics simulation",
                            "key_classes": ["RigidBody", "Collider", "Simulation"]
                        },
                        "ui": {
                            "description": "User interface system",
                            "key_classes": ["PlayerUI", "SceneUI"]
                        },
                        "networking": {
                            "description": "Multiplayer networking",
                            "key_concepts": ["Server-authoritative", "Automatic sync"]
                        }
                    },
                    "key_principles": [
                        "Server-authoritative architecture",
                        "Event-driven design",
                        "Type-safe TypeScript API",
                        "Automatic state synchronization"
                    ]
                }
            }
        
        @self.mcp.resource("resource://hytopia/patterns/catalog")
        async def patterns_catalog() -> Dict[str, Any]:
            """Catalog of common HYTOPIA development patterns"""
            return {
                "name": "HYTOPIA Patterns Catalog",
                "mimeType": "application/json",
                "content": {
                    "entity_patterns": {
                        "basic_entity": {
                            "description": "Simple entity creation",
                            "use_case": "Static objects, decorations"
                        },
                        "npc_entity": {
                            "description": "Non-player characters with AI",
                            "use_case": "Quest givers, enemies, companions"
                        },
                        "collectible_entity": {
                            "description": "Items players can collect",
                            "use_case": "Coins, power-ups, resources"
                        }
                    },
                    "controller_patterns": {
                        "player_controller": {
                            "description": "Handle player input and movement",
                            "use_case": "Player character control"
                        },
                        "ai_controller": {
                            "description": "AI behavior implementation",
                            "use_case": "Enemy AI, NPC behavior"
                        },
                        "physics_controller": {
                            "description": "Physics-based movement",
                            "use_case": "Vehicles, projectiles"
                        }
                    },
                    "system_patterns": {
                        "game_loop": {
                            "description": "Main game update cycle",
                            "use_case": "Game state management"
                        },
                        "event_system": {
                            "description": "Event-driven architecture",
                            "use_case": "Loose coupling between systems"
                        },
                        "persistence": {
                            "description": "Save/load game data",
                            "use_case": "Player progress, world state"
                        }
                    }
                }
            }
        
        @self.mcp.resource("resource://hytopia/concepts/glossary")
        async def concepts_glossary() -> Dict[str, Any]:
            """Glossary of HYTOPIA concepts"""
            return {
                "name": "HYTOPIA Concepts Glossary",
                "mimeType": "application/json",
                "content": {
                    "server_authoritative": {
                        "definition": "All game logic runs on the server, clients only render",
                        "benefits": ["Prevents cheating", "Ensures consistency", "Simplifies logic"]
                    },
                    "entity": {
                        "definition": "Base class for all game objects",
                        "types": ["ModelEntity", "BlockEntity", "PlayerEntity"]
                    },
                    "chunk": {
                        "definition": "16x16x16 section of voxel terrain",
                        "purpose": "Efficient world management and streaming"
                    },
                    "controller": {
                        "definition": "Handles entity behavior and logic",
                        "separation": "Separates behavior from data"
                    },
                    "rigid_body": {
                        "definition": "Physics body for entities",
                        "types": ["dynamic", "kinematic", "fixed"]
                    },
                    "collider": {
                        "definition": "Defines collision shape",
                        "shapes": ["ball", "block", "capsule", "trimesh"]
                    }
                }
            }
        
        @self.mcp.resource("resource://hytopia/quickstart/checklist")
        async def quickstart_checklist() -> Dict[str, Any]:
            """Quick start checklist for new developers"""
            return {
                "name": "HYTOPIA Quick Start Checklist",
                "mimeType": "application/json",
                "content": {
                    "setup": [
                        "Install Node.js (v18+)",
                        "Run: npm create hytopia@latest",
                        "Choose project template",
                        "Install dependencies"
                    ],
                    "first_steps": [
                        "Understand server-authoritative architecture",
                        "Create basic world with terrain",
                        "Implement player spawning",
                        "Add simple gameplay mechanic"
                    ],
                    "learning_path": [
                        "1. Read getting-started guide",
                        "2. Study entity system",
                        "3. Learn physics basics",
                        "4. Implement UI",
                        "5. Add multiplayer features"
                    ],
                    "common_tasks": {
                        "create_entity": "Extend Entity class and spawn",
                        "handle_input": "Use controller with tickWithPlayerInput",
                        "save_data": "Use player.setPersistedData()",
                        "create_ui": "HTML/CSS with player.ui.load()"
                    }
                }
            }
        
        @self.mcp.resource("resource://hytopia/troubleshooting/common-issues")
        async def common_issues() -> Dict[str, Any]:
            """Common issues and solutions"""
            return {
                "name": "HYTOPIA Common Issues",
                "mimeType": "application/json",
                "content": {
                    "entity_not_appearing": {
                        "symptoms": "Entity created but not visible",
                        "common_causes": [
                            "Forgot to call entity.spawn()",
                            "Entity spawned at wrong position",
                            "Model URI incorrect"
                        ],
                        "solutions": [
                            "Ensure spawn() is called",
                            "Check position coordinates",
                            "Verify model path"
                        ]
                    },
                    "physics_not_working": {
                        "symptoms": "Entity falls through floor or doesn't collide",
                        "common_causes": [
                            "No rigid body attached",
                            "Wrong rigid body type",
                            "Missing colliders"
                        ],
                        "solutions": [
                            "Call setRigidBody() with proper config",
                            "Use 'dynamic' for moving objects",
                            "Add appropriate collider shapes"
                        ]
                    },
                    "ui_not_updating": {
                        "symptoms": "UI shows but doesn't update",
                        "common_causes": [
                            "Not sending data from server",
                            "Wrong message format",
                            "Client not handling messages"
                        ],
                        "solutions": [
                            "Use player.ui.sendData() regularly",
                            "Check message structure",
                            "Implement message handlers in UI"
                        ]
                    },
                    "multiplayer_desync": {
                        "symptoms": "Players see different states",
                        "common_causes": [
                            "Client-side game logic",
                            "Not using server state",
                            "Race conditions"
                        ],
                        "solutions": [
                            "Move all logic to server",
                            "Trust only server state",
                            "Use proper event ordering"
                        ]
                    }
                }
            }
        
        @self.mcp.resource("resource://hytopia/performance/tips")
        async def performance_tips() -> Dict[str, Any]:
            """Performance optimization tips"""
            return {
                "name": "HYTOPIA Performance Tips",
                "mimeType": "application/json",
                "content": {
                    "entity_optimization": [
                        "Use object pooling for frequently spawned entities",
                        "Implement LOD (Level of Detail) system",
                        "Disable updates for distant entities",
                        "Use simple colliders when possible"
                    ],
                    "physics_optimization": [
                        "Limit active rigid bodies",
                        "Use fixed rigid bodies for static objects",
                        "Simplify collision meshes",
                        "Adjust physics tick rate if needed"
                    ],
                    "network_optimization": [
                        "Send only changed data",
                        "Batch updates together",
                        "Use compression for large data",
                        "Implement view distance culling"
                    ],
                    "world_optimization": [
                        "Limit active chunk count",
                        "Use efficient terrain generation",
                        "Cache computed values",
                        "Batch block operations"
                    ],
                    "profiling_tools": [
                        "Use browser DevTools for client performance",
                        "Monitor server CPU and memory",
                        "Track network bandwidth usage",
                        "Identify performance bottlenecks"
                    ]
                }
            }
        
        @self.mcp.resource("resource://hytopia/examples/index")
        async def examples_index() -> Dict[str, Any]:
            """Index of available examples"""
            await self.sdk_analyzer.initialize()
            
            return {
                "name": "HYTOPIA Examples Index",
                "mimeType": "application/json",
                "content": {
                    "categories": {
                        "basic": [
                            "entity-spawn",
                            "player-movement",
                            "world-generation"
                        ],
                        "intermediate": [
                            "custom-ui",
                            "pathfinding",
                            "persistence"
                        ],
                        "advanced": [
                            "ai-agents",
                            "physics-simulation",
                            "procedural-generation"
                        ],
                        "complete_games": [
                            "zombies-fps",
                            "racing-game",
                            "puzzle-platformer"
                        ]
                    },
                    "learning_progression": [
                        "Start with basic examples",
                        "Study intermediate patterns",
                        "Analyze complete games",
                        "Build your own variations"
                    ]
                }
            }