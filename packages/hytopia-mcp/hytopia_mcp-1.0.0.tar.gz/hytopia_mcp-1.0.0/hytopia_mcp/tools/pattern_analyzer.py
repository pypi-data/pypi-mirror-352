"""
Pattern Analyzer Tools - Analyze and explain HYTOPIA SDK patterns without generating code
"""

from typing import Dict, List, Any, Optional
from fastmcp import FastMCP, Context
import json

class PatternAnalyzerTools:
    def __init__(self, mcp: FastMCP, sdk_analyzer):
        self.mcp = mcp
        self.sdk_analyzer = sdk_analyzer
        self._register_tools()
    
    def _register_tools(self):
        @self.mcp.tool()
        async def hytopia_entity_patterns(
            pattern_type: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain common entity patterns in HYTOPIA.
            Types: basic, npc, collectible, enemy, platform, projectile, vehicle
            Returns pattern structure, lifecycle, and best practices.
            """
            if context:
                await context.info(f"Analyzing {pattern_type} entity pattern")
            
            patterns = {
                "basic": {
                    "description": "Basic entity that extends ModelEntity or BlockEntity",
                    "extends": "ModelEntity or BlockEntity",
                    "required_imports": ["Entity", "ModelEntity/BlockEntity", "World", "Vector3"],
                    "constructor_pattern": {
                        "accepts": "World instance and options object",
                        "must_call": "super(world, options)",
                        "common_options": ["modelUri", "position", "rotation", "scale"]
                    },
                    "lifecycle": [
                        {"method": "constructor", "purpose": "Initialize entity properties"},
                        {"method": "spawn", "purpose": "Add entity to world, setup physics/events"},
                        {"method": "tick", "purpose": "Update logic (if using controller)"},
                        {"method": "despawn", "purpose": "Remove from world, cleanup"}
                    ],
                    "common_patterns": [
                        "Override spawn() to setup physics and event handlers",
                        "Use controllers for behavior logic",
                        "Store custom properties as class members",
                        "Handle cleanup in despawn or event handlers"
                    ],
                    "best_practices": [
                        "Always call super.spawn() when overriding",
                        "Check isSpawned before operations",
                        "Clean up event listeners on despawn",
                        "Use type-safe options interfaces"
                    ],
                    "common_mistakes": [
                        "Forgetting to call super() methods",
                        "Not checking if entity is spawned",
                        "Memory leaks from event handlers",
                        "Modifying position without physics"
                    ]
                },
                "npc": {
                    "description": "Non-player character with interaction capabilities",
                    "extends": "ModelEntity",
                    "required_imports": ["ModelEntity", "PlayerEntity", "SimpleEntityController"],
                    "key_properties": [
                        {"name": "dialogues", "type": "string[]", "purpose": "NPC conversation texts"},
                        {"name": "interactionRange", "type": "number", "purpose": "Distance for interaction"},
                        {"name": "currentState", "type": "string", "purpose": "AI state management"}
                    ],
                    "interaction_pattern": {
                        "detection": "Use collision events or distance checks",
                        "prompt": "Send UI data to nearby players",
                        "response": "Handle player input through UI events",
                        "feedback": "Update NPC state and player UI"
                    },
                    "controller_usage": "Attach SimpleEntityController for movement/behavior",
                    "common_features": [
                        "Dialogue system with multiple responses",
                        "Quest giving/receiving",
                        "Shop/trade interfaces",
                        "Following or patrolling behavior"
                    ],
                    "implementation_tips": [
                        "Use player.ui.sendData() for interaction prompts",
                        "Store dialogue state per player if needed",
                        "Consider using state machines for complex behavior",
                        "Implement interaction cooldowns"
                    ]
                },
                "collectible": {
                    "description": "Items that players can collect",
                    "extends": "ModelEntity or BlockEntity",
                    "physics_setup": "Use kinematic body with sensor collider",
                    "key_patterns": [
                        "Sensor collider for overlap detection",
                        "Visual effects (rotation, floating)",
                        "Collection feedback (sound, particles)",
                        "Respawn logic if needed"
                    ],
                    "collection_flow": [
                        "Detect player collision via sensor",
                        "Validate collection conditions",
                        "Apply collection effects",
                        "Remove or hide entity",
                        "Schedule respawn if applicable"
                    ],
                    "animation_pattern": "Use controller tick for floating/rotation",
                    "data_persistence": "Update player persisted data on collection",
                    "common_types": ["Coins", "Power-ups", "Keys", "Health packs"]
                },
                "enemy": {
                    "description": "Hostile entities with AI behavior",
                    "extends": "ModelEntity",
                    "required_components": [
                        "Health system",
                        "Damage dealing",
                        "AI controller",
                        "Detection system"
                    ],
                    "ai_patterns": {
                        "state_machine": ["idle", "patrol", "chase", "attack", "flee"],
                        "detection": "Raycast or distance-based player detection",
                        "pathfinding": "Use PathfindingEntityController",
                        "combat": "Cooldown-based attack patterns"
                    },
                    "health_pattern": {
                        "storage": "Class property with max health",
                        "damage": "Public method to apply damage",
                        "death": "Despawn with effects/drops"
                    },
                    "optimization_tips": [
                        "Use LOD for distant enemies",
                        "Disable AI when far from players",
                        "Pool enemies instead of creating/destroying",
                        "Batch similar enemies for performance"
                    ]
                },
                "platform": {
                    "description": "Moving platforms for platforming gameplay",
                    "extends": "ModelEntity",
                    "physics": "KinematicPositionRigidBody",
                    "movement_patterns": [
                        "Waypoint-based movement",
                        "Sine wave motion",
                        "Rotating platforms",
                        "Triggered movement"
                    ],
                    "waypoint_system": {
                        "storage": "Array of Vector3 positions",
                        "movement": "Lerp between waypoints",
                        "timing": "Pause at each waypoint",
                        "looping": "Cycle or ping-pong"
                    },
                    "player_interaction": {
                        "sticky_platform": "Parent player to platform",
                        "physics": "Platform carries player automatically",
                        "edge_cases": "Handle player jumping/leaving"
                    }
                },
                "projectile": {
                    "description": "Launched objects with physics",
                    "extends": "ModelEntity",
                    "physics": "DynamicRigidBody with initial velocity",
                    "lifecycle_pattern": [
                        "Spawn with direction/velocity",
                        "Apply physics impulse",
                        "Detect collisions",
                        "Deal damage/effects",
                        "Despawn after hit or timeout"
                    ],
                    "collision_handling": {
                        "entities": "Check owner to avoid self-damage",
                        "terrain": "Explode or bounce",
                        "cleanup": "Always despawn to avoid memory leaks"
                    },
                    "performance": [
                        "Use object pooling for frequent projectiles",
                        "Limit active projectile count",
                        "Simple colliders (sphere/box)",
                        "Timeout to prevent stuck projectiles"
                    ]
                },
                "vehicle": {
                    "description": "Rideable entities with player control",
                    "extends": "ModelEntity", 
                    "physics": "DynamicRigidBody with constraints",
                    "seat_system": {
                        "driver": "Primary control position",
                        "passengers": "Additional seats",
                        "mounting": "Parent player to seat node"
                    },
                    "control_pattern": {
                        "input": "Transfer from player to vehicle",
                        "physics": "Apply forces based on input",
                        "camera": "Adjust player camera for vehicle"
                    },
                    "common_features": [
                        "Speed/acceleration control",
                        "Turning and steering",
                        "Enter/exit interactions",
                        "Damage and health system"
                    ]
                }
            }
            
            if pattern_type not in patterns:
                return {
                    "error": f"Unknown pattern type: {pattern_type}",
                    "available_types": list(patterns.keys()),
                    "usage": "Choose a pattern type to learn about entity implementation patterns"
                }
            
            return patterns[pattern_type]
        
        @self.mcp.tool()
        async def hytopia_controller_patterns(
            controller_type: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain controller patterns in HYTOPIA.
            Types: player, ai, physics, pathfinding, state_machine, simple
            Returns implementation patterns and best practices.
            """
            patterns = {
                "player": {
                    "description": "Controller for player-controlled entities",
                    "extends": "DefaultPlayerEntityController or BaseEntityController",
                    "input_handling": {
                        "method": "tickWithPlayerInput(input, deltaTime)",
                        "input_properties": ["w", "a", "s", "d", "space", "shift", "mouseLeft", "mouseRight"],
                        "mouse_position": "input.mousePosition (Vector2)"
                    },
                    "movement_pattern": {
                        "ground": "Apply velocity based on input direction",
                        "air": "Limited air control",
                        "swimming": "Different physics in water"
                    },
                    "common_features": [
                        "Sprint with shift key",
                        "Jump with space",
                        "Interact with E key",
                        "Attack with mouse buttons"
                    ],
                    "best_practices": [
                        "Normalize diagonal movement",
                        "Apply deltaTime for frame independence",
                        "Check isGrounded for jump",
                        "Handle state transitions smoothly"
                    ]
                },
                "ai": {
                    "description": "AI behavior controller for NPCs/enemies",
                    "extends": "BaseEntityController",
                    "architecture": {
                        "update_method": "tick() called every frame",
                        "decision_making": "State machines or behavior trees",
                        "target_selection": "Find nearest player/objective",
                        "movement": "Calculate direction and apply"
                    },
                    "common_patterns": {
                        "detection": {
                            "methods": ["Distance checks", "Raycasting", "Trigger volumes"],
                            "optimization": "Use spatial partitioning"
                        },
                        "state_management": {
                            "states": ["idle", "patrol", "alert", "combat"],
                            "transitions": "Based on triggers/conditions"
                        },
                        "combat": {
                            "targeting": "Lock onto player",
                            "attack_patterns": "Cooldown-based abilities",
                            "movement": "Strafe, retreat, charge"
                        }
                    },
                    "performance_tips": [
                        "LOD system for AI complexity",
                        "Disable when far from players",
                        "Batch AI updates",
                        "Use simple physics shapes"
                    ]
                },
                "physics": {
                    "description": "Physics-based movement controller",
                    "extends": "BaseEntityController",
                    "force_application": {
                        "methods": ["applyImpulse", "applyForce", "setVelocity"],
                        "timing": "Apply forces in tick()",
                        "coordination": "Combine multiple forces"
                    },
                    "common_behaviors": [
                        "Hover at fixed height",
                        "Magnetic attraction/repulsion", 
                        "Orbital movement",
                        "Spring-like connections"
                    ],
                    "physics_queries": {
                        "raycasting": "Check ground distance",
                        "overlap": "Detect nearby entities",
                        "constraints": "Limit movement axes"
                    }
                },
                "pathfinding": {
                    "description": "Navigation controller using built-in pathfinding",
                    "extends": "PathfindingEntityController",
                    "configuration": {
                        "properties": ["speed", "maxJump", "maxFall"],
                        "methods": ["pathfind()", "abort()"]
                    },
                    "usage_pattern": {
                        "setup": "Set navigation parameters",
                        "pathfind": "Call with target and callbacks",
                        "update": "Automatic movement along path",
                        "completion": "Handle success/failure"
                    },
                    "advanced_features": [
                        "Dynamic obstacle avoidance",
                        "Multi-goal pathfinding",
                        "Path smoothing",
                        "Custom cost functions"
                    ]
                },
                "state_machine": {
                    "description": "State-based behavior controller",
                    "architecture": {
                        "states": "Map of state objects",
                        "transitions": "Condition-based state changes",
                        "updates": "Per-state update logic"
                    },
                    "state_structure": {
                        "enter": "Called when entering state",
                        "update": "Called every tick",
                        "exit": "Called when leaving state"
                    },
                    "implementation_tips": [
                        "Keep states focused and simple",
                        "Use clear transition conditions",
                        "Avoid state explosion",
                        "Consider hierarchical states"
                    ],
                    "common_patterns": [
                        "Combat state machines",
                        "Animation state control",
                        "AI behavior trees",
                        "Game mode phases"
                    ]
                },
                "simple": {
                    "description": "Basic controller for simple behaviors",
                    "extends": "SimpleEntityController",
                    "use_cases": [
                        "Rotating objects",
                        "Simple animations",
                        "Basic movement patterns",
                        "Environmental effects"
                    ],
                    "implementation": {
                        "tick": "Override tick() method",
                        "no_input": "No player input handling",
                        "lightweight": "Minimal overhead"
                    }
                }
            }
            
            if controller_type not in patterns:
                return {
                    "error": f"Unknown controller type: {controller_type}",
                    "available_types": list(patterns.keys())
                }
            
            return patterns[controller_type]
        
        @self.mcp.tool()
        async def hytopia_world_patterns(
            aspect: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain world setup and management patterns.
            Aspects: initialization, terrain, spawning, events, multiplayer, persistence
            """
            patterns = {
                "initialization": {
                    "description": "Setting up a game world",
                    "entry_point": "startServer((world) => { ... })",
                    "initialization_order": [
                        "Register block types",
                        "Generate or load terrain",
                        "Setup game rules",
                        "Initialize systems",
                        "Configure event handlers"
                    ],
                    "world_access": {
                        "managers": ["entityManager", "playerManager", "chatManager", "audioManager"],
                        "terrain": "world.chunkLattice",
                        "events": "world.on(event, handler)"
                    },
                    "best_practices": [
                        "Initialize once, reuse systems",
                        "Setup event handlers early",
                        "Use world instance, not globals",
                        "Clean shutdown handling"
                    ]
                },
                "terrain": {
                    "description": "Terrain generation and modification",
                    "chunk_system": {
                        "size": "16x16x16 blocks per chunk",
                        "coordinates": "Global block coordinates",
                        "lattice": "world.chunkLattice manages chunks"
                    },
                    "generation_patterns": [
                        "Flat world: Simple loops",
                        "Terrain: Perlin noise heightmaps",
                        "Structures: Procedural placement",
                        "Biomes: Region-based generation"
                    ],
                    "modification": {
                        "set_block": "chunkLattice.setBlock(position, blockType)",
                        "get_block": "chunkLattice.getBlock(position)",
                        "bulk_ops": "Batch operations for performance"
                    },
                    "performance": [
                        "Generate in chunks",
                        "Use worker threads if needed",
                        "Cache generated data",
                        "LOD for distant terrain"
                    ]
                },
                "spawning": {
                    "description": "Entity and player spawning patterns",
                    "player_spawning": {
                        "event": "world.on('playerJoin')",
                        "entity": "Create PlayerEntity",
                        "position": "Designated spawn points",
                        "inventory": "Load from persistence"
                    },
                    "entity_spawning": {
                        "creation": "new EntityClass(world, options)",
                        "spawning": "entity.spawn()",
                        "timing": "Immediate or scheduled",
                        "pooling": "Reuse entities for performance"
                    },
                    "spawn_points": {
                        "storage": "Array or map of positions",
                        "selection": "Random, team-based, or sequential",
                        "validation": "Check for obstructions",
                        "respawn": "Handle death/respawn cycle"
                    }
                },
                "events": {
                    "description": "World event handling patterns",
                    "player_events": [
                        {"event": "playerJoin", "use": "Setup new player"},
                        {"event": "playerLeave", "use": "Cleanup and save"},
                        {"event": "playerRespawn", "use": "Handle death"}
                    ],
                    "game_events": [
                        {"event": "tick", "use": "Game update logic"},
                        {"event": "entitySpawn", "use": "Track entities"},
                        {"event": "entityDespawn", "use": "Cleanup"}
                    ],
                    "patterns": {
                        "event_aggregation": "Central event manager",
                        "event_filtering": "Conditional handlers",
                        "event_ordering": "Priority-based handling"
                    },
                    "best_practices": [
                        "Unsubscribe when done",
                        "Avoid heavy computation in handlers",
                        "Use specific events over polling",
                        "Handle errors gracefully"
                    ]
                },
                "multiplayer": {
                    "description": "Multiplayer synchronization patterns",
                    "architecture": "Server-authoritative",
                    "automatic_sync": [
                        "Entity positions/rotations",
                        "Animation states",
                        "Block changes",
                        "Physics state"
                    ],
                    "manual_sync": {
                        "ui_data": "player.ui.sendData()",
                        "chat": "chatManager.sendMessage()",
                        "custom": "Via UI or persistence"
                    },
                    "patterns": [
                        "All logic on server",
                        "Client prediction for movement",
                        "Interpolation for smoothness",
                        "Lag compensation techniques"
                    ],
                    "best_practices": [
                        "Never trust client input",
                        "Validate all actions server-side",
                        "Minimize network traffic",
                        "Handle disconnections gracefully"
                    ]
                },
                "persistence": {
                    "description": "Data persistence patterns",
                    "player_data": {
                        "save": "player.setPersistedData(data)",
                        "load": "player.getPersistedData()",
                        "timing": "On leave or periodically"
                    },
                    "world_data": {
                        "global": "PersistenceManager.setGlobalData()",
                        "chunks": "Custom chunk saving",
                        "entities": "Serialize entity state"
                    },
                    "patterns": [
                        "Incremental saves",
                        "Backup systems",
                        "Migration handling",
                        "Data validation"
                    ]
                }
            }
            
            if aspect not in patterns:
                return {
                    "error": f"Unknown aspect: {aspect}",
                    "available_aspects": list(patterns.keys())
                }
            
            return patterns[aspect]
        
        @self.mcp.tool()
        async def hytopia_game_patterns(
            pattern_type: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain common game implementation patterns.
            Types: game_loop, scoring, teams, rounds, inventory, combat
            """
            patterns = {
                "game_loop": {
                    "description": "Main game loop patterns",
                    "phases": ["waiting", "starting", "playing", "ending"],
                    "state_management": {
                        "storage": "Class properties or world data",
                        "transitions": "Method calls with validation",
                        "broadcasting": "Update all players on change"
                    },
                    "timing_patterns": {
                        "frame_based": "Count ticks (60/second)",
                        "time_based": "Use Date.now() or timers",
                        "event_based": "React to game events"
                    },
                    "update_pattern": {
                        "tick_handler": "world.on('tick')",
                        "rate_limiting": "Update every N ticks",
                        "priority": "Order of system updates"
                    }
                },
                "scoring": {
                    "description": "Score tracking patterns",
                    "storage_options": [
                        "Player persisted data",
                        "In-memory maps",
                        "Custom score manager"
                    ],
                    "update_patterns": {
                        "immediate": "Update on action",
                        "batched": "Queue and process",
                        "validated": "Verify before applying"
                    },
                    "display": {
                        "ui": "Send via player.ui",
                        "chat": "Announce in chat",
                        "world": "3D text or billboards"
                    },
                    "features": [
                        "Leaderboards",
                        "Score multipliers",
                        "Combo systems",
                        "Achievement tracking"
                    ]
                },
                "teams": {
                    "description": "Team-based gameplay patterns",
                    "team_structure": {
                        "storage": "Map<playerId, teamId>",
                        "metadata": "Team names, colors, spawns",
                        "balancing": "Auto-balance algorithms"
                    },
                    "assignment": {
                        "methods": ["Random", "Balanced", "Player choice"],
                        "timing": ["On join", "Round start", "Manual"]
                    },
                    "features": [
                        "Team-only chat",
                        "Friendly fire toggle",
                        "Team objectives",
                        "Shared resources"
                    ],
                    "synchronization": {
                        "visual": "Team colors/models",
                        "ui": "Team-specific HUD",
                        "spawning": "Team spawn points"
                    }
                },
                "rounds": {
                    "description": "Round-based game patterns",
                    "round_lifecycle": [
                        "Waiting for players",
                        "Round starting countdown",
                        "Active gameplay", 
                        "Round ending",
                        "Intermission"
                    ],
                    "state_reset": {
                        "world": "Reset terrain/entities",
                        "players": "Respawn and re-equip",
                        "scores": "Per-round tracking"
                    },
                    "win_conditions": [
                        "Time limit",
                        "Score target",
                        "Last team standing",
                        "Objective completion"
                    ]
                },
                "inventory": {
                    "description": "Inventory system patterns",
                    "data_structure": {
                        "simple": "Array of item IDs",
                        "complex": "Map with quantities",
                        "slotted": "Fixed slot system"
                    },
                    "operations": [
                        "Add/remove items",
                        "Stack management",
                        "Slot swapping",
                        "Capacity checks"
                    ],
                    "persistence": "Store in player data",
                    "ui_sync": {
                        "full_update": "Send entire inventory",
                        "delta_update": "Send changes only",
                        "action_based": "UI requests changes"
                    }
                },
                "combat": {
                    "description": "Combat system patterns",
                    "damage_system": {
                        "calculation": "Base damage + modifiers",
                        "types": "Physical, magical, elemental",
                        "mitigation": "Armor, resistance, shields"
                    },
                    "hit_detection": {
                        "methods": ["Collision-based", "Raycast", "Area of effect"],
                        "validation": "Server-side verification"
                    },
                    "combat_flow": [
                        "Initiate attack",
                        "Validate target",
                        "Calculate damage",
                        "Apply effects",
                        "Update health",
                        "Handle death"
                    ],
                    "features": [
                        "Combo systems",
                        "Critical hits",
                        "Status effects",
                        "Knockback/stun"
                    ]
                }
            }
            
            if pattern_type not in patterns:
                return {
                    "error": f"Unknown pattern type: {pattern_type}",
                    "available_types": list(patterns.keys())
                }
            
            return patterns[pattern_type]
        
        @self.mcp.tool()
        async def hytopia_ui_patterns(
            ui_type: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain UI implementation patterns.
            Types: hud, menu, dialog, inventory, minimap, interaction
            """
            patterns = {
                "hud": {
                    "description": "Heads-up display patterns",
                    "structure": {
                        "html": "Overlay with positioned elements",
                        "css": "Fixed positioning, z-index layers",
                        "js": "Message handler for updates"
                    },
                    "common_elements": [
                        "Health/mana bars",
                        "Score display",
                        "Timer/clock",
                        "Minimap",
                        "Hotbar"
                    ],
                    "update_pattern": {
                        "server": "player.ui.sendData({type, data})",
                        "client": "Handle message, update DOM",
                        "frequency": "On change or periodic"
                    },
                    "best_practices": [
                        "Minimize DOM updates",
                        "Use CSS transforms for smooth animation",
                        "Batch server updates",
                        "Cache unchanged values"
                    ]
                },
                "menu": {
                    "description": "Menu system patterns",
                    "types": ["Main menu", "Pause menu", "Settings", "Shop"],
                    "navigation": {
                        "keyboard": "Arrow keys and enter",
                        "mouse": "Click and hover",
                        "gamepad": "D-pad navigation"
                    },
                    "state_management": {
                        "current_menu": "Track active menu",
                        "history": "Back button support",
                        "data": "Menu-specific state"
                    },
                    "communication": {
                        "open": "Server tells client to show",
                        "input": "Client sends selections",
                        "close": "Either can initiate"
                    }
                },
                "dialog": {
                    "description": "Dialog/conversation UI patterns",
                    "structure": {
                        "speaker": "NPC name/portrait",
                        "text": "Dialog content",
                        "choices": "Player response options"
                    },
                    "flow_control": {
                        "linear": "Next/previous",
                        "branching": "Choice-based",
                        "conditional": "Based on game state"
                    },
                    "features": [
                        "Typewriter effect",
                        "Choice highlighting",
                        "Portrait animations",
                        "Voice indicators"
                    ]
                },
                "inventory": {
                    "description": "Inventory UI patterns",
                    "layouts": [
                        "Grid-based slots",
                        "List view",
                        "Category tabs",
                        "Search/filter"
                    ],
                    "interactions": {
                        "drag_drop": "Move items between slots",
                        "click": "Select and use items",
                        "hover": "Show item details",
                        "shortcuts": "Hotkey assignments"
                    },
                    "sync_pattern": {
                        "full": "Send complete inventory",
                        "delta": "Send only changes",
                        "lazy": "Load on demand"
                    }
                },
                "minimap": {
                    "description": "Minimap implementation patterns",
                    "rendering": {
                        "canvas": "2D canvas drawing",
                        "dom": "HTML elements",
                        "hybrid": "Canvas with DOM overlays"
                    },
                    "data_source": {
                        "static": "Pre-rendered map image",
                        "dynamic": "Real-time world data",
                        "fog": "Explored area tracking"
                    },
                    "features": [
                        "Player position",
                        "Team members",
                        "Objectives",
                        "Terrain types"
                    ]
                },
                "interaction": {
                    "description": "Interaction prompt patterns",
                    "trigger": {
                        "proximity": "Distance-based",
                        "look_at": "Raycast detection",
                        "collision": "Overlap triggers"
                    },
                    "display": {
                        "world_space": "3D prompt above object",
                        "screen_space": "2D overlay",
                        "contextual": "Bottom of screen"
                    },
                    "input_handling": {
                        "key_press": "Single action key",
                        "hold": "Hold to interact",
                        "selection": "Multiple options"
                    }
                }
            }
            
            if ui_type not in patterns:
                return {
                    "error": f"Unknown UI type: {ui_type}",
                    "available_types": list(patterns.keys())
                }
            
            return patterns[ui_type]
        
        @self.mcp.tool()
        async def hytopia_best_practices(
            topic: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get best practices for specific HYTOPIA development topics.
            Topics: performance, networking, architecture, debugging, testing
            """
            practices = {
                "performance": {
                    "entity_optimization": [
                        "Use object pooling for frequently spawned entities",
                        "Implement LOD (Level of Detail) for distant entities",
                        "Disable AI/physics when far from players",
                        "Batch similar operations together",
                        "Use simple colliders over complex meshes"
                    ],
                    "world_optimization": [
                        "Generate terrain in chunks asynchronously",
                        "Use spatial partitioning for entity queries",
                        "Limit active chunk count",
                        "Cache frequently accessed data",
                        "Minimize block updates per tick"
                    ],
                    "network_optimization": [
                        "Send only changed data",
                        "Batch UI updates",
                        "Use compression for large data",
                        "Implement update rate limiting",
                        "Prioritize important updates"
                    ],
                    "code_optimization": [
                        "Avoid creating objects in loops",
                        "Reuse vector/quaternion instances",
                        "Use early returns in conditionals",
                        "Profile before optimizing",
                        "Cache expensive calculations"
                    ]
                },
                "networking": {
                    "architecture": [
                        "All game logic runs on server",
                        "Never trust client input",
                        "Validate all player actions",
                        "Use authoritative server state",
                        "Client is just a renderer"
                    ],
                    "synchronization": [
                        "Automatic for entities/physics",
                        "Manual for custom data via UI",
                        "Use events for state changes",
                        "Implement client prediction carefully",
                        "Handle network latency gracefully"
                    ],
                    "security": [
                        "Validate all inputs server-side",
                        "Rate limit player actions",
                        "Sanitize chat messages",
                        "Check permissions for actions",
                        "Log suspicious behavior"
                    ]
                },
                "architecture": {
                    "code_organization": [
                        "Separate concerns into modules",
                        "Use composition over inheritance",
                        "Keep controllers focused",
                        "Implement systems as managers",
                        "Use events for loose coupling"
                    ],
                    "state_management": [
                        "Centralize game state",
                        "Use immutable updates where possible",
                        "Implement state machines for complex logic",
                        "Separate volatile and persistent state",
                        "Document state dependencies"
                    ],
                    "extensibility": [
                        "Design for modularity",
                        "Use interfaces for contracts",
                        "Implement plugin systems",
                        "Allow configuration without code changes",
                        "Version your save data"
                    ]
                },
                "debugging": {
                    "tools": [
                        "Use console.log strategically",
                        "Implement debug UI overlays",
                        "Add admin commands for testing",
                        "Use Chrome DevTools for UI",
                        "Profile performance bottlenecks"
                    ],
                    "techniques": [
                        "Binary search for bugs",
                        "Reproduce issues consistently",
                        "Use minimal test cases",
                        "Check assumptions with assertions",
                        "Log state transitions"
                    ],
                    "multiplayer_debugging": [
                        "Test with multiple clients",
                        "Simulate network latency",
                        "Log server-side errors",
                        "Implement replay systems",
                        "Use debug visualization"
                    ]
                },
                "testing": {
                    "strategies": [
                        "Test core game logic first",
                        "Automate repetitive tests",
                        "Use multiple test clients",
                        "Test edge cases",
                        "Implement integration tests"
                    ],
                    "areas_to_test": [
                        "Player spawn/despawn",
                        "Combat calculations",
                        "Inventory operations",
                        "State transitions",
                        "Persistence save/load"
                    ],
                    "multiplayer_testing": [
                        "Test with max players",
                        "Simulate disconnections",
                        "Test concurrent actions",
                        "Verify state sync",
                        "Check race conditions"
                    ]
                }
            }
            
            if topic not in practices:
                return {
                    "error": f"Unknown topic: {topic}",
                    "available_topics": list(practices.keys())
                }
            
            return {
                "topic": topic,
                "best_practices": practices[topic],
                "remember": "These are guidelines - adapt to your specific needs"
            }
        
        @self.mcp.tool()
        async def hytopia_common_pitfalls(
            area: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Learn about common mistakes and how to avoid them.
            Areas: entities, physics, networking, performance, ui
            """
            pitfalls = {
                "entities": {
                    "spawning": [
                        {
                            "mistake": "Not calling super() in overridden methods",
                            "consequence": "Entity doesn't initialize properly",
                            "solution": "Always call super() first in spawn(), constructor"
                        },
                        {
                            "mistake": "Modifying position without physics",
                            "consequence": "Desync between visual and physics position",
                            "solution": "Use setPosition() or physics forces"
                        },
                        {
                            "mistake": "Not checking isSpawned before operations",
                            "consequence": "Errors when entity is despawned",
                            "solution": "Guard operations with if (entity.isSpawned)"
                        }
                    ],
                    "lifecycle": [
                        {
                            "mistake": "Memory leaks from event handlers",
                            "consequence": "Performance degradation over time",
                            "solution": "Remove listeners in despawn handler"
                        },
                        {
                            "mistake": "Circular references preventing garbage collection",
                            "consequence": "Memory leaks",
                            "solution": "Clear references on despawn"
                        }
                    ]
                },
                "physics": {
                    "rigidbody": [
                        {
                            "mistake": "Wrong rigid body type for use case",
                            "consequence": "Unexpected physics behavior",
                            "solution": "Use kinematic for controlled movement, dynamic for physics"
                        },
                        {
                            "mistake": "Setting position on dynamic bodies",
                            "consequence": "Teleporting breaks physics",
                            "solution": "Use forces or switch to kinematic temporarily"
                        }
                    ],
                    "collisions": [
                        {
                            "mistake": "Complex mesh colliders for everything",
                            "consequence": "Poor performance",
                            "solution": "Use simple shapes (box, sphere) when possible"
                        },
                        {
                            "mistake": "Not setting collision layers",
                            "consequence": "Everything collides with everything",
                            "solution": "Use collision groups to filter interactions"
                        }
                    ]
                },
                "networking": {
                    "trust": [
                        {
                            "mistake": "Trusting client-sent positions",
                            "consequence": "Cheating/exploitation",
                            "solution": "Only accept input, calculate position server-side"
                        },
                        {
                            "mistake": "Client-side game logic",
                            "consequence": "Desync and cheating",
                            "solution": "All logic on server, client just renders"
                        }
                    ],
                    "performance": [
                        {
                            "mistake": "Sending updates every tick",
                            "consequence": "Network overload",
                            "solution": "Rate limit updates, send only changes"
                        },
                        {
                            "mistake": "Large UI data payloads",
                            "consequence": "Lag and poor performance",
                            "solution": "Send minimal data, cache on client"
                        }
                    ]
                },
                "performance": {
                    "entities": [
                        {
                            "mistake": "Creating/destroying entities frequently",
                            "consequence": "GC pressure and hitches",
                            "solution": "Use object pooling"
                        },
                        {
                            "mistake": "Complex AI for all entities",
                            "consequence": "CPU overload",
                            "solution": "LOD system for AI complexity"
                        }
                    ],
                    "world": [
                        {
                            "mistake": "Updating entire world every tick",
                            "consequence": "Poor performance",
                            "solution": "Update only active areas"
                        },
                        {
                            "mistake": "No spatial partitioning",
                            "consequence": "O(n²) collision checks",
                            "solution": "Use chunks or octrees"
                        }
                    ]
                },
                "ui": {
                    "updates": [
                        {
                            "mistake": "Updating DOM every frame",
                            "consequence": "Poor UI performance",
                            "solution": "Batch updates, use requestAnimationFrame"
                        },
                        {
                            "mistake": "Not caching UI data",
                            "consequence": "Redundant updates",
                            "solution": "Only update when values change"
                        }
                    ],
                    "communication": [
                        {
                            "mistake": "Sending entire UI state repeatedly",
                            "consequence": "Network waste",
                            "solution": "Send deltas or specific updates"
                        },
                        {
                            "mistake": "No input validation on UI actions",
                            "consequence": "Exploits and errors",
                            "solution": "Validate all UI-triggered actions server-side"
                        }
                    ]
                }
            }
            
            if area not in pitfalls:
                return {
                    "error": f"Unknown area: {area}",
                    "available_areas": list(pitfalls.keys())
                }
            
            return {
                "area": area,
                "pitfalls": pitfalls[area],
                "tip": "Learn from these common mistakes to write better code"
            }