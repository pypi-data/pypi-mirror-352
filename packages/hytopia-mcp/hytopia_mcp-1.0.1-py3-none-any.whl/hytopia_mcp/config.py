"""
Configuration management for HYTOPIA MCP
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class Config:
    """Configuration manager for HYTOPIA MCP"""
    
    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        # Cache settings
        self.cache_dir = Path(os.path.expanduser(
            os.getenv('CACHE_DIR', '~/.cache/hytopia-mcp')
        ))
        self.cache_max_size_mb = int(os.getenv('CACHE_MAX_SIZE_MB', '500'))
        self.cache_ttl_hours = int(os.getenv('CACHE_TTL_HOURS', '24'))
        
        # SDK settings
        self.sdk_auto_update = os.getenv('SDK_AUTO_UPDATE', 'false').lower() == 'true'
        self.sdk_update_check_interval_hours = int(
            os.getenv('SDK_UPDATE_CHECK_INTERVAL_HOURS', '6')
        )
        self.sdk_github_token = os.getenv('SDK_GITHUB_TOKEN', '').strip() or None
        
        # Performance settings
        self.max_search_results = int(os.getenv('MAX_SEARCH_RESULTS', '20'))
        self.enable_caching = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        self.cache_preload = os.getenv('CACHE_PRELOAD', 'true').lower() == 'true'
        
        # Development settings
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'info').upper()
        self.log_file = Path(os.path.expanduser(
            os.getenv('LOG_FILE', '~/.logs/hytopia-mcp/server.log')
        ))
        
        # API settings
        self.api_timeout_seconds = int(os.getenv('API_TIMEOUT_SECONDS', '30'))
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
        
        # Feature flags
        self.enable_experimental_features = os.getenv(
            'ENABLE_EXPERIMENTAL_FEATURES', 'false'
        ).lower() == 'true'
        self.enable_typescript_parsing = os.getenv(
            'ENABLE_TYPESCRIPT_PARSING', 'true'
        ).lower() == 'true'
        self.enable_example_analysis = os.getenv(
            'ENABLE_EXAMPLE_ANALYSIS', 'true'
        ).lower() == 'true'
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if self.log_file.parent:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_github_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'HYTOPIA-MCP/1.0'
        }
        if self.sdk_github_token:
            headers['Authorization'] = f'token {self.sdk_github_token}'
        return headers
    
    def get_cache_path(self, key: str) -> Path:
        """Get full path for a cache key"""
        # Sanitize key to prevent directory traversal
        safe_key = key.replace('/', '_').replace('\\', '_').replace('..', '_')
        return self.cache_dir / f"{safe_key}.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for debugging"""
        return {
            'cache': {
                'dir': str(self.cache_dir),
                'max_size_mb': self.cache_max_size_mb,
                'ttl_hours': self.cache_ttl_hours,
                'enabled': self.enable_caching,
                'preload': self.cache_preload
            },
            'sdk': {
                'auto_update': self.sdk_auto_update,
                'update_check_interval_hours': self.sdk_update_check_interval_hours,
                'has_github_token': bool(self.sdk_github_token)
            },
            'performance': {
                'max_search_results': self.max_search_results,
                'max_concurrent_requests': self.max_concurrent_requests,
                'api_timeout_seconds': self.api_timeout_seconds
            },
            'development': {
                'debug': self.debug,
                'log_level': self.log_level,
                'log_file': str(self.log_file)
            },
            'features': {
                'experimental': self.enable_experimental_features,
                'typescript_parsing': self.enable_typescript_parsing,
                'example_analysis': self.enable_example_analysis
            }
        }

# Global config instance
config = Config()