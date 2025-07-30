"""
Concept Explainer Tools - Explain HYTOPIA concepts and architecture
"""

from typing import Dict, List, Any, Optional
from fastmcp import FastMCP, Context

class ConceptExplainerTools:
    def __init__(self, mcp: FastMCP, sdk_analyzer):
        self.mcp = mcp
        self.sdk_analyzer = sdk_analyzer
        self._register_tools()
    
    def _register_tools(self):
        @self.mcp.tool()
        async def hytopia_explain_concept(
            concept: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain core HYTOPIA concepts in detail.
            Concepts: server-authoritative, entity-system, event-driven, physics, 
                     networking, persistence, chunk-system, multiplayer
            """
            if context:
                await context.info(f"Explaining concept: {concept}")
            
            concepts = {
                "server-authoritative": {
                    "definition": "All game logic runs exclusively on the server, with clients acting only as renderers",
                    "why_important": [
                        "Prevents cheating by eliminating client-side game logic",
                        "Ensures consistency across all players",
                        "Simplifies multiplayer synchronization",
                        "Centralizes game state management"
                    ],
                    "how_it_works": [
                        "Server processes all game logic and physics",
                        "Clients send only input (keyboard, mouse)",
                        "Server validates all actions before applying",
                        "Server broadcasts state changes to clients",
                        "Clients render based on server state"
                    ],
                    "implications": [
                        "Network latency affects responsiveness",
                        "Client prediction may be needed for smooth movement",
                        "Server performance is critical",
                        "All validation must be server-side"
                    ],
                    "examples": [
                        "Player movement: Client sends WASD input, server calculates position",
                        "Combat: Client clicks to attack, server validates and applies damage",
                        "Building: Client requests block placement, server checks and places"
                    ]
                },
                "entity-system": {
                    "definition": "Game objects are represented as entities with components and behaviors",
                    "core_classes": {
                        "Entity": "Base class for all game objects",
                        "ModelEntity": "3D model-based entities",
                        "BlockEntity": "Voxel-based entities",
                        "PlayerEntity": "Special entity for players"
                    },
                    "lifecycle": [
                        "Creation: new Entity(world, options)",
                        "Configuration: Set properties, attach controllers",
                        "Spawning: entity.spawn() adds to world",
                        "Updates: Controllers handle per-frame logic",
                        "Despawning: entity.despawn() removes from world"
                    ],
                    "controllers": {
                        "purpose": "Separate behavior from data",
                        "types": ["Player input", "AI", "Physics", "Animation"],
                        "attachment": "entity.setController(controller)"
                    },
                    "best_practices": [
                        "Keep entities focused on single purpose",
                        "Use composition over inheritance",
                        "Controllers handle behavior, entities hold state",
                        "Clean up properly on despawn"
                    ]
                },
                "event-driven": {
                    "definition": "Components communicate through events rather than direct coupling",
                    "benefits": [
                        "Loose coupling between systems",
                        "Easy to extend functionality",
                        "Clear data flow",
                        "Testable components"
                    ],
                    "event_sources": {
                        "World": ["playerJoin", "playerLeave", "tick"],
                        "Entity": ["spawn", "despawn", "collision"],
                        "Player": ["join", "leave", "death", "respawn"],
                        "Block": ["place", "break", "interaction"]
                    },
                    "usage_pattern": [
                        "Subscribe: object.on('event', handler)",
                        "Emit: object.emit('event', data)",
                        "Unsubscribe: object.off('event', handler)",
                        "One-time: object.once('event', handler)"
                    ],
                    "best_practices": [
                        "Always unsubscribe when done",
                        "Keep handlers focused",
                        "Avoid heavy computation in handlers",
                        "Use specific events over generic ones"
                    ]
                },
                "physics": {
                    "definition": "Built-in physics simulation for realistic movement and collisions",
                    "rigid_bodies": {
                        "dynamic": "Affected by forces and gravity",
                        "kinematic_position": "Controlled movement, affects others",
                        "kinematic_velocity": "Velocity-based movement",
                        "fixed": "Static, immovable objects"
                    },
                    "colliders": {
                        "shapes": ["ball", "block", "capsule", "trimesh"],
                        "properties": ["mass", "friction", "bounciness"],
                        "sensors": "Detect overlaps without physical response"
                    },
                    "forces": [
                        "Gravity: Automatic downward force",
                        "Impulses: Instant velocity changes",
                        "Forces: Continuous acceleration",
                        "Constraints: Limit movement axes"
                    ],
                    "collision_detection": {
                        "events": "entity.on('collision', handler)",
                        "filtering": "Collision groups and masks",
                        "callbacks": "Custom collision responses"
                    }
                },
                "networking": {
                    "definition": "Automatic synchronization of game state across clients",
                    "automatic_sync": [
                        "Entity positions and rotations",
                        "Animation states",
                        "Block changes",
                        "Physics state"
                    ],
                    "manual_sync": {
                        "ui_data": "player.ui.sendData() for custom data",
                        "chat": "chatManager for text messages",
                        "persistence": "Player/world data saving"
                    },
                    "optimization": [
                        "Delta compression for changes only",
                        "Priority-based updates",
                        "View distance culling",
                        "Update rate limiting"
                    ],
                    "security": [
                        "Never trust client data",
                        "Validate all inputs server-side",
                        "Rate limit actions",
                        "Sanitize user content"
                    ]
                },
                "persistence": {
                    "definition": "System for saving and loading game data",
                    "player_data": {
                        "save": "player.setPersistedData(data)",
                        "load": "player.getPersistedData()",
                        "automatic": "Saved on disconnect",
                        "schema": "Define your data structure"
                    },
                    "world_data": {
                        "global": "PersistenceManager.setGlobalData()",
                        "retrieval": "PersistenceManager.getGlobalData()",
                        "use_cases": ["Leaderboards", "World state", "Shared progress"]
                    },
                    "best_practices": [
                        "Version your data schemas",
                        "Handle migration between versions",
                        "Save incrementally, not all at once",
                        "Validate loaded data"
                    ]
                },
                "chunk-system": {
                    "definition": "World divided into 16x16x16 voxel chunks for efficient management",
                    "structure": {
                        "chunk_size": "16 blocks in each dimension",
                        "coordinates": "Global block positions",
                        "lattice": "ChunkLattice manages all chunks"
                    },
                    "benefits": [
                        "Efficient memory usage",
                        "Streamable worlds",
                        "Parallel processing",
                        "Localized updates"
                    ],
                    "operations": {
                        "setBlock": "Place/modify single block",
                        "getBlock": "Query block at position",
                        "bulk": "Modify multiple blocks efficiently"
                    },
                    "optimization": [
                        "Only active chunks are simulated",
                        "Chunk loading/unloading",
                        "Level of detail for distant chunks",
                        "Batch block updates"
                    ]
                },
                "multiplayer": {
                    "definition": "Built-in support for multiple concurrent players",
                    "player_management": {
                        "connection": "Automatic player creation on join",
                        "disconnection": "Graceful handling and cleanup",
                        "reconnection": "Resume from saved state"
                    },
                    "synchronization": {
                        "automatic": "Positions, animations, world changes",
                        "custom": "UI data, game-specific state",
                        "conflicts": "Server state is authoritative"
                    },
                    "scalability": [
                        "Player count limits",
                        "World size considerations",
                        "Performance optimization",
                        "Instance management"
                    ],
                    "features": [
                        "Built-in chat system",
                        "Player identification",
                        "Permission systems",
                        "Team/group support"
                    ]
                }
            }
            
            concept_lower = concept.lower().replace("_", "-")
            if concept_lower not in concepts:
                return {
                    "error": f"Unknown concept: {concept}",
                    "available_concepts": list(concepts.keys()),
                    "suggestion": "Try 'server-authoritative' or 'entity-system'"
                }
            
            return {
                "concept": concept,
                "explanation": concepts[concept_lower],
                "related_concepts": self._get_related_concepts(concept_lower)
            }
        
        @self.mcp.tool()
        async def hytopia_explain_architecture(
            component: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain HYTOPIA architectural components and their relationships.
            Components: world-hierarchy, manager-pattern, event-flow, 
                       entity-controller, client-server
            """
            architectures = {
                "world-hierarchy": {
                    "description": "Hierarchical organization of game objects and systems",
                    "structure": {
                        "GameServer": {
                            "role": "Top-level server instance",
                            "contains": ["WorldManager", "PlayerManager", "ModelRegistry"]
                        },
                        "WorldManager": {
                            "role": "Manages multiple world instances",
                            "operations": ["Create worlds", "Switch worlds", "World lifecycle"]
                        },
                        "World": {
                            "role": "Individual game world instance",
                            "contains": [
                                "EntityManager: All entities",
                                "ChunkLattice: Terrain",
                                "AudioManager: Sounds",
                                "LightManager: Lighting",
                                "SceneUIManager: 3D UI"
                            ]
                        }
                    },
                    "access_pattern": [
                        "Server provides world in startServer()",
                        "World gives access to managers",
                        "Managers handle specific domains"
                    ]
                },
                "manager-pattern": {
                    "description": "Centralized management of game objects by type",
                    "benefits": [
                        "Single point of access",
                        "Efficient queries and updates",
                        "Lifecycle management",
                        "Performance optimization"
                    ],
                    "managers": {
                        "EntityManager": {
                            "purpose": "Manage all entities",
                            "methods": ["spawn", "despawn", "getById", "getByTag"]
                        },
                        "PlayerManager": {
                            "purpose": "Track connected players",
                            "methods": ["getConnectedPlayers", "getByUsername"]
                        },
                        "AudioManager": {
                            "purpose": "Handle game audio",
                            "methods": ["play", "stop", "setVolume"]
                        },
                        "BlockTypeRegistry": {
                            "purpose": "Define block types",
                            "methods": ["registerBlockType", "getBlockType"]
                        }
                    },
                    "pattern": [
                        "Manager holds collection of objects",
                        "Provides CRUD operations",
                        "Handles object lifecycle",
                        "Optimizes queries and updates"
                    ]
                },
                "event-flow": {
                    "description": "How events propagate through the system",
                    "flow_types": {
                        "bottom-up": "Entity → World → GameServer",
                        "top-down": "GameServer → World → Entities",
                        "lateral": "Entity → Entity (via World)"
                    },
                    "event_bubbling": [
                        "Entity emits local event",
                        "World can listen and re-emit",
                        "Global handlers can process"
                    ],
                    "common_flows": {
                        "player_action": [
                            "Input received by server",
                            "Validated by game logic",
                            "Applied to player entity",
                            "State change broadcast"
                        ],
                        "entity_interaction": [
                            "Collision detected",
                            "Event emitted",
                            "Handlers process",
                            "Effects applied"
                        ]
                    }
                },
                "entity-controller": {
                    "description": "Separation of data (Entity) and behavior (Controller)",
                    "benefits": [
                        "Reusable behaviors",
                        "Hot-swappable logic",
                        "Clean separation of concerns",
                        "Testable components"
                    ],
                    "relationship": {
                        "entity": "Holds state and properties",
                        "controller": "Implements behavior logic",
                        "binding": "entity.setController(controller)"
                    },
                    "controller_types": {
                        "BaseEntityController": "Abstract base class",
                        "DefaultPlayerEntityController": "Player movement/input",
                        "PathfindingEntityController": "AI navigation",
                        "SimpleEntityController": "Basic behaviors"
                    },
                    "lifecycle": [
                        "Controller created",
                        "Attached to entity",
                        "tick() called each frame",
                        "Detached on entity despawn"
                    ]
                },
                "client-server": {
                    "description": "Communication architecture between game client and server",
                    "protocol": "WebSocket for real-time bidirectional communication",
                    "data_flow": {
                        "client_to_server": [
                            "Player input (WASD, mouse)",
                            "UI interactions",
                            "Chat messages"
                        ],
                        "server_to_client": [
                            "Entity updates",
                            "World changes",
                            "UI data",
                            "Audio triggers"
                        ]
                    },
                    "synchronization": {
                        "snapshot": "Full world state periodically",
                        "delta": "Only changes since last update",
                        "priority": "Important updates first"
                    },
                    "optimization": [
                        "Compression of data",
                        "Batching of updates",
                        "View distance culling",
                        "Update rate throttling"
                    ]
                }
            }
            
            component_lower = component.lower().replace("_", "-")
            if component_lower not in architectures:
                return {
                    "error": f"Unknown component: {component}",
                    "available_components": list(architectures.keys())
                }
            
            return {
                "component": component,
                "architecture": architectures[component_lower],
                "diagrams": self._get_architecture_diagrams(component_lower)
            }
        
        @self.mcp.tool()
        async def hytopia_explain_lifecycle(
            lifecycle_type: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explain various lifecycles in HYTOPIA.
            Types: entity, player, world, game-session, chunk
            """
            lifecycles = {
                "entity": {
                    "description": "Complete lifecycle of an entity from creation to destruction",
                    "phases": [
                        {
                            "phase": "Construction",
                            "description": "Entity object created in memory",
                            "code": "const entity = new MyEntity(world, options)",
                            "state": "Exists but not in world"
                        },
                        {
                            "phase": "Configuration",
                            "description": "Set up properties and components",
                            "code": "entity.setController(controller)",
                            "state": "Configured but not active"
                        },
                        {
                            "phase": "Spawning",
                            "description": "Add entity to world",
                            "code": "entity.spawn()",
                            "state": "Active in world, events firing"
                        },
                        {
                            "phase": "Active",
                            "description": "Entity updating each tick",
                            "code": "controller.tick() called",
                            "state": "Fully functional"
                        },
                        {
                            "phase": "Despawning",
                            "description": "Remove from world",
                            "code": "entity.despawn()",
                            "state": "Removed but object exists"
                        },
                        {
                            "phase": "Cleanup",
                            "description": "Garbage collection",
                            "code": "// Automatic when no references",
                            "state": "Memory freed"
                        }
                    ],
                    "events": {
                        "spawn": "Fired when entity enters world",
                        "despawn": "Fired when entity leaves world",
                        "tick": "Fired every frame while active"
                    },
                    "best_practices": [
                        "Always clean up event listeners",
                        "Clear references to prevent memory leaks",
                        "Use object pooling for frequent spawn/despawn"
                    ]
                },
                "player": {
                    "description": "Player lifecycle from connection to disconnection",
                    "phases": [
                        {
                            "phase": "Connection",
                            "description": "Player connects to server",
                            "events": ["playerConnect in PlayerManager"],
                            "automatic": "Player object created"
                        },
                        {
                            "phase": "World Join",
                            "description": "Player joins a world",
                            "events": ["playerJoin in World"],
                            "setup": "Create PlayerEntity, load data"
                        },
                        {
                            "phase": "Active Play",
                            "description": "Player interacting with game",
                            "continuous": "Input processing, state updates",
                            "sync": "Automatic position/state sync"
                        },
                        {
                            "phase": "World Leave",
                            "description": "Player leaves world",
                            "events": ["playerLeave in World"],
                            "cleanup": "Save state, despawn entity"
                        },
                        {
                            "phase": "Disconnection",
                            "description": "Player disconnects from server",
                            "events": ["playerDisconnect in PlayerManager"],
                            "persist": "Final data save"
                        }
                    ],
                    "data_persistence": {
                        "automatic": "On disconnect and periodically",
                        "manual": "player.setPersistedData()",
                        "loading": "On world join"
                    }
                },
                "world": {
                    "description": "World lifecycle from creation to cleanup",
                    "phases": [
                        {
                            "phase": "Creation",
                            "description": "World instance created",
                            "code": "worldManager.createWorld(options)",
                            "initialization": "Managers and systems setup"
                        },
                        {
                            "phase": "Setup",
                            "description": "Initialize world content",
                            "tasks": ["Generate terrain", "Place entities", "Configure rules"],
                            "customization": "Game-specific setup"
                        },
                        {
                            "phase": "Active",
                            "description": "World running with players",
                            "continuous": ["Physics simulation", "Entity updates", "Event processing"],
                            "management": "Player joins/leaves"
                        },
                        {
                            "phase": "Shutdown",
                            "description": "World closing",
                            "tasks": ["Save state", "Disconnect players", "Clean up resources"],
                            "graceful": "Allow time for cleanup"
                        }
                    ],
                    "persistence": {
                        "world_state": "Custom implementation",
                        "terrain": "Chunk-based saving",
                        "entities": "Serialize important entities"
                    }
                },
                "game-session": {
                    "description": "Game round or match lifecycle",
                    "phases": [
                        {
                            "phase": "Lobby",
                            "description": "Waiting for players",
                            "features": ["Player ready states", "Team selection", "Map voting"],
                            "transition": "Minimum players reached"
                        },
                        {
                            "phase": "Starting",
                            "description": "Game initialization",
                            "tasks": ["Reset world state", "Spawn players", "Start countdown"],
                            "duration": "Usually 5-10 seconds"
                        },
                        {
                            "phase": "Playing",
                            "description": "Active gameplay",
                            "monitoring": ["Win conditions", "Time limits", "Score tracking"],
                            "dynamic": "Events and objectives"
                        },
                        {
                            "phase": "Ending",
                            "description": "Game conclusion",
                            "tasks": ["Determine winners", "Show results", "Award rewards"],
                            "transition": "Back to lobby or new game"
                        }
                    ],
                    "state_management": {
                        "storage": "In-memory or persisted",
                        "broadcast": "Update all players",
                        "validation": "Server-authoritative"
                    }
                },
                "chunk": {
                    "description": "Terrain chunk lifecycle",
                    "phases": [
                        {
                            "phase": "Generation",
                            "description": "Chunk created or loaded",
                            "trigger": "Player proximity or world generation",
                            "process": "Procedural or from save"
                        },
                        {
                            "phase": "Active",
                            "description": "Chunk in use",
                            "updates": "Block changes, entity interactions",
                            "optimization": "Only near players"
                        },
                        {
                            "phase": "Inactive",
                            "description": "No players nearby",
                            "behavior": "Pause updates, keep in memory",
                            "threshold": "Distance-based"
                        },
                        {
                            "phase": "Unloading",
                            "description": "Remove from memory",
                            "trigger": "Memory pressure or distance",
                            "save": "Persist changes if any"
                        }
                    ],
                    "optimization": {
                        "loading": "Predictive based on movement",
                        "caching": "Keep frequently used chunks",
                        "compression": "For storage and network"
                    }
                }
            }
            
            lifecycle_lower = lifecycle_type.lower().replace("_", "-")
            if lifecycle_lower not in lifecycles:
                return {
                    "error": f"Unknown lifecycle: {lifecycle_type}",
                    "available_lifecycles": list(lifecycles.keys())
                }
            
            return {
                "lifecycle_type": lifecycle_type,
                "details": lifecycles[lifecycle_lower],
                "common_patterns": self._get_lifecycle_patterns(lifecycle_lower)
            }
        
        @self.mcp.tool()
        async def hytopia_compare_approaches(
            topic: str,
            approaches: List[str],
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Compare different approaches to implementing features.
            Topics: movement, collision, ai, persistence, ui, networking
            """
            if len(approaches) < 2:
                return {
                    "error": "Please provide at least 2 approaches to compare",
                    "example": "approaches=['physics-based', 'direct-position']"
                }
            
            comparisons = {
                "movement": {
                    "physics-based": {
                        "description": "Use rigid body physics for movement",
                        "pros": [
                            "Realistic physics interactions",
                            "Handles collisions automatically",
                            "Works with forces and gravity"
                        ],
                        "cons": [
                            "Less precise control",
                            "Can be unpredictable",
                            "Performance overhead"
                        ],
                        "use_when": [
                            "Realistic physics needed",
                            "Environmental interactions important",
                            "Player expectations align with physics"
                        ],
                        "example": "rigidBody.applyImpulse(direction)"
                    },
                    "direct-position": {
                        "description": "Directly set entity position",
                        "pros": [
                            "Precise control",
                            "Predictable behavior",
                            "Better performance"
                        ],
                        "cons": [
                            "Must handle collisions manually",
                            "Less realistic",
                            "No physics interactions"
                        ],
                        "use_when": [
                            "Precise movement needed",
                            "Performance is critical",
                            "Simple collision detection sufficient"
                        ],
                        "example": "entity.setPosition(newPosition)"
                    },
                    "controller-based": {
                        "description": "Use built-in controller classes",
                        "pros": [
                            "Handles common patterns",
                            "Integrated with input system",
                            "Includes features like jumping"
                        ],
                        "cons": [
                            "Less flexibility",
                            "May not fit all games",
                            "Customization limitations"
                        ],
                        "use_when": [
                            "Standard movement patterns work",
                            "Quick implementation needed",
                            "Don't need unique mechanics"
                        ],
                        "example": "entity.setController(new DefaultPlayerEntityController())"
                    }
                },
                "collision": {
                    "physics-colliders": {
                        "description": "Use physics engine collision detection",
                        "pros": [
                            "Accurate collision detection",
                            "Handles complex shapes",
                            "Continuous collision detection"
                        ],
                        "cons": [
                            "Performance cost",
                            "Setup complexity",
                            "Physics knowledge required"
                        ],
                        "use_when": [
                            "Complex collision shapes",
                            "Physics-based gameplay",
                            "High accuracy needed"
                        ]
                    },
                    "distance-checks": {
                        "description": "Simple distance-based detection",
                        "pros": [
                            "Very fast",
                            "Simple to implement",
                            "Predictable"
                        ],
                        "cons": [
                            "Only works for spheres",
                            "Not accurate for complex shapes",
                            "No collision response"
                        ],
                        "use_when": [
                            "Simple circular/spherical objects",
                            "Performance is critical",
                            "Approximate detection sufficient"
                        ]
                    },
                    "raycast-detection": {
                        "description": "Use raycasting for line-of-sight or projectiles",
                        "pros": [
                            "Perfect for projectiles",
                            "Good for vision checks",
                            "Precise hit detection"
                        ],
                        "cons": [
                            "Only detects along lines",
                            "Multiple rays needed for areas",
                            "Can miss between rays"
                        ],
                        "use_when": [
                            "Shooting mechanics",
                            "Line of sight checks",
                            "Laser/beam weapons"
                        ]
                    }
                },
                "ai": {
                    "state-machine": {
                        "description": "Finite state machine for AI behavior",
                        "pros": [
                            "Easy to understand",
                            "Predictable behavior",
                            "Simple to debug"
                        ],
                        "cons": [
                            "Can become complex",
                            "Rigid transitions",
                            "State explosion problem"
                        ],
                        "use_when": [
                            "Clear, distinct states",
                            "Simple AI behaviors",
                            "Predictability important"
                        ]
                    },
                    "behavior-tree": {
                        "description": "Hierarchical behavior trees",
                        "pros": [
                            "Modular and reusable",
                            "Complex behaviors possible",
                            "Industry standard"
                        ],
                        "cons": [
                            "Steeper learning curve",
                            "More complex to implement",
                            "Debugging can be difficult"
                        ],
                        "use_when": [
                            "Complex AI needed",
                            "Reusable behaviors",
                            "Professional game AI"
                        ]
                    },
                    "utility-based": {
                        "description": "Score actions and choose highest",
                        "pros": [
                            "Emergent behavior",
                            "Smooth transitions",
                            "Highly flexible"
                        ],
                        "cons": [
                            "Hard to predict",
                            "Tuning required",
                            "Performance considerations"
                        ],
                        "use_when": [
                            "Dynamic behavior needed",
                            "Multiple factors to consider",
                            "Realistic decision making"
                        ]
                    }
                }
            }
            
            topic_lower = topic.lower()
            if topic_lower not in comparisons:
                return {
                    "error": f"Unknown topic: {topic}",
                    "available_topics": list(comparisons.keys())
                }
            
            comparison_result = {
                "topic": topic,
                "approaches": {}
            }
            
            for approach in approaches:
                approach_lower = approach.lower().replace("_", "-")
                if approach_lower in comparisons[topic_lower]:
                    comparison_result["approaches"][approach] = comparisons[topic_lower][approach_lower]
                else:
                    comparison_result["approaches"][approach] = {
                        "error": f"Unknown approach for {topic}: {approach}",
                        "available": list(comparisons[topic_lower].keys())
                    }
            
            # Add recommendation
            comparison_result["recommendation"] = self._get_approach_recommendation(topic_lower, approaches)
            
            return comparison_result
    
    def _get_related_concepts(self, concept: str) -> List[str]:
        """Get concepts related to the given one"""
        relations = {
            "server-authoritative": ["networking", "multiplayer", "event-driven"],
            "entity-system": ["entity-controller", "event-driven", "physics"],
            "event-driven": ["server-authoritative", "entity-system"],
            "physics": ["entity-system", "collision-detection"],
            "networking": ["server-authoritative", "multiplayer", "persistence"],
            "persistence": ["networking", "multiplayer"],
            "chunk-system": ["terrain-generation", "optimization"],
            "multiplayer": ["server-authoritative", "networking", "persistence"]
        }
        return relations.get(concept, [])
    
    def _get_architecture_diagrams(self, component: str) -> Dict[str, str]:
        """Get ASCII diagrams for architecture components"""
        diagrams = {
            "world-hierarchy": """
GameServer
    ├── WorldManager
    │   ├── World 1
    │   │   ├── EntityManager
    │   │   ├── ChunkLattice
    │   │   ├── AudioManager
    │   │   └── ...
    │   └── World 2
    │       └── ...
    └── PlayerManager
            """,
            "entity-controller": """
Entity (Data)          Controller (Behavior)
    │                        │
    ├── position ←──────────┤ tick()
    ├── rotation            │
    ├── health              ├── handleInput()
    └── ...                 └── updateState()
            """,
            "event-flow": """
Player Input → Server → Validation
                ↓
            Game Logic
                ↓
            Entity Update
                ↓
            State Change → Broadcast → All Clients
            """
        }
        return {"ascii": diagrams.get(component, "No diagram available")}
    
    def _get_lifecycle_patterns(self, lifecycle: str) -> List[str]:
        """Get common patterns for lifecycle management"""
        patterns = {
            "entity": [
                "Object pooling for frequently spawned entities",
                "Lazy initialization for expensive components",
                "Event cleanup in despawn handlers"
            ],
            "player": [
                "Grace period for reconnection",
                "Incremental data saving",
                "State restoration on rejoin"
            ],
            "world": [
                "Warm-up period before allowing players",
                "Graceful shutdown with player migration",
                "World state snapshots for recovery"
            ]
        }
        return patterns.get(lifecycle, [])
    
    def _get_approach_recommendation(self, topic: str, approaches: List[str]) -> str:
        """Get recommendation based on topic and approaches"""
        recommendations = {
            "movement": "Use physics-based for realistic games, direct-position for arcade-style",
            "collision": "Use physics colliders for accuracy, distance checks for performance",
            "ai": "Start with state machines, upgrade to behavior trees for complexity"
        }
        return recommendations.get(topic, "Choose based on your specific requirements")