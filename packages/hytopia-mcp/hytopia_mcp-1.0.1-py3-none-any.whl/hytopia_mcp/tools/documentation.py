"""
Documentation Tools - Access and search HYTOPIA documentation
"""

from typing import Dict, List, Any, Optional
from fastmcp import FastMCP, Context

class DocumentationTools:
    def __init__(self, mcp: FastMCP, sdk_analyzer):
        self.mcp = mcp
        self.sdk_analyzer = sdk_analyzer
        self._register_tools()
        
        # Mock documentation structure
        self.docs = self._load_documentation()
    
    def _register_tools(self):
        @self.mcp.tool()
        async def hytopia_get_guide(
            guide_name: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get a specific documentation guide.
            Guides: getting-started, entities, physics, ui, networking, persistence
            """
            if context:
                await context.info(f"Fetching guide: {guide_name}")
            
            guide = self.docs["guides"].get(guide_name)
            if not guide:
                return {
                    "error": f"Guide '{guide_name}' not found",
                    "available_guides": list(self.docs["guides"].keys()),
                    "suggestion": "Try 'getting-started' or 'entities'"
                }
            
            return {
                "guide": guide_name,
                "content": guide,
                "related_guides": self._get_related_guides(guide_name),
                "next_steps": self._get_next_steps(guide_name)
            }
        
        @self.mcp.tool()
        async def hytopia_search_docs(
            query: str,
            limit: int = 10,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Search through HYTOPIA documentation.
            Returns relevant sections and guides.
            """
            if context:
                await context.info(f"Searching documentation for: {query}")
            
            query_lower = query.lower()
            results = []
            
            # Search guides
            for guide_name, guide_content in self.docs["guides"].items():
                relevance = self._calculate_doc_relevance(query_lower, guide_name, guide_content)
                if relevance > 0:
                    results.append({
                        "type": "guide",
                        "name": guide_name,
                        "title": guide_content["title"],
                        "relevance": relevance,
                        "preview": self._get_content_preview(guide_content, query_lower)
                    })
            
            # Search tutorials
            for tutorial_name, tutorial_content in self.docs["tutorials"].items():
                relevance = self._calculate_doc_relevance(query_lower, tutorial_name, tutorial_content)
                if relevance > 0:
                    results.append({
                        "type": "tutorial",
                        "name": tutorial_name,
                        "title": tutorial_content["title"],
                        "relevance": relevance,
                        "preview": self._get_content_preview(tutorial_content, query_lower)
                    })
            
            # Search API reference
            for api_name, api_content in self.docs["api_reference"].items():
                relevance = self._calculate_doc_relevance(query_lower, api_name, api_content)
                if relevance > 0:
                    results.append({
                        "type": "api_reference",
                        "name": api_name,
                        "title": api_content["title"],
                        "relevance": relevance,
                        "preview": self._get_content_preview(api_content, query_lower)
                    })
            
            # Sort by relevance
            results.sort(key=lambda x: x["relevance"], reverse=True)
            top_results = results[:limit]
            
            return {
                "query": query,
                "found": len(results),
                "showing": len(top_results),
                "results": top_results,
                "search_tips": self._get_search_tips(query, results)
            }
        
        @self.mcp.tool()
        async def hytopia_get_tutorial(
            tutorial_name: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get a step-by-step tutorial.
            Tutorials: first-game, multiplayer-basics, custom-entities, game-modes
            """
            tutorial = self.docs["tutorials"].get(tutorial_name)
            if not tutorial:
                return {
                    "error": f"Tutorial '{tutorial_name}' not found",
                    "available_tutorials": list(self.docs["tutorials"].keys())
                }
            
            return {
                "tutorial": tutorial_name,
                "content": tutorial,
                "prerequisites": tutorial.get("prerequisites", []),
                "estimated_time": tutorial.get("estimated_time", "30 minutes"),
                "next_tutorials": self._get_next_tutorials(tutorial_name)
            }
        
        @self.mcp.tool()
        async def hytopia_get_api_docs(
            api_element: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get API documentation for a specific class, method, or interface.
            Example: 'Entity', 'World.entityManager', 'EntityOptions'
            """
            # Check if it's in our reference
            api_doc = self.docs["api_reference"].get(api_element)
            if api_doc:
                return {
                    "element": api_element,
                    "documentation": api_doc,
                    "examples": api_doc.get("examples", []),
                    "see_also": api_doc.get("see_also", [])
                }
            
            # Try to get from SDK analyzer
            if "." in api_element:
                class_name, member = api_element.split(".", 1)
                class_info = await self.sdk_analyzer.get_class_info(class_name)
                if class_info:
                    # Look for method or property
                    for method in class_info.get("methods", []):
                        if method["name"] == member:
                            return {
                                "element": api_element,
                                "documentation": {
                                    "type": "method",
                                    "class": class_name,
                                    "name": member,
                                    "description": method.get("description", ""),
                                    "signature": self._format_method_signature(method),
                                    "parameters": method.get("parameters", []),
                                    "returns": method.get("returns", {})
                                }
                            }
            else:
                # Try as class
                class_info = await self.sdk_analyzer.get_class_info(api_element)
                if class_info:
                    return {
                        "element": api_element,
                        "documentation": {
                            "type": "class",
                            "name": api_element,
                            "description": class_info.get("description", ""),
                            "extends": class_info.get("extends"),
                            "properties": class_info.get("properties", [])[:5],  # First 5
                            "methods": [m["name"] for m in class_info.get("methods", [])][:10]  # First 10
                        }
                    }
            
            return {
                "error": f"API documentation for '{api_element}' not found",
                "suggestion": "Try 'hytopia_search_docs' or 'hytopia_explore_class'"
            }
        
        @self.mcp.tool()
        async def hytopia_get_best_practices(
            topic: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get best practices for specific topics.
            Topics: performance, security, architecture, multiplayer, testing
            """
            practices = self.docs["best_practices"].get(topic)
            if not practices:
                return {
                    "error": f"Best practices for '{topic}' not found",
                    "available_topics": list(self.docs["best_practices"].keys())
                }
            
            return {
                "topic": topic,
                "best_practices": practices,
                "common_mistakes": self._get_common_mistakes(topic),
                "examples": self._get_best_practice_examples(topic)
            }
    
    def _load_documentation(self) -> Dict[str, Any]:
        """Load documentation structure (mock for now)"""
        return {
            "guides": {
                "getting-started": {
                    "title": "Getting Started with HYTOPIA",
                    "sections": [
                        {
                            "title": "Installation",
                            "content": "Install HYTOPIA SDK using npm create hytopia@latest"
                        },
                        {
                            "title": "Your First Game",
                            "content": "Create a basic game world with player spawning"
                        },
                        {
                            "title": "Understanding the Architecture",
                            "content": "Learn about server-authoritative design"
                        }
                    ],
                    "key_concepts": ["Server setup", "World creation", "Player management"],
                    "next_guide": "entities"
                },
                "entities": {
                    "title": "Working with Entities",
                    "sections": [
                        {
                            "title": "Entity Basics",
                            "content": "Entities are the building blocks of your game"
                        },
                        {
                            "title": "Creating Entities",
                            "content": "Extend Entity classes and spawn in world"
                        },
                        {
                            "title": "Entity Controllers",
                            "content": "Separate behavior from data with controllers"
                        }
                    ],
                    "key_concepts": ["Entity lifecycle", "Controllers", "Events"],
                    "next_guide": "physics"
                },
                "physics": {
                    "title": "Physics System",
                    "sections": [
                        {
                            "title": "Rigid Bodies",
                            "content": "Add physics to entities with rigid bodies"
                        },
                        {
                            "title": "Colliders",
                            "content": "Define collision shapes and properties"
                        },
                        {
                            "title": "Forces and Impulses",
                            "content": "Apply forces to create realistic movement"
                        }
                    ],
                    "key_concepts": ["RigidBody types", "Collision detection", "Physics optimization"]
                },
                "ui": {
                    "title": "User Interface Development",
                    "sections": [
                        {
                            "title": "HTML/CSS UI",
                            "content": "Create UI with web technologies"
                        },
                        {
                            "title": "Server-Client Communication",
                            "content": "Send data between server and UI"
                        },
                        {
                            "title": "3D Scene UI",
                            "content": "Place UI elements in the game world"
                        }
                    ],
                    "key_concepts": ["UI loading", "Data binding", "Event handling"]
                },
                "networking": {
                    "title": "Networking and Multiplayer",
                    "sections": [
                        {
                            "title": "Automatic Synchronization",
                            "content": "Entity positions and states sync automatically"
                        },
                        {
                            "title": "Custom Data Sync",
                            "content": "Send custom data through UI system"
                        },
                        {
                            "title": "Network Optimization",
                            "content": "Optimize for smooth multiplayer experience"
                        }
                    ],
                    "key_concepts": ["Server authority", "State sync", "Lag compensation"]
                },
                "persistence": {
                    "title": "Data Persistence",
                    "sections": [
                        {
                            "title": "Player Data",
                            "content": "Save and load player progress"
                        },
                        {
                            "title": "World State",
                            "content": "Persist world changes"
                        },
                        {
                            "title": "Data Migration",
                            "content": "Handle schema changes"
                        }
                    ],
                    "key_concepts": ["Save timing", "Data validation", "Versioning"]
                }
            },
            "tutorials": {
                "first-game": {
                    "title": "Build Your First HYTOPIA Game",
                    "steps": [
                        "Set up the project",
                        "Create a world with terrain",
                        "Add player spawning",
                        "Implement basic gameplay",
                        "Test with multiple players"
                    ],
                    "prerequisites": [],
                    "estimated_time": "45 minutes"
                },
                "multiplayer-basics": {
                    "title": "Multiplayer Game Basics",
                    "steps": [
                        "Understanding server authority",
                        "Handling player connections",
                        "Synchronizing game state",
                        "Implementing chat",
                        "Testing with multiple clients"
                    ],
                    "prerequisites": ["first-game"],
                    "estimated_time": "60 minutes"
                },
                "custom-entities": {
                    "title": "Creating Custom Entities",
                    "steps": [
                        "Design entity class structure",
                        "Implement entity behavior",
                        "Add physics and collisions",
                        "Create entity controllers",
                        "Handle entity events"
                    ],
                    "prerequisites": ["first-game"],
                    "estimated_time": "90 minutes"
                }
            },
            "api_reference": {
                "Entity": {
                    "title": "Entity Class Reference",
                    "description": "Base class for all game objects",
                    "examples": [
                        "Basic entity creation",
                        "Entity with physics",
                        "Entity event handling"
                    ],
                    "see_also": ["ModelEntity", "BlockEntity", "EntityManager"]
                },
                "World": {
                    "title": "World Class Reference",
                    "description": "Main game world container",
                    "examples": [
                        "Accessing world managers",
                        "World event handling",
                        "World configuration"
                    ],
                    "see_also": ["WorldManager", "EntityManager", "ChunkLattice"]
                }
            },
            "best_practices": {
                "performance": {
                    "title": "Performance Optimization",
                    "practices": [
                        "Use object pooling for frequently spawned entities",
                        "Implement LOD for distant objects",
                        "Batch operations when possible",
                        "Profile before optimizing",
                        "Use simple colliders"
                    ],
                    "anti_patterns": [
                        "Creating entities every frame",
                        "Complex collision meshes everywhere",
                        "Updating all entities every tick"
                    ]
                },
                "security": {
                    "title": "Security Best Practices",
                    "practices": [
                        "Never trust client input",
                        "Validate all actions server-side",
                        "Sanitize user-generated content",
                        "Rate limit player actions",
                        "Log suspicious behavior"
                    ],
                    "anti_patterns": [
                        "Client-side game logic",
                        "Trusting client positions",
                        "Storing secrets in client code"
                    ]
                },
                "architecture": {
                    "title": "Architecture Best Practices",
                    "practices": [
                        "Separate concerns clearly",
                        "Use composition over inheritance",
                        "Keep controllers focused",
                        "Use events for loose coupling",
                        "Design for testability"
                    ],
                    "anti_patterns": [
                        "God objects",
                        "Tight coupling",
                        "Business logic in entities"
                    ]
                }
            }
        }
    
    def _calculate_doc_relevance(self, query: str, name: str, content: Dict[str, Any]) -> float:
        """Calculate relevance score for documentation"""
        score = 0.0
        
        # Check name
        if query in name.lower():
            score += 3.0
        
        # Check title
        if query in content.get("title", "").lower():
            score += 2.0
        
        # Check sections
        for section in content.get("sections", []):
            if query in section.get("title", "").lower():
                score += 1.5
            if query in section.get("content", "").lower():
                score += 1.0
        
        # Check key concepts
        for concept in content.get("key_concepts", []):
            if query in concept.lower():
                score += 1.5
        
        return score
    
    def _get_content_preview(self, content: Dict[str, Any], query: str) -> str:
        """Get preview of content around query match"""
        # Check sections
        for section in content.get("sections", []):
            if query in section.get("content", "").lower():
                text = section["content"]
                # Find query position and extract surrounding text
                pos = text.lower().find(query)
                if pos != -1:
                    start = max(0, pos - 50)
                    end = min(len(text), pos + len(query) + 50)
                    preview = text[start:end]
                    if start > 0:
                        preview = "..." + preview
                    if end < len(text):
                        preview = preview + "..."
                    return preview
        
        # Fallback to first section
        if content.get("sections"):
            first_content = content["sections"][0].get("content", "")
            return first_content[:100] + "..." if len(first_content) > 100 else first_content
        
        return "No preview available"
    
    def _get_search_tips(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """Get search tips based on results"""
        tips = []
        
        if not results:
            tips.append("Try broader terms like 'entity' or 'physics'")
            tips.append("Browse guides with 'hytopia_get_guide'")
        elif len(results) > 20:
            tips.append("Refine your search with more specific terms")
        
        # Suggest based on result types
        result_types = set(r["type"] for r in results[:5])
        if "guide" in result_types:
            tips.append("Use 'hytopia_get_guide' to read full guides")
        if "tutorial" in result_types:
            tips.append("Use 'hytopia_get_tutorial' for step-by-step instructions")
        
        return tips
    
    def _get_related_guides(self, guide_name: str) -> List[str]:
        """Get guides related to the current one"""
        relations = {
            "getting-started": ["entities", "physics", "ui"],
            "entities": ["physics", "entity-controllers", "events"],
            "physics": ["entities", "collision-detection", "optimization"],
            "ui": ["player-input", "networking", "events"],
            "networking": ["persistence", "optimization", "security"],
            "persistence": ["player-data", "world-state", "networking"]
        }
        return relations.get(guide_name, [])
    
    def _get_next_steps(self, guide_name: str) -> List[str]:
        """Get recommended next steps after reading a guide"""
        next_steps = {
            "getting-started": [
                "Read the entities guide",
                "Try the first-game tutorial",
                "Explore example projects"
            ],
            "entities": [
                "Learn about physics",
                "Implement custom controllers",
                "Study entity patterns"
            ],
            "physics": [
                "Experiment with different colliders",
                "Optimize physics performance",
                "Create physics-based gameplay"
            ]
        }
        return next_steps.get(guide_name, ["Explore related guides", "Try practical examples"])
    
    def _get_next_tutorials(self, tutorial_name: str) -> List[str]:
        """Get recommended next tutorials"""
        progressions = {
            "first-game": ["multiplayer-basics", "custom-entities"],
            "multiplayer-basics": ["game-modes", "advanced-networking"],
            "custom-entities": ["ai-implementation", "complex-behaviors"]
        }
        return progressions.get(tutorial_name, [])
    
    def _format_method_signature(self, method: Dict[str, Any]) -> str:
        """Format method signature"""
        params = []
        for param in method.get("parameters", []):
            param_str = param["name"]
            if param.get("optional"):
                param_str += "?"
            param_str += f": {param.get('type', 'any')}"
            params.append(param_str)
        
        return_type = method.get("returns", {}).get("type", "void")
        return f"{method['name']}({', '.join(params)}): {return_type}"
    
    def _get_common_mistakes(self, topic: str) -> List[str]:
        """Get common mistakes for a topic"""
        mistakes = {
            "performance": [
                "Premature optimization",
                "Not profiling first",
                "Over-engineering solutions"
            ],
            "security": [
                "Trusting client data",
                "Client-side validation only",
                "Exposing internal state"
            ],
            "architecture": [
                "Tight coupling",
                "Not planning for scale",
                "Ignoring SOLID principles"
            ]
        }
        return mistakes.get(topic, [])
    
    def _get_best_practice_examples(self, topic: str) -> List[str]:
        """Get examples demonstrating best practices"""
        examples = {
            "performance": ["object-pooling", "lod-system", "batch-operations"],
            "security": ["input-validation", "rate-limiting", "secure-chat"],
            "architecture": ["modular-systems", "event-driven", "clean-separation"]
        }
        return examples.get(topic, [])