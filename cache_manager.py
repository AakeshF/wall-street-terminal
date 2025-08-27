"""
Cache Manager
=============
Fast. Efficient. Smart caching.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

class CacheManager:
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 4):
        """Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cached data in hours
        """
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key"""
        # Use hash to handle special characters in symbols
        safe_key = hashlib.md5(key.encode()).hexdigest()[:10]
        return os.path.join(self.cache_dir, f"{key}_{safe_key}.json")
        
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cached data is still valid"""
        if not os.path.exists(cache_path):
            return False
            
        # Check file modification time
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - mod_time
        
        return age < timedelta(hours=self.ttl_hours)
        
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data if available and valid"""
        cache_path = self._get_cache_path(key)
        
        if not self._is_cache_valid(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return data.get('data')
        except Exception:
            return None
            
    def set(self, key: str, data: any) -> bool:
        """Cache data with timestamp"""
        cache_path = self._get_cache_path(key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'key': key,
                'data': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            return True
        except Exception:
            return False
            
    def get_historical_prices(self, symbol: str) -> Optional[List[float]]:
        """Get cached historical prices for a symbol"""
        key = f"{symbol}_historical"
        return self.get(key)
        
    def set_historical_prices(self, symbol: str, prices: List[float]) -> bool:
        """Cache historical prices for a symbol"""
        key = f"{symbol}_historical"
        return self.set(key, prices)
        
    def clear_old_cache(self) -> int:
        """Remove expired cache files"""
        removed = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                if not self._is_cache_valid(filepath):
                    try:
                        os.remove(filepath)
                        removed += 1
                    except:
                        pass
                        
        return removed
        
    def clear_all(self) -> int:
        """Clear all cache files"""
        removed = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(filepath)
                    removed += 1
                except:
                    pass
                    
        return removed