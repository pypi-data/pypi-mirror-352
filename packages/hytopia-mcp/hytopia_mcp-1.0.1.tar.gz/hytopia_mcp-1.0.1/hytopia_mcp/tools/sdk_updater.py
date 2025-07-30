"""
SDK Updater Tools - Keep SDK data up to date from GitHub
"""

from typing import Dict, List, Any, Optional
from fastmcp import FastMCP, Context
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
from ..config import config

class SDKUpdaterTools:
    def __init__(self, mcp: FastMCP, cache_manager, sdk_analyzer):
        self.mcp = mcp
        self.cache_manager = cache_manager
        self.sdk_analyzer = sdk_analyzer
        self._register_tools()
        
        # GitHub API configuration
        self.github_api = "https://api.github.com"
        self.sdk_repo = "hytopiagg/sdk"
        self.examples_repo = "hytopiagg/sdk-examples"
    
    def _register_tools(self):
        @self.mcp.tool()
        async def hytopia_check_updates(
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Check if there are updates available for the HYTOPIA SDK.
            """
            if context:
                await context.info("Checking for SDK updates...")
            
            try:
                # Get current version from cache
                current_version = await self.cache_manager.get("sdk_version")
                last_check = await self.cache_manager.get("last_update_check")
                
                # Check if we've checked recently
                if last_check:
                    last_check_time = datetime.fromisoformat(last_check)
                    if datetime.now() - last_check_time < timedelta(hours=config.sdk_update_check_interval_hours):
                        return {
                            "status": "recently_checked",
                            "last_check": last_check,
                            "current_version": current_version,
                            "message": f"SDK was checked recently (within {config.sdk_update_check_interval_hours} hours). Use force=True to check again."
                        }
                
                # Get latest release info from GitHub
                latest_info = await self._get_latest_release_info()
                
                # Save last check time
                await self.cache_manager.set("last_update_check", datetime.now().isoformat())
                
                if not latest_info:
                    return {
                        "status": "error",
                        "message": "Could not fetch latest release information"
                    }
                
                # Compare versions
                latest_version = latest_info.get("tag_name", "unknown")
                
                update_available = current_version != latest_version if current_version else True
                
                return {
                    "status": "update_available" if update_available else "up_to_date",
                    "current_version": current_version or "unknown",
                    "latest_version": latest_version,
                    "release_date": latest_info.get("published_at"),
                    "release_notes": latest_info.get("body", ""),
                    "update_available": update_available
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "message": "Failed to check for updates"
                }
        
        @self.mcp.tool()
        async def hytopia_update_sdk(
            force: bool = False,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Update the local SDK cache with latest data from GitHub.
            Set force=True to update even if already up to date.
            """
            if context:
                await context.info("Updating SDK data...")
            
            try:
                # Check if update is needed
                if not force:
                    update_check = await hytopia_check_updates()
                    if not update_check.get("update_available"):
                        return {
                            "status": "already_up_to_date",
                            "version": update_check.get("current_version"),
                            "message": "SDK is already up to date"
                        }
                
                # Clear existing cache
                await self.cache_manager.clear()
                
                # Re-initialize SDK analyzer
                await self.sdk_analyzer.initialize()
                
                # Get latest version info
                latest_info = await self._get_latest_release_info()
                latest_version = latest_info.get("tag_name", "unknown") if latest_info else "unknown"
                
                # Save new version
                await self.cache_manager.set("sdk_version", latest_version)
                await self.cache_manager.set("sdk_updated_at", datetime.now().isoformat())
                
                return {
                    "status": "updated",
                    "new_version": latest_version,
                    "updated_at": datetime.now().isoformat(),
                    "message": "SDK cache updated successfully"
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "message": "Failed to update SDK"
                }
        
        @self.mcp.tool()
        async def hytopia_get_changelog(
            limit: int = 5,
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get recent changelog entries for the HYTOPIA SDK.
            """
            if context:
                await context.info("Fetching SDK changelog...")
            
            try:
                # Get recent releases
                releases = await self._get_recent_releases(limit)
                
                if not releases:
                    return {
                        "status": "error",
                        "message": "Could not fetch release history"
                    }
                
                # Format changelog
                changelog = []
                for release in releases:
                    changelog.append({
                        "version": release.get("tag_name"),
                        "date": release.get("published_at"),
                        "name": release.get("name"),
                        "changes": self._parse_release_notes(release.get("body", "")),
                        "is_prerelease": release.get("prerelease", False)
                    })
                
                return {
                    "status": "success",
                    "changelog": changelog,
                    "total_entries": len(changelog)
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "message": "Failed to fetch changelog"
                }
        
        @self.mcp.tool()
        async def hytopia_sdk_status(
            context: Context = None
        ) -> Dict[str, Any]:
            """
            Get current status of the SDK cache and update system.
            """
            try:
                # Get cache info
                cache_info = await self.cache_manager.get_cache_info()
                
                # Get version info
                current_version = await self.cache_manager.get("sdk_version")
                last_update = await self.cache_manager.get("sdk_updated_at")
                last_check = await self.cache_manager.get("last_update_check")
                
                # Check if SDK analyzer is initialized
                analyzer_ready = self.sdk_analyzer._initialized
                
                return {
                    "status": "operational",
                    "cache_status": cache_info,
                    "sdk_version": current_version or "not_cached",
                    "last_updated": last_update or "never",
                    "last_check": last_check or "never",
                    "analyzer_initialized": analyzer_ready,
                    "auto_update": "enabled" if config.sdk_auto_update else "disabled",
                    "update_interval": f"{config.sdk_update_check_interval_hours} hours",
                    "config": {
                        "cache_enabled": config.enable_caching,
                        "cache_ttl_hours": config.cache_ttl_hours,
                        "max_search_results": config.max_search_results
                    }
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "message": "Failed to get SDK status"
                }
    
    async def _check_and_update(self) -> Dict[str, Any]:
        """Internal method to check and update if needed"""
        try:
            # Check for updates
            update_info = await hytopia_check_updates()
            
            if update_info.get("update_available"):
                # Perform update
                return await hytopia_update_sdk()
            else:
                return {
                    "updated": False,
                    "current_version": update_info.get("current_version")
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "updated": False
            }
    
    async def _get_latest_release_info(self) -> Optional[Dict[str, Any]]:
        """Get latest release information from GitHub"""
        try:
            url = f"{self.github_api}/repos/{self.sdk_repo}/releases/latest"
            
            headers = config.get_github_headers()
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
                    
        except Exception:
            return None
    
    async def _get_recent_releases(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent releases from GitHub"""
        try:
            url = f"{self.github_api}/repos/{self.sdk_repo}/releases"
            params = {"per_page": limit}
            
            headers = config.get_github_headers()
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    return []
                    
        except Exception:
            return []
    
    def _parse_release_notes(self, body: str) -> Dict[str, List[str]]:
        """Parse release notes into structured format"""
        sections = {
            "features": [],
            "fixes": [],
            "breaking_changes": [],
            "other": []
        }
        
        if not body:
            return sections
        
        lines = body.split("\n")
        current_section = "other"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if "feature" in line.lower() or "added" in line.lower():
                current_section = "features"
            elif "fix" in line.lower() or "bug" in line.lower():
                current_section = "fixes"
            elif "breaking" in line.lower():
                current_section = "breaking_changes"
            elif line.startswith("-") or line.startswith("*"):
                # Bullet point
                content = line[1:].strip()
                if content:
                    sections[current_section].append(content)
        
        return sections