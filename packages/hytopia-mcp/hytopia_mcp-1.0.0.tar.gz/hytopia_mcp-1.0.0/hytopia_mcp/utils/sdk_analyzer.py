"""
SDK Analyzer - Parse and analyze HYTOPIA SDK structure
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import aiohttp
import asyncio

class SDKAnalyzer:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.sdk_data: Optional[Dict[str, Any]] = None
        self.api_index: Dict[str, Any] = {}
        self._initialized = False
        self._init_lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize SDK analyzer by loading/parsing SDK data"""
        async with self._init_lock:
            if self._initialized:
                return
            
            # Try to load from cache first
            cached_data = await self.cache_manager.get("sdk_data", ttl=86400)  # 24 hour TTL
            if cached_data:
                self.sdk_data = cached_data
                self.api_index = await self.cache_manager.get("api_index", ttl=86400) or {}
                self._initialized = True
                return
            
            # If not cached, fetch and parse
            await self._fetch_and_parse_sdk()
            
            # Cache the results
            if self.sdk_data:
                await self.cache_manager.set("sdk_data", self.sdk_data)
                await self.cache_manager.set("api_index", self.api_index)
            
            self._initialized = True
    
    async def _fetch_and_parse_sdk(self) -> None:
        """Fetch SDK data from GitHub and parse it"""
        # For now, we'll create a mock structure based on our knowledge
        # In a real implementation, this would fetch and parse the actual TypeScript definitions
        
        self.sdk_data = {
            "version": "0.1.0-alpha",
            "last_updated": datetime.now().isoformat(),
            "namespaces": {
                "server": {
                    "classes": self._get_mock_classes(),
                    "interfaces": self._get_mock_interfaces(),
                    "enums": self._get_mock_enums()
                }
            }
        }
        
        # Build search index
        self._build_api_index()
    
    def _get_mock_classes(self) -> Dict[str, Any]:
        """Get mock class definitions"""
        return {
            "Entity": {
                "description": "Base class for all game entities",
                "extends": "EventRouter",
                "properties": [
                    {"name": "id", "type": "string", "readonly": True},
                    {"name": "position", "type": "Vector3", "readonly": True},
                    {"name": "rotation", "type": "Quaternion", "readonly": True},
                    {"name": "isSpawned", "type": "boolean", "readonly": True}
                ],
                "methods": [
                    {
                        "name": "spawn",
                        "description": "Spawn entity in the world",
                        "parameters": [],
                        "returns": {"type": "void"}
                    },
                    {
                        "name": "despawn",
                        "description": "Remove entity from the world",
                        "parameters": [],
                        "returns": {"type": "void"}
                    },
                    {
                        "name": "setPosition",
                        "description": "Set entity position",
                        "parameters": [
                            {"name": "position", "type": "Vector3"}
                        ],
                        "returns": {"type": "void"}
                    }
                ],
                "events": ["spawn", "despawn", "position_changed"]
            },
            "World": {
                "description": "Main game world instance",
                "properties": [
                    {"name": "entityManager", "type": "EntityManager", "readonly": True},
                    {"name": "playerManager", "type": "PlayerManager", "readonly": True},
                    {"name": "chunkLattice", "type": "ChunkLattice", "readonly": True},
                    {"name": "audioManager", "type": "AudioManager", "readonly": True}
                ],
                "methods": [],
                "events": ["tick", "playerJoin", "playerLeave"]
            },
            "Player": {
                "description": "Represents a connected player",
                "properties": [
                    {"name": "id", "type": "string", "readonly": True},
                    {"name": "username", "type": "string", "readonly": True},
                    {"name": "input", "type": "PlayerInput", "readonly": True},
                    {"name": "camera", "type": "PlayerCamera", "readonly": True},
                    {"name": "ui", "type": "PlayerUI", "readonly": True}
                ],
                "methods": [
                    {
                        "name": "disconnect",
                        "description": "Disconnect the player",
                        "parameters": [
                            {"name": "reason", "type": "string", "optional": True}
                        ],
                        "returns": {"type": "void"}
                    }
                ],
                "events": ["join", "leave", "spawn", "death"]
            }
        }
    
    def _get_mock_interfaces(self) -> Dict[str, Any]:
        """Get mock interface definitions"""
        return {
            "EntityOptions": {
                "description": "Options for creating entities",
                "properties": [
                    {"name": "position", "type": "Vector3", "optional": True},
                    {"name": "rotation", "type": "Quaternion", "optional": True},
                    {"name": "name", "type": "string", "optional": True}
                ]
            },
            "PlayerInput": {
                "description": "Player input state",
                "properties": [
                    {"name": "w", "type": "boolean"},
                    {"name": "a", "type": "boolean"},
                    {"name": "s", "type": "boolean"},
                    {"name": "d", "type": "boolean"},
                    {"name": "space", "type": "boolean"},
                    {"name": "shift", "type": "boolean"},
                    {"name": "mouseLeft", "type": "boolean"},
                    {"name": "mouseRight", "type": "boolean"}
                ]
            }
        }
    
    def _get_mock_enums(self) -> Dict[str, Any]:
        """Get mock enum definitions"""
        return {
            "RigidBodyType": {
                "description": "Types of rigid bodies",
                "values": ["dynamic", "kinematic_position", "kinematic_velocity", "fixed"]
            },
            "ColliderShape": {
                "description": "Collision shape types",
                "values": ["ball", "block", "capsule", "cone", "cylinder", "trimesh"]
            }
        }
    
    def _build_api_index(self) -> None:
        """Build searchable index of API elements"""
        self.api_index = {
            "classes": {},
            "methods": {},
            "properties": {},
            "interfaces": {},
            "enums": {}
        }
        
        # Index classes
        for class_name, class_data in self.sdk_data["namespaces"]["server"]["classes"].items():
            self.api_index["classes"][class_name.lower()] = class_name
            
            # Index methods
            for method in class_data.get("methods", []):
                method_key = f"{class_name}.{method['name']}".lower()
                self.api_index["methods"][method_key] = {
                    "class": class_name,
                    "method": method["name"]
                }
            
            # Index properties
            for prop in class_data.get("properties", []):
                prop_key = f"{class_name}.{prop['name']}".lower()
                self.api_index["properties"][prop_key] = {
                    "class": class_name,
                    "property": prop["name"]
                }
    
    async def get_api_structure(self) -> Dict[str, Any]:
        """Get the overall API structure"""
        await self.initialize()
        return self.sdk_data or {}
    
    async def get_class_info(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a class"""
        await self.initialize()
        
        if not self.sdk_data:
            return None
        
        classes = self.sdk_data["namespaces"]["server"]["classes"]
        return classes.get(class_name)
    
    async def get_method_info(self, class_name: str, method_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific method"""
        class_info = await self.get_class_info(class_name)
        if not class_info:
            return None
        
        for method in class_info.get("methods", []):
            if method["name"] == method_name:
                return method
        
        return None
    
    async def find_similar_classes(self, query: str) -> List[str]:
        """Find classes with similar names"""
        await self.initialize()
        
        if not self.sdk_data:
            return []
        
        query_lower = query.lower()
        classes = self.sdk_data["namespaces"]["server"]["classes"]
        
        # Exact match
        if query in classes:
            return [query]
        
        # Case-insensitive match
        for class_name in classes:
            if class_name.lower() == query_lower:
                return [class_name]
        
        # Partial matches
        matches = []
        for class_name in classes:
            if query_lower in class_name.lower():
                matches.append(class_name)
        
        return sorted(matches)[:5]  # Return top 5 matches
    
    async def get_all_interfaces(self) -> List[str]:
        """Get list of all interfaces"""
        await self.initialize()
        
        if not self.sdk_data:
            return []
        
        interfaces = self.sdk_data["namespaces"]["server"]["interfaces"]
        return sorted(interfaces.keys())
    
    async def get_all_enums(self) -> List[Dict[str, Any]]:
        """Get all enums with their values"""
        await self.initialize()
        
        if not self.sdk_data:
            return []
        
        enums = self.sdk_data["namespaces"]["server"]["enums"]
        result = []
        
        for name, data in enums.items():
            result.append({
                "name": name,
                "description": data.get("description", ""),
                "values": data.get("values", [])
            })
        
        return result
    
    async def get_sdk_version(self) -> str:
        """Get current SDK version"""
        await self.initialize()
        return self.sdk_data.get("version", "unknown") if self.sdk_data else "unknown"
    
    async def get_last_update(self) -> str:
        """Get last update timestamp"""
        await self.initialize()
        return self.sdk_data.get("last_updated", "unknown") if self.sdk_data else "unknown"
    
    async def search_api(self, query: str) -> Dict[str, List[Any]]:
        """Search across all API elements"""
        await self.initialize()
        
        query_lower = query.lower()
        results = {
            "classes": [],
            "methods": [],
            "properties": [],
            "interfaces": [],
            "enums": []
        }
        
        if not self.api_index:
            return results
        
        # Search classes
        for key, value in self.api_index["classes"].items():
            if query_lower in key:
                results["classes"].append(value)
        
        # Search methods
        for key, value in self.api_index["methods"].items():
            if query_lower in key:
                results["methods"].append(value)
        
        # Search properties
        for key, value in self.api_index["properties"].items():
            if query_lower in key:
                results["properties"].append(value)
        
        return results