"""
Example Analyzer Tools - Analyze patterns and code examples from HYTOPIA SDK
"""

from typing import Dict, List, Any, Optional
from fastmcp import FastMCP, Context
import re

class ExampleAnalyzerTools:
    def __init__(self, mcp: FastMCP, sdk_analyzer):
        self.mcp = mcp
        self.sdk_analyzer = sdk_analyzer
        self._register_tools()
        
        # Mock example data - in real implementation, this would be fetched from GitHub
        self.examples = self._load_example_data()
    
    def _register_tools(self):
        @self.mcp.tool()
        async def hytopia_find_example_patterns(
            pattern: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Find examples demonstrating specific patterns.
            Patterns: entity-creation, physics, ai, ui, multiplayer, persistence, etc.
            """
            if context:
                await context.info(f"Searching for examples with pattern: {pattern}")
            
            pattern_lower = pattern.lower()
            matching_examples = []
            
            for example_name, example_data in self.examples.items():
                if any(pattern_lower in tag.lower() for tag in example_data.get("tags", [])):
                    matching_examples.append({
                        "name": example_name,
                        "description": example_data["description"],
                        "difficulty": example_data.get("difficulty", "medium"),
                        "key_concepts": example_data.get("key_concepts", []),
                        "files": example_data.get("main_files", [])
                    })
            
            if not matching_examples:
                return {
                    "pattern": pattern,
                    "found": 0,
                    "examples": [],
                    "suggestion": "Try broader terms like 'entity', 'physics', or 'ui'"
                }
            
            return {
                "pattern": pattern,
                "found": len(matching_examples),
                "examples": matching_examples,
                "usage_tips": self._get_pattern_usage_tips(pattern_lower)
            }
        
        @self.mcp.tool()
        async def hytopia_analyze_example(
            example_name: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Analyze a specific example to understand its implementation.
            Returns structure, patterns used, and learning points.
            """
            if context:
                await context.info(f"Analyzing example: {example_name}")
            
            example = self.examples.get(example_name)
            if not example:
                similar = self._find_similar_examples(example_name)
                return {
                    "error": f"Example '{example_name}' not found",
                    "similar_examples": similar,
                    "available_examples": list(self.examples.keys())[:10]
                }
            
            analysis = {
                "example": example_name,
                "description": example["description"],
                "difficulty": example.get("difficulty", "medium"),
                "structure": self._analyze_structure(example),
                "patterns": self._analyze_patterns(example),
                "key_concepts": example.get("key_concepts", []),
                "learning_points": self._extract_learning_points(example),
                "code_snippets": self._extract_key_snippets(example),
                "customization_guide": self._get_customization_guide(example)
            }
            
            return analysis
        
        @self.mcp.tool()
        async def hytopia_list_examples_by_topic(
            topic: str = None,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            List all examples organized by topic.
            Topics: gameplay, entities, physics, ui, networking, audio, persistence
            """
            topics = {
                "gameplay": [
                    "zombies-fps",
                    "hole-in-wall",
                    "payload-game",
                    "wall-dodge",
                    "frontiers-rpg"
                ],
                "entities": [
                    "entity-spawn",
                    "entity-controller",
                    "entity-animations",
                    "child-entity",
                    "block-entity"
                ],
                "physics": [
                    "physics-basic",
                    "collision-detection",
                    "rigid-bodies",
                    "forces-impulses"
                ],
                "ui": [
                    "custom-ui",
                    "hud-example",
                    "menu-system",
                    "inventory-ui"
                ],
                "networking": [
                    "multiplayer-sync",
                    "player-persistence",
                    "chat-system",
                    "team-management"
                ],
                "ai": [
                    "ai-agents",
                    "pathfinding",
                    "state-machine-ai",
                    "enemy-behavior"
                ],
                "world": [
                    "world-generation",
                    "world-switching",
                    "chunk-management",
                    "terrain-modification"
                ]
            }
            
            if topic:
                topic_lower = topic.lower()
                if topic_lower not in topics:
                    return {
                        "error": f"Unknown topic: {topic}",
                        "available_topics": list(topics.keys())
                    }
                
                examples = []
                for example_name in topics[topic_lower]:
                    if example_name in self.examples:
                        examples.append({
                            "name": example_name,
                            "description": self.examples[example_name]["description"],
                            "difficulty": self.examples[example_name].get("difficulty", "medium")
                        })
                
                return {
                    "topic": topic,
                    "examples": examples,
                    "learning_path": self._get_learning_path(topic_lower)
                }
            
            # Return all topics
            return {
                "topics": {
                    topic: len(examples) for topic, examples in topics.items()
                },
                "total_examples": sum(len(examples) for examples in topics.values()),
                "usage": "Specify a topic to see examples, e.g., hytopia_list_examples_by_topic('entities')"
            }
        
        @self.mcp.tool()
        async def hytopia_get_example_structure(
            example_name: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get the file structure and organization of an example project.
            """
            example = self.examples.get(example_name)
            if not example:
                return {
                    "error": f"Example '{example_name}' not found"
                }
            
            structure = example.get("structure", {})
            
            return {
                "example": example_name,
                "structure": structure,
                "entry_point": example.get("entry_point", "index.ts"),
                "dependencies": example.get("dependencies", []),
                "setup_instructions": self._get_setup_instructions(example_name)
            }
    
    def _load_example_data(self) -> Dict[str, Any]:
        """Load example data (mock for now)"""
        return {
            "zombies-fps": {
                "description": "First-person shooter with zombie enemies",
                "difficulty": "advanced",
                "tags": ["gameplay", "combat", "ai", "fps"],
                "key_concepts": [
                    "Enemy AI with state machines",
                    "Projectile physics",
                    "Health and damage systems",
                    "Wave spawning"
                ],
                "main_files": ["ZombieEntity.ts", "PlayerController.ts", "GameManager.ts"],
                "structure": {
                    "entities/": "Game entities (zombies, projectiles)",
                    "controllers/": "Entity controllers",
                    "systems/": "Game systems (health, spawning)",
                    "ui/": "HUD and menus"
                }
            },
            "entity-spawn": {
                "description": "Basic entity spawning and management",
                "difficulty": "beginner",
                "tags": ["entities", "spawning", "basics"],
                "key_concepts": [
                    "Entity creation",
                    "Spawn positions",
                    "Entity lifecycle",
                    "Basic properties"
                ],
                "main_files": ["index.ts", "MyEntity.ts"],
                "structure": {
                    "index.ts": "Main server file",
                    "entities/": "Entity definitions"
                }
            },
            "pathfinding": {
                "description": "AI pathfinding demonstration",
                "difficulty": "intermediate",
                "tags": ["ai", "pathfinding", "navigation"],
                "key_concepts": [
                    "PathfindingEntityController",
                    "Navigation mesh",
                    "Obstacle avoidance",
                    "Target following"
                ],
                "main_files": ["PathfindingNPC.ts", "NavigationSetup.ts"],
                "patterns": {
                    "pathfinding_setup": {
                        "description": "Initialize pathfinding controller",
                        "code_pattern": "entity.setController(new PathfindingEntityController())"
                    },
                    "navigation": {
                        "description": "Navigate to target",
                        "code_pattern": "controller.pathfind({ target, onComplete })"
                    }
                }
            },
            "custom-ui": {
                "description": "Custom UI implementation with HTML/CSS",
                "difficulty": "intermediate",
                "tags": ["ui", "hud", "interface"],
                "key_concepts": [
                    "HTML/CSS UI creation",
                    "Server-client communication",
                    "UI data binding",
                    "Event handling"
                ],
                "main_files": ["ui/index.html", "ui/ui.js", "UIManager.ts"],
                "structure": {
                    "ui/": "HTML/CSS/JS files",
                    "server/": "Server-side UI logic"
                }
            },
            "ai-agents": {
                "description": "Intelligent NPCs with behavior patterns",
                "difficulty": "advanced",
                "tags": ["ai", "npc", "behavior"],
                "key_concepts": [
                    "State machine AI",
                    "Behavior trees",
                    "Decision making",
                    "Environmental awareness"
                ],
                "main_files": ["AIController.ts", "BehaviorTree.ts", "StateManager.ts"]
            },
            "world-switching": {
                "description": "Multiple worlds and transitions",
                "difficulty": "intermediate",
                "tags": ["world", "level", "transition"],
                "key_concepts": [
                    "World management",
                    "Player transitions",
                    "State preservation",
                    "Loading screens"
                ],
                "main_files": ["WorldManager.ts", "TransitionHandler.ts"]
            },
            "player-persistence": {
                "description": "Save and load player progress",
                "difficulty": "intermediate",
                "tags": ["persistence", "save", "data"],
                "key_concepts": [
                    "Data serialization",
                    "Save/load mechanics",
                    "Version migration",
                    "Data validation"
                ],
                "main_files": ["PersistenceManager.ts", "PlayerData.ts"]
            }
        }
    
    def _find_similar_examples(self, query: str) -> List[str]:
        """Find examples with similar names"""
        query_lower = query.lower()
        similar = []
        
        for example_name in self.examples:
            if query_lower in example_name.lower():
                similar.append(example_name)
        
        return similar[:5]
    
    def _analyze_structure(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure of an example"""
        return {
            "directories": example.get("structure", {}),
            "entry_point": example.get("entry_point", "index.ts"),
            "file_count": len(example.get("main_files", [])),
            "organization": self._determine_organization_pattern(example)
        }
    
    def _determine_organization_pattern(self, example: Dict[str, Any]) -> str:
        """Determine the organizational pattern used"""
        structure = example.get("structure", {})
        
        if "entities/" in structure and "controllers/" in structure:
            return "MVC-style separation"
        elif "systems/" in structure:
            return "System-based architecture"
        elif all(key.endswith(".ts") for key in structure):
            return "Flat structure"
        else:
            return "Domain-based organization"
    
    def _analyze_patterns(self, example: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns used in the example"""
        patterns = []
        
        # Check for common patterns based on tags and concepts
        tags = example.get("tags", [])
        concepts = example.get("key_concepts", [])
        
        if "ai" in tags:
            patterns.append({
                "pattern": "AI Controller",
                "usage": "Separate AI logic into dedicated controllers",
                "benefits": "Reusable, testable AI behaviors"
            })
        
        if "ui" in tags:
            patterns.append({
                "pattern": "Server-Client UI Communication",
                "usage": "player.ui.sendData() and message handlers",
                "benefits": "Synchronized UI state"
            })
        
        if any("persistence" in concept.lower() for concept in concepts):
            patterns.append({
                "pattern": "Data Persistence",
                "usage": "player.setPersistedData() for saving",
                "benefits": "Automatic save/load handling"
            })
        
        return patterns
    
    def _extract_learning_points(self, example: Dict[str, Any]) -> List[str]:
        """Extract key learning points from an example"""
        learning_points = []
        
        # Base learning points on difficulty
        difficulty = example.get("difficulty", "medium")
        
        if difficulty == "beginner":
            learning_points.extend([
                "Basic HYTOPIA concepts and setup",
                "Simple entity creation and management",
                "Event handling fundamentals"
            ])
        elif difficulty == "intermediate":
            learning_points.extend([
                "Advanced entity patterns",
                "System integration",
                "Performance considerations"
            ])
        else:  # advanced
            learning_points.extend([
                "Complex architectural patterns",
                "Optimization techniques",
                "Production-ready implementations"
            ])
        
        # Add specific learning points based on tags
        tags = example.get("tags", [])
        if "ai" in tags:
            learning_points.append("AI behavior implementation patterns")
        if "physics" in tags:
            learning_points.append("Physics system integration")
        if "ui" in tags:
            learning_points.append("Client-server UI synchronization")
        
        return learning_points
    
    def _extract_key_snippets(self, example: Dict[str, Any]) -> Dict[str, str]:
        """Extract key code snippets that demonstrate patterns"""
        snippets = {}
        
        # Mock snippets based on example type
        if "entity-spawn" in example.get("name", ""):
            snippets["entity_creation"] = """// Create and spawn entity
const entity = new MyEntity(world, {
    position: new Vector3(0, 0, 0),
    modelUri: 'models/my-model.glb'
});
entity.spawn();"""
        
        if "ai" in example.get("tags", []):
            snippets["ai_controller"] = """// AI Controller setup
class EnemyAIController extends BaseEntityController {
    tick() {
        // AI logic here
        this.updateState();
        this.findTarget();
        this.executeAction();
    }
}"""
        
        if "ui" in example.get("tags", []):
            snippets["ui_communication"] = """// Send data to UI
player.ui.sendData({
    type: 'update_health',
    health: player.health,
    maxHealth: player.maxHealth
});"""
        
        return snippets
    
    def _get_customization_guide(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Get guide for customizing the example"""
        return {
            "easy_modifications": self._get_easy_mods(example),
            "intermediate_modifications": self._get_intermediate_mods(example),
            "advanced_modifications": self._get_advanced_mods(example)
        }
    
    def _get_easy_mods(self, example: Dict[str, Any]) -> List[str]:
        """Get easy modifications for the example"""
        mods = ["Change entity models and textures", "Adjust spawn positions", "Modify game parameters"]
        
        tags = example.get("tags", [])
        if "ui" in tags:
            mods.append("Customize UI colors and layout")
        if "ai" in tags:
            mods.append("Adjust AI difficulty parameters")
        
        return mods
    
    def _get_intermediate_mods(self, example: Dict[str, Any]) -> List[str]:
        """Get intermediate modifications"""
        return [
            "Add new entity types",
            "Implement additional game mechanics",
            "Extend existing systems",
            "Add multiplayer features"
        ]
    
    def _get_advanced_mods(self, example: Dict[str, Any]) -> List[str]:
        """Get advanced modifications"""
        return [
            "Refactor architecture for scalability",
            "Implement custom physics behaviors",
            "Create procedural content generation",
            "Add complex AI behaviors"
        ]
    
    def _get_pattern_usage_tips(self, pattern: str) -> List[str]:
        """Get tips for using a pattern"""
        tips = {
            "entity": [
                "Start with simple entities and add complexity",
                "Use composition over inheritance",
                "Keep entity logic minimal, use controllers"
            ],
            "physics": [
                "Choose the right rigid body type",
                "Use simple colliders when possible",
                "Test physics interactions thoroughly"
            ],
            "ai": [
                "Begin with state machines",
                "Add complexity incrementally",
                "Profile AI performance impact"
            ],
            "ui": [
                "Keep UI updates minimal and batched",
                "Use CSS for animations when possible",
                "Handle connection loss gracefully"
            ]
        }
        
        return tips.get(pattern, ["Study the example carefully", "Experiment with modifications", "Test in multiplayer"])
    
    def _get_learning_path(self, topic: str) -> List[str]:
        """Get recommended learning path for a topic"""
        paths = {
            "entities": [
                "1. Start with entity-spawn example",
                "2. Move to entity-controller",
                "3. Try entity-animations",
                "4. Explore child-entity relationships"
            ],
            "ai": [
                "1. Begin with simple state machines",
                "2. Implement pathfinding",
                "3. Add decision-making logic",
                "4. Create complex behaviors"
            ],
            "ui": [
                "1. Create basic HUD elements",
                "2. Implement interactive menus",
                "3. Add data binding",
                "4. Build complex UI systems"
            ]
        }
        
        return paths.get(topic, ["1. Start with basic examples", "2. Gradually increase complexity", "3. Combine patterns"])
    
    def _get_setup_instructions(self, example_name: str) -> List[str]:
        """Get setup instructions for an example"""
        return [
            f"1. Clone the example: git clone [example-repo]/{example_name}",
            "2. Install dependencies: npm install",
            "3. Configure any required settings",
            "4. Run the server: npm run dev",
            "5. Connect with Claude Desktop or browser"
        ]