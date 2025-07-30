"""
API Explorer Tools - Intelligent navigation through HYTOPIA SDK API
"""

from typing import Dict, List, Any, Optional
from fastmcp import FastMCP, Context
import json
import re
from pathlib import Path

class APIExplorerTools:
    def __init__(self, mcp: FastMCP, sdk_analyzer):
        self.mcp = mcp
        self.sdk_analyzer = sdk_analyzer
        self._register_tools()
    
    def _register_tools(self):
        @self.mcp.tool()
        async def hytopia_list_modules(
            category: Optional[str] = None,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            List all available modules/namespaces in HYTOPIA SDK.
            Categories: core, entities, physics, world, player, ui, audio, blocks, utils
            """
            api_structure = await self.sdk_analyzer.get_api_structure()
            
            modules = {
                "core": {
                    "description": "Core game systems",
                    "modules": [
                        {"name": "World", "description": "Main game world class"},
                        {"name": "WorldManager", "description": "Manages multiple worlds"},
                        {"name": "GameServer", "description": "Server instance management"},
                        {"name": "EventRouter", "description": "Event system base class"}
                    ]
                },
                "entities": {
                    "description": "Entity system classes",
                    "modules": [
                        {"name": "Entity", "description": "Base entity class"},
                        {"name": "BlockEntity", "description": "Voxel-based entities"},
                        {"name": "ModelEntity", "description": "3D model entities"},
                        {"name": "PlayerEntity", "description": "Player-specific entities"},
                        {"name": "EntityManager", "description": "Entity lifecycle management"},
                        {"name": "BaseEntityController", "description": "Entity behavior control"},
                        {"name": "DefaultPlayerEntityController", "description": "Default player controls"},
                        {"name": "PathfindingEntityController", "description": "AI pathfinding"},
                        {"name": "SimpleEntityController", "description": "Basic entity control"}
                    ]
                },
                "physics": {
                    "description": "Physics simulation",
                    "modules": [
                        {"name": "Simulation", "description": "Physics world"},
                        {"name": "RigidBody", "description": "Physics bodies"},
                        {"name": "Collider", "description": "Collision shapes"},
                        {"name": "CollisionGroups", "description": "Collision filtering"},
                        {"name": "DynamicRigidBody", "description": "Moving physics bodies"},
                        {"name": "FixedRigidBody", "description": "Static physics bodies"},
                        {"name": "KinematicRigidBody", "description": "Controlled physics bodies"}
                    ]
                },
                "world": {
                    "description": "World and terrain management",
                    "modules": [
                        {"name": "ChunkLattice", "description": "Terrain chunk grid"},
                        {"name": "Chunk", "description": "16x16x16 block sections"},
                        {"name": "Block", "description": "Individual voxel blocks"},
                        {"name": "BlockType", "description": "Block definitions"},
                        {"name": "BlockTypeRegistry", "description": "Block type management"}
                    ]
                },
                "player": {
                    "description": "Player systems",
                    "modules": [
                        {"name": "Player", "description": "Connected player"},
                        {"name": "PlayerManager", "description": "Global player management"},
                        {"name": "PlayerInput", "description": "Input state"},
                        {"name": "PlayerCamera", "description": "Camera control"},
                        {"name": "PlayerUI", "description": "UI system"}
                    ]
                },
                "ui": {
                    "description": "User interface",
                    "modules": [
                        {"name": "PlayerUI", "description": "Per-player UI"},
                        {"name": "SceneUI", "description": "3D world UI"},
                        {"name": "SceneUIManager", "description": "Scene UI management"}
                    ]
                },
                "audio": {
                    "description": "Audio system",
                    "modules": [
                        {"name": "Audio", "description": "Audio instances"},
                        {"name": "AudioManager", "description": "Audio management"}
                    ]
                },
                "blocks": {
                    "description": "Block system",
                    "modules": [
                        {"name": "BlockType", "description": "Block type definitions"},
                        {"name": "BlockTypeRegistry", "description": "Block registration"},
                        {"name": "BlockCollider", "description": "Block collision shapes"}
                    ]
                },
                "utils": {
                    "description": "Utility classes",
                    "modules": [
                        {"name": "Vector2", "description": "2D vector math"},
                        {"name": "Vector3", "description": "3D vector math"},
                        {"name": "Quaternion", "description": "Rotation math"},
                        {"name": "Matrix4", "description": "Transformation matrices"},
                        {"name": "RgbColor", "description": "Color values"}
                    ]
                }
            }
            
            if category:
                if category.lower() in modules:
                    return {
                        "category": category,
                        "modules": modules[category.lower()]
                    }
                else:
                    return {
                        "error": f"Unknown category: {category}",
                        "available_categories": list(modules.keys())
                    }
            
            return {
                "categories": modules,
                "total_modules": sum(len(cat["modules"]) for cat in modules.values()),
                "usage": "Use hytopia_explore_class to dive into specific classes"
            }
        
        @self.mcp.tool()
        async def hytopia_explore_class(
            class_name: str,
            include_inherited: bool = False,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Explore a specific class in detail - its purpose, properties, methods, and events.
            Example: hytopia_explore_class("Entity")
            """
            class_info = await self.sdk_analyzer.get_class_info(class_name)
            
            if not class_info:
                suggestions = await self.sdk_analyzer.find_similar_classes(class_name)
                return {
                    "error": f"Class '{class_name}' not found",
                    "suggestions": suggestions,
                    "tip": "Use hytopia_list_modules to see available classes"
                }
            
            # Format the class information
            result = {
                "class": class_name,
                "description": class_info.get("description", ""),
                "extends": class_info.get("extends", None),
                "category": self._categorize_class(class_name),
                "constructor": self._format_constructor(class_info.get("constructor")),
                "properties": self._format_properties(class_info.get("properties", [])),
                "methods": self._format_methods_summary(class_info.get("methods", [])),
                "events": self._format_events(class_info.get("events", [])),
                "usage_pattern": self._get_usage_pattern(class_name),
                "related_classes": self._get_related_classes(class_name),
                "common_use_cases": self._get_common_use_cases(class_name)
            }
            
            if include_inherited and class_info.get("extends"):
                parent_info = await self.sdk_analyzer.get_class_info(class_info["extends"])
                if parent_info:
                    result["inherited_methods"] = self._format_methods_summary(
                        parent_info.get("methods", [])
                    )
            
            return result
        
        @self.mcp.tool()
        async def hytopia_get_methods(
            class_name: str,
            filter_by: Optional[str] = None,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get all methods of a class with filtering options.
            Filters: getters, setters, events, async, static
            Example: hytopia_get_methods("Entity", "setters")
            """
            class_info = await self.sdk_analyzer.get_class_info(class_name)
            
            if not class_info:
                return {
                    "error": f"Class '{class_name}' not found",
                    "tip": "Use hytopia_list_modules to see available classes"
                }
            
            methods = class_info.get("methods", [])
            
            # Apply filters
            if filter_by:
                if filter_by == "getters":
                    methods = [m for m in methods if m["name"].startswith("get")]
                elif filter_by == "setters":
                    methods = [m for m in methods if m["name"].startswith("set")]
                elif filter_by == "events":
                    methods = [m for m in methods if m["name"] in ["on", "off", "once", "emit"]]
                elif filter_by == "async":
                    methods = [m for m in methods if m.get("async", False)]
                elif filter_by == "static":
                    methods = [m for m in methods if m.get("static", False)]
            
            # Group methods by category
            categorized = {
                "lifecycle": [],
                "state_management": [],
                "event_handling": [],
                "getters": [],
                "setters": [],
                "actions": [],
                "utilities": []
            }
            
            for method in methods:
                category = self._categorize_method(method)
                categorized[category].append({
                    "name": method["name"],
                    "description": method.get("description", ""),
                    "parameters": len(method.get("parameters", [])),
                    "returns": method.get("returns", {}).get("type", "void"),
                    "async": method.get("async", False)
                })
            
            # Remove empty categories
            categorized = {k: v for k, v in categorized.items() if v}
            
            return {
                "class": class_name,
                "total_methods": len(methods),
                "filtered_by": filter_by,
                "methods_by_category": categorized,
                "usage": "Use hytopia_get_method_details for full method signatures"
            }
        
        @self.mcp.tool()
        async def hytopia_get_method_details(
            class_name: str,
            method_name: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get detailed information about a specific method including parameters, return type, and examples.
            Example: hytopia_get_method_details("Entity", "setPosition")
            """
            method_info = await self.sdk_analyzer.get_method_info(class_name, method_name)
            
            if not method_info:
                return {
                    "error": f"Method '{method_name}' not found in class '{class_name}'",
                    "tip": f"Use hytopia_get_methods('{class_name}') to see available methods"
                }
            
            # Generate usage example
            example = self._generate_method_example(class_name, method_info)
            
            return {
                "class": class_name,
                "method": method_name,
                "signature": self._format_method_signature(method_info),
                "description": method_info.get("description", ""),
                "parameters": self._format_parameters(method_info.get("parameters", [])),
                "returns": self._format_return_type(method_info.get("returns")),
                "async": method_info.get("async", False),
                "static": method_info.get("static", False),
                "example": example,
                "related_methods": self._get_related_methods(class_name, method_name),
                "common_patterns": self._get_method_patterns(class_name, method_name)
            }
        
        @self.mcp.tool()
        async def hytopia_get_properties(
            class_name: str,
            include_readonly: bool = True,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get all properties of a class with their types and descriptions.
            """
            class_info = await self.sdk_analyzer.get_class_info(class_name)
            
            if not class_info:
                return {
                    "error": f"Class '{class_name}' not found"
                }
            
            properties = class_info.get("properties", [])
            
            if not include_readonly:
                properties = [p for p in properties if not p.get("readonly", False)]
            
            return {
                "class": class_name,
                "properties": [{
                    "name": prop["name"],
                    "type": prop.get("type", "any"),
                    "description": prop.get("description", ""),
                    "readonly": prop.get("readonly", False),
                    "optional": prop.get("optional", False),
                    "default": prop.get("default")
                } for prop in properties],
                "total": len(properties)
            }
        
        @self.mcp.tool()
        async def hytopia_get_interfaces(
            pattern: Optional[str] = None,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            List all interfaces in the SDK with optional pattern matching.
            Example: hytopia_get_interfaces("Options")
            """
            interfaces = await self.sdk_analyzer.get_all_interfaces()
            
            if pattern:
                interfaces = [i for i in interfaces if pattern.lower() in i.lower()]
            
            # Group by category
            categorized = {
                "options": [i for i in interfaces if "Options" in i],
                "events": [i for i in interfaces if "Event" in i],
                "callbacks": [i for i in interfaces if "Callback" in i],
                "data": [i for i in interfaces if i not in sum([
                    [i for i in interfaces if "Options" in i],
                    [i for i in interfaces if "Event" in i],
                    [i for i in interfaces if "Callback" in i]
                ], [])]
            }
            
            return {
                "total": len(interfaces),
                "pattern": pattern,
                "interfaces_by_type": categorized,
                "usage": "Use hytopia_explore_class to examine interface details"
            }
        
        @self.mcp.tool()
        async def hytopia_get_enums(
            context: Context = None
        ) -> Dict[str, Any]:
            """
            List all enums in the SDK with their values.
            """
            enums = await self.sdk_analyzer.get_all_enums()
            
            return {
                "enums": [{
                    "name": enum["name"],
                    "description": enum.get("description", ""),
                    "values": enum.get("values", [])
                } for enum in enums],
                "total": len(enums)
            }
    
    def _categorize_class(self, class_name: str) -> str:
        """Categorize a class based on its name"""
        if "Entity" in class_name:
            return "entities"
        elif "Player" in class_name:
            return "player"
        elif any(phys in class_name for phys in ["RigidBody", "Collider", "Simulation"]):
            return "physics"
        elif any(world in class_name for world in ["World", "Chunk", "Block"]):
            return "world"
        elif "UI" in class_name:
            return "ui"
        elif "Audio" in class_name:
            return "audio"
        elif any(util in class_name for util in ["Vector", "Matrix", "Quaternion", "Color"]):
            return "utils"
        else:
            return "core"
    
    def _categorize_method(self, method: Dict) -> str:
        """Categorize a method based on its name and properties"""
        name = method["name"]
        
        if name in ["spawn", "despawn", "destroy", "init", "dispose"]:
            return "lifecycle"
        elif name.startswith("get"):
            return "getters"
        elif name.startswith("set"):
            return "setters"
        elif name in ["on", "off", "once", "emit"]:
            return "event_handling"
        elif name in ["update", "tick", "sync"]:
            return "state_management"
        elif any(action in name for action in ["move", "rotate", "scale", "play", "stop", "load"]):
            return "actions"
        else:
            return "utilities"
    
    def _format_constructor(self, constructor: Optional[Dict]) -> Optional[Dict]:
        """Format constructor information"""
        if not constructor:
            return None
        
        return {
            "parameters": self._format_parameters(constructor.get("parameters", [])),
            "description": constructor.get("description", "")
        }
    
    def _format_properties(self, properties: List[Dict]) -> List[Dict]:
        """Format property information"""
        return [{
            "name": prop["name"],
            "type": prop.get("type", "any"),
            "readonly": prop.get("readonly", False),
            "description": prop.get("description", "")[:100] + "..." if len(prop.get("description", "")) > 100 else prop.get("description", "")
        } for prop in properties[:10]]  # Limit to first 10 for overview
    
    def _format_methods_summary(self, methods: List[Dict]) -> Dict[str, List[str]]:
        """Format methods as a summary grouped by category"""
        summary = {}
        for method in methods:
            category = self._categorize_method(method)
            if category not in summary:
                summary[category] = []
            summary[category].append(method["name"])
        return summary
    
    def _format_events(self, events: List[Dict]) -> List[str]:
        """Format event names"""
        return [event["name"] for event in events]
    
    def _format_parameters(self, parameters: List[Dict]) -> List[Dict]:
        """Format parameter information"""
        return [{
            "name": param["name"],
            "type": param.get("type", "any"),
            "optional": param.get("optional", False),
            "description": param.get("description", ""),
            "default": param.get("default")
        } for param in parameters]
    
    def _format_return_type(self, returns: Optional[Dict]) -> Dict[str, Any]:
        """Format return type information"""
        if not returns:
            return {"type": "void"}
        
        return {
            "type": returns.get("type", "any"),
            "description": returns.get("description", "")
        }
    
    def _format_method_signature(self, method: Dict) -> str:
        """Generate method signature string"""
        params = []
        for param in method.get("parameters", []):
            param_str = param["name"]
            if param.get("optional", False):
                param_str += "?"
            param_str += f": {param.get('type', 'any')}"
            params.append(param_str)
        
        return_type = method.get("returns", {}).get("type", "void")
        async_prefix = "async " if method.get("async", False) else ""
        
        return f"{async_prefix}{method['name']}({', '.join(params)}): {return_type}"
    
    def _generate_method_example(self, class_name: str, method: Dict) -> str:
        """Generate a usage example for a method"""
        method_name = method["name"]
        
        # Special cases for common patterns
        if class_name == "Entity" and method_name == "setPosition":
            return """// Move entity to a new position
entity.setPosition(new Vector3(10, 0, 5));

// Animate movement over time
function moveEntity(entity, targetPos, duration) {
  const startPos = entity.position;
  const startTime = Date.now();
  
  const update = () => {
    const elapsed = Date.now() - startTime;
    const t = Math.min(elapsed / duration, 1);
    
    const currentPos = Vector3.lerp(startPos, targetPos, t);
    entity.setPosition(currentPos);
    
    if (t < 1) {
      requestAnimationFrame(update);
    }
  };
  
  update();
}"""
        
        # Generate generic example
        params = []
        for param in method.get("parameters", []):
            if param["type"] == "string":
                params.append(f'"{param["name"]}"')
            elif param["type"] == "number":
                params.append("0")
            elif param["type"] == "boolean":
                params.append("true")
            elif "Vector3" in param["type"]:
                params.append("new Vector3(0, 0, 0)")
            else:
                params.append(f"/* {param['type']} */" )
        
        instance_name = class_name[0].lower() + class_name[1:]
        return f"{instance_name}.{method_name}({', '.join(params)});"
    
    def _get_usage_pattern(self, class_name: str) -> str:
        """Get common usage pattern for a class"""
        patterns = {
            "Entity": "Entities are spawned through world.entityManager and controlled via controllers",
            "World": "Access the world instance in startServer callback",
            "Player": "Players are managed automatically, listen for join/leave events",
            "BlockType": "Register custom block types with BlockTypeRegistry",
            "Audio": "Play audio through world.audioManager",
            "RigidBody": "Attach physics bodies to entities for physics simulation"
        }
        return patterns.get(class_name, f"Use {class_name} as part of the HYTOPIA game system")
    
    def _get_related_classes(self, class_name: str) -> List[str]:
        """Get related classes"""
        relations = {
            "Entity": ["EntityManager", "BaseEntityController", "RigidBody", "Collider"],
            "World": ["WorldManager", "ChunkLattice", "EntityManager", "AudioManager"],
            "Player": ["PlayerEntity", "PlayerInput", "PlayerCamera", "PlayerUI"],
            "BlockType": ["BlockTypeRegistry", "Block", "Chunk", "ChunkLattice"],
            "RigidBody": ["Collider", "Simulation", "Entity"],
            "Audio": ["AudioManager", "Entity"]
        }
        return relations.get(class_name, [])
    
    def _get_common_use_cases(self, class_name: str) -> List[str]:
        """Get common use cases for a class"""
        use_cases = {
            "Entity": [
                "Create NPCs and enemies",
                "Spawn collectible items",
                "Build interactive objects",
                "Implement moving platforms"
            ],
            "World": [
                "Initialize game world",
                "Handle player connections",
                "Manage game state",
                "Control world physics"
            ],
            "Player": [
                "Track player actions",
                "Handle player input",
                "Manage player inventory",
                "Show player-specific UI"
            ],
            "BlockType": [
                "Create custom blocks",
                "Define block interactions",
                "Set block textures",
                "Handle block collisions"
            ]
        }
        return use_cases.get(class_name, [])
    
    def _get_related_methods(self, class_name: str, method_name: str) -> List[str]:
        """Get methods commonly used together"""
        related = {
            ("Entity", "setPosition"): ["getPosition", "setRotation", "setScale"],
            ("Entity", "spawn"): ["despawn", "setController", "setRigidBody"],
            ("World", "on"): ["off", "once", "emit"],
            ("Player", "ui.load"): ["ui.sendData", "ui.on"],
            ("BlockType", "registerBlockType"): ["getBlockType", "getAllBlockTypes"]
        }
        return related.get((class_name, method_name), [])
    
    def _get_method_patterns(self, class_name: str, method_name: str) -> List[str]:
        """Get common patterns for using a method"""
        patterns = {
            ("Entity", "setPosition"): [
                "Teleport entity instantly",
                "Animate movement over time",
                "Follow another entity",
                "Constrain to boundaries"
            ],
            ("Entity", "on"): [
                "Listen for collision events",
                "React to despawn",
                "Monitor state changes",
                "Chain multiple handlers"
            ],
            ("World", "chunkLattice.setBlock"): [
                "Build structures programmatically",
                "Modify terrain at runtime",
                "Create destructible environments",
                "Generate procedural worlds"
            ]
        }
        return patterns.get((class_name, method_name), [])