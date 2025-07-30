"""
Search Tools - Unified search across HYTOPIA SDK resources
"""

from typing import Dict, List, Any, Optional, Set
from fastmcp import FastMCP, Context
import re
from difflib import SequenceMatcher

class SearchTools:
    def __init__(self, mcp: FastMCP, sdk_analyzer):
        self.mcp = mcp
        self.sdk_analyzer = sdk_analyzer
        self._register_tools()
    
    def _register_tools(self):
        @self.mcp.tool()
        async def hytopia_search_all(
            query: str,
            limit: int = 10,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Search across all HYTOPIA resources (API, docs, examples).
            Returns ranked results from all sources.
            """
            if context:
                await context.info(f"Searching for: {query}")
            
            # Normalize query
            query_lower = query.lower()
            query_words = query_lower.split()
            
            results = {
                "api": await self._search_api(query_lower, query_words),
                "patterns": self._search_patterns(query_lower, query_words),
                "concepts": self._search_concepts(query_lower, query_words),
                "examples": self._search_examples(query_lower, query_words)
            }
            
            # Combine and rank results
            all_results = []
            
            for category, items in results.items():
                for item in items:
                    item["category"] = category
                    item["score"] = self._calculate_relevance_score(query_lower, item)
                    all_results.append(item)
            
            # Sort by score and limit
            all_results.sort(key=lambda x: x["score"], reverse=True)
            top_results = all_results[:limit]
            
            return {
                "query": query,
                "total_found": len(all_results),
                "showing": len(top_results),
                "results": top_results,
                "categories": {k: len(v) for k, v in results.items()},
                "suggestions": self._get_search_suggestions(query, all_results)
            }
        
        @self.mcp.tool()
        async def hytopia_find_related(
            item_type: str,
            item_name: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Find items related to a specific API element, pattern, or concept.
            Types: class, method, pattern, concept, example
            """
            if context:
                await context.info(f"Finding items related to {item_type}: {item_name}")
            
            related = {
                "directly_related": [],
                "similar": [],
                "used_together": [],
                "examples": []
            }
            
            if item_type == "class":
                related["directly_related"] = await self._find_related_classes(item_name)
                related["similar"] = await self._find_similar_classes(item_name)
                related["used_together"] = self._find_commonly_used_with(item_name)
                related["examples"] = self._find_examples_using(item_name)
            
            elif item_type == "method":
                class_name, method_name = self._parse_method_reference(item_name)
                related["directly_related"] = await self._find_related_methods(class_name, method_name)
                related["similar"] = self._find_similar_methods(method_name)
                related["used_together"] = self._find_methods_used_together(class_name, method_name)
            
            elif item_type == "pattern":
                related["similar"] = self._find_similar_patterns(item_name)
                related["examples"] = self._find_pattern_examples(item_name)
                related["concepts"] = self._find_related_concepts_for_pattern(item_name)
            
            elif item_type == "concept":
                related["directly_related"] = self._find_related_concepts(item_name)
                related["api_elements"] = await self._find_api_for_concept(item_name)
                related["examples"] = self._find_concept_examples(item_name)
            
            return {
                "item_type": item_type,
                "item_name": item_name,
                "related": related,
                "usage_context": self._get_usage_context(item_type, item_name)
            }
        
        @self.mcp.tool()
        async def hytopia_search_by_use_case(
            use_case: str,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Search for resources based on what you want to accomplish.
            Examples: "create npc", "add physics", "save player data", "make ui"
            """
            if context:
                await context.info(f"Searching for use case: {use_case}")
            
            # Parse use case into action and target
            action, target = self._parse_use_case(use_case)
            
            resources = {
                "relevant_classes": [],
                "relevant_methods": [],
                "patterns": [],
                "examples": [],
                "steps": []
            }
            
            # Map common use cases
            use_case_mappings = {
                ("create", "npc"): {
                    "classes": ["ModelEntity", "BaseEntityController"],
                    "patterns": ["npc_entity", "ai_controller"],
                    "examples": ["ai-agents", "entity-spawn"],
                    "steps": [
                        "1. Create entity class extending ModelEntity",
                        "2. Implement AI controller",
                        "3. Add interaction logic",
                        "4. Spawn in world"
                    ]
                },
                ("add", "physics"): {
                    "classes": ["RigidBody", "Collider"],
                    "methods": ["setRigidBody", "onCollision"],
                    "patterns": ["physics-based", "collision-detection"],
                    "examples": ["physics-basic"],
                    "steps": [
                        "1. Create rigid body configuration",
                        "2. Add colliders",
                        "3. Set physics properties",
                        "4. Handle collisions"
                    ]
                },
                ("save", "player"): {
                    "classes": ["Player", "PersistenceManager"],
                    "methods": ["setPersistedData", "getPersistedData"],
                    "patterns": ["player_persistence"],
                    "examples": ["player-persistence"],
                    "steps": [
                        "1. Define data schema",
                        "2. Save on key events",
                        "3. Load on player join",
                        "4. Handle migrations"
                    ]
                },
                ("make", "ui"): {
                    "classes": ["PlayerUI", "SceneUI"],
                    "methods": ["ui.load", "ui.sendData"],
                    "patterns": ["ui_hud", "ui_menu"],
                    "examples": ["custom-ui"],
                    "steps": [
                        "1. Create HTML/CSS files",
                        "2. Load UI on player join",
                        "3. Send data from server",
                        "4. Handle UI events"
                    ]
                },
                ("spawn", "entity"): {
                    "classes": ["Entity", "EntityManager"],
                    "methods": ["spawn", "despawn"],
                    "patterns": ["entity_lifecycle"],
                    "examples": ["entity-spawn"],
                    "steps": [
                        "1. Create entity instance",
                        "2. Set initial properties",
                        "3. Call spawn()",
                        "4. Handle lifecycle events"
                    ]
                },
                ("move", "player"): {
                    "classes": ["PlayerEntity", "DefaultPlayerEntityController"],
                    "methods": ["setPosition", "tickWithPlayerInput"],
                    "patterns": ["player_controller", "movement"],
                    "examples": ["player-movement"],
                    "steps": [
                        "1. Get player input",
                        "2. Process in controller",
                        "3. Apply movement",
                        "4. Sync with clients"
                    ]
                }
            }
            
            # Find best match
            best_match = None
            best_score = 0
            
            for (mapped_action, mapped_target), mapping in use_case_mappings.items():
                score = 0
                if action.lower() == mapped_action:
                    score += 2
                if target.lower() in mapped_target:
                    score += 2
                if mapped_action in use_case.lower():
                    score += 1
                if mapped_target in use_case.lower():
                    score += 1
                
                if score > best_score:
                    best_score = score
                    best_match = mapping
            
            if best_match:
                resources.update(best_match)
            else:
                # Fallback to general search
                api_results = await self.sdk_analyzer.search_api(use_case)
                resources["relevant_classes"] = api_results.get("classes", [])[:5]
                resources["relevant_methods"] = api_results.get("methods", [])[:5]
                resources["suggestion"] = "Try more specific terms or browse examples"
            
            return {
                "use_case": use_case,
                "action": action,
                "target": target,
                "resources": resources,
                "confidence": "high" if best_score >= 3 else "medium" if best_score >= 1 else "low"
            }
    
    async def _search_api(self, query: str, query_words: List[str]) -> List[Dict[str, Any]]:
        """Search API elements"""
        results = []
        api_results = await self.sdk_analyzer.search_api(query)
        
        # Format class results
        for class_name in api_results.get("classes", []):
            results.append({
                "type": "class",
                "name": class_name,
                "description": f"Class: {class_name}",
                "path": f"hytopia.{class_name}"
            })
        
        # Format method results
        for method_info in api_results.get("methods", []):
            results.append({
                "type": "method",
                "name": f"{method_info['class']}.{method_info['method']}",
                "description": f"Method in {method_info['class']}",
                "path": f"hytopia.{method_info['class']}.{method_info['method']}"
            })
        
        return results
    
    def _search_patterns(self, query: str, query_words: List[str]) -> List[Dict[str, Any]]:
        """Search patterns"""
        results = []
        
        # Pattern definitions
        patterns = {
            "entity_creation": ["entity", "create", "spawn"],
            "controller_setup": ["controller", "behavior", "ai"],
            "physics_setup": ["physics", "rigid", "body", "collider"],
            "ui_implementation": ["ui", "interface", "hud", "menu"],
            "persistence": ["save", "load", "persist", "data"],
            "networking": ["network", "sync", "multiplayer"],
            "event_handling": ["event", "listener", "handler", "on"]
        }
        
        for pattern_name, keywords in patterns.items():
            if any(word in keywords for word in query_words):
                results.append({
                    "type": "pattern",
                    "name": pattern_name,
                    "description": f"Pattern: {pattern_name.replace('_', ' ').title()}",
                    "path": f"patterns.{pattern_name}"
                })
        
        return results
    
    def _search_concepts(self, query: str, query_words: List[str]) -> List[Dict[str, Any]]:
        """Search concepts"""
        results = []
        
        concepts = [
            "server-authoritative",
            "entity-system",
            "event-driven",
            "physics",
            "networking",
            "persistence",
            "chunk-system",
            "multiplayer"
        ]
        
        for concept in concepts:
            if any(word in concept.lower() for word in query_words):
                results.append({
                    "type": "concept",
                    "name": concept,
                    "description": f"Concept: {concept.replace('-', ' ').title()}",
                    "path": f"concepts.{concept}"
                })
        
        return results
    
    def _search_examples(self, query: str, query_words: List[str]) -> List[Dict[str, Any]]:
        """Search examples"""
        results = []
        
        # Mock example data
        examples = [
            {"name": "entity-spawn", "tags": ["entity", "spawn", "basic"]},
            {"name": "ai-agents", "tags": ["ai", "npc", "behavior"]},
            {"name": "custom-ui", "tags": ["ui", "interface", "hud"]},
            {"name": "player-persistence", "tags": ["save", "load", "data"]},
            {"name": "physics-basic", "tags": ["physics", "collision", "rigid"]}
        ]
        
        for example in examples:
            if any(word in example["name"] or any(word in tag for tag in example["tags"]) for word in query_words):
                results.append({
                    "type": "example",
                    "name": example["name"],
                    "description": f"Example: {example['name'].replace('-', ' ').title()}",
                    "path": f"examples.{example['name']}"
                })
        
        return results
    
    def _calculate_relevance_score(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate relevance score for a result"""
        score = 0.0
        
        # Exact match in name
        if query in result["name"].lower():
            score += 5.0
        
        # Partial match in name
        elif any(word in result["name"].lower() for word in query.split()):
            score += 3.0
        
        # Match in description
        if query in result.get("description", "").lower():
            score += 2.0
        
        # Use SequenceMatcher for fuzzy matching
        matcher = SequenceMatcher(None, query, result["name"].lower())
        score += matcher.ratio() * 2
        
        # Boost based on type
        type_boost = {
            "class": 1.5,
            "method": 1.3,
            "pattern": 1.2,
            "example": 1.1,
            "concept": 1.0
        }
        score *= type_boost.get(result.get("type", ""), 1.0)
        
        return score
    
    def _get_search_suggestions(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """Get search suggestions based on results"""
        suggestions = []
        
        if not results:
            suggestions.append("Try broader terms like 'entity' or 'player'")
            suggestions.append("Use 'hytopia_list_modules' to browse available APIs")
        elif len(results) > 20:
            suggestions.append("Try more specific terms to narrow results")
            suggestions.append("Add context like 'player movement' or 'entity spawn'")
        
        # Suggest related searches based on top results
        if results:
            top_types = set(r["type"] for r in results[:5])
            if "class" in top_types:
                suggestions.append("Use 'hytopia_explore_class' for detailed class info")
            if "pattern" in top_types:
                suggestions.append("Use 'hytopia_entity_patterns' for pattern details")
        
        return suggestions
    
    async def _find_related_classes(self, class_name: str) -> List[str]:
        """Find classes directly related to the given class"""
        relations = {
            "Entity": ["EntityManager", "BaseEntityController", "ModelEntity", "BlockEntity"],
            "World": ["WorldManager", "ChunkLattice", "EntityManager", "AudioManager"],
            "Player": ["PlayerEntity", "PlayerInput", "PlayerCamera", "PlayerUI"],
            "RigidBody": ["Collider", "Simulation", "Entity"]
        }
        return relations.get(class_name, [])
    
    async def _find_similar_classes(self, class_name: str) -> List[str]:
        """Find classes similar to the given class"""
        if "Entity" in class_name:
            return ["ModelEntity", "BlockEntity", "PlayerEntity"]
        elif "Controller" in class_name:
            return ["BaseEntityController", "SimpleEntityController", "PathfindingEntityController"]
        elif "Manager" in class_name:
            return ["EntityManager", "AudioManager", "PlayerManager", "WorldManager"]
        return []
    
    def _find_commonly_used_with(self, class_name: str) -> List[str]:
        """Find classes commonly used together"""
        common_pairs = {
            "Entity": ["BaseEntityController", "RigidBody", "Collider"],
            "World": ["EntityManager", "Player", "ChunkLattice"],
            "Player": ["PlayerEntity", "PlayerUI", "PlayerInput"]
        }
        return common_pairs.get(class_name, [])
    
    def _find_examples_using(self, class_name: str) -> List[str]:
        """Find examples that use the given class"""
        class_examples = {
            "Entity": ["entity-spawn", "entity-controller"],
            "BaseEntityController": ["ai-agents", "entity-controller"],
            "PlayerUI": ["custom-ui", "hud-example"],
            "RigidBody": ["physics-basic", "collision-detection"]
        }
        return class_examples.get(class_name, [])
    
    def _parse_method_reference(self, reference: str) -> tuple:
        """Parse method reference like 'Entity.spawn' into class and method"""
        parts = reference.split(".")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return "", reference
    
    async def _find_related_methods(self, class_name: str, method_name: str) -> List[str]:
        """Find methods related to the given method"""
        related = {
            ("Entity", "spawn"): ["despawn", "setPosition", "setController"],
            ("Entity", "setPosition"): ["getPosition", "setRotation", "move"],
            ("Player", "ui.load"): ["ui.sendData", "ui.on"]
        }
        return related.get((class_name, method_name), [])
    
    def _find_similar_methods(self, method_name: str) -> List[str]:
        """Find methods with similar names across classes"""
        if method_name.startswith("get"):
            return ["getPosition", "getRotation", "getHealth"]
        elif method_name.startswith("set"):
            return ["setPosition", "setRotation", "setHealth"]
        elif "spawn" in method_name:
            return ["spawn", "despawn", "respawn"]
        return []
    
    def _find_methods_used_together(self, class_name: str, method_name: str) -> List[str]:
        """Find methods commonly used together"""
        method_groups = {
            ("Entity", "spawn"): ["setPosition", "setController", "setRigidBody"],
            ("Entity", "setRigidBody"): ["addCollider", "setMass", "applyImpulse"],
            ("Player", "ui.load"): ["ui.sendData", "ui.on"]
        }
        return method_groups.get((class_name, method_name), [])
    
    def _find_similar_patterns(self, pattern_name: str) -> List[str]:
        """Find similar patterns"""
        if "entity" in pattern_name:
            return ["entity_creation", "entity_lifecycle", "entity_controller"]
        elif "ui" in pattern_name:
            return ["ui_hud", "ui_menu", "ui_communication"]
        return []
    
    def _find_pattern_examples(self, pattern_name: str) -> List[str]:
        """Find examples demonstrating a pattern"""
        pattern_examples = {
            "entity_creation": ["entity-spawn", "npc-creation"],
            "physics": ["physics-basic", "collision-detection"],
            "ui": ["custom-ui", "hud-example"]
        }
        
        for pattern, examples in pattern_examples.items():
            if pattern in pattern_name:
                return examples
        return []
    
    def _find_related_concepts_for_pattern(self, pattern_name: str) -> List[str]:
        """Find concepts related to a pattern"""
        if "entity" in pattern_name:
            return ["entity-system", "event-driven"]
        elif "physics" in pattern_name:
            return ["physics", "collision-detection"]
        elif "network" in pattern_name:
            return ["server-authoritative", "networking"]
        return []
    
    def _find_related_concepts(self, concept_name: str) -> List[str]:
        """Find related concepts"""
        concept_relations = {
            "server-authoritative": ["networking", "multiplayer"],
            "entity-system": ["event-driven", "component-based"],
            "physics": ["collision-detection", "rigid-bodies"]
        }
        return concept_relations.get(concept_name, [])
    
    async def _find_api_for_concept(self, concept_name: str) -> List[str]:
        """Find API elements related to a concept"""
        concept_apis = {
            "server-authoritative": ["World", "Player", "Entity"],
            "entity-system": ["Entity", "EntityManager", "BaseEntityController"],
            "physics": ["RigidBody", "Collider", "Simulation"]
        }
        return concept_apis.get(concept_name, [])
    
    def _find_concept_examples(self, concept_name: str) -> List[str]:
        """Find examples demonstrating a concept"""
        concept_examples = {
            "server-authoritative": ["multiplayer-sync", "player-input"],
            "entity-system": ["entity-spawn", "entity-controller"],
            "physics": ["physics-basic", "forces-example"]
        }
        return concept_examples.get(concept_name, [])
    
    def _get_usage_context(self, item_type: str, item_name: str) -> str:
        """Get context about how to use an item"""
        if item_type == "class":
            return f"Use 'hytopia_explore_class(\"{item_name}\")' for detailed information"
        elif item_type == "method":
            return f"Use 'hytopia_get_method_details' for signature and examples"
        elif item_type == "pattern":
            return f"Use pattern analysis tools to understand implementation"
        elif item_type == "concept":
            return f"Use 'hytopia_explain_concept(\"{item_name}\")' for explanation"
        return "Explore related items to understand usage"
    
    def _parse_use_case(self, use_case: str) -> tuple:
        """Parse use case into action and target"""
        words = use_case.lower().split()
        
        # Common action words
        actions = ["create", "make", "add", "implement", "build", "setup", "spawn", "move", "save", "load"]
        
        action = "create"  # default
        target = use_case  # default to full string
        
        for word in words:
            if word in actions:
                action = word
                # Everything after action is target
                idx = words.index(word)
                if idx < len(words) - 1:
                    target = " ".join(words[idx + 1:])
                break
        
        return action, target