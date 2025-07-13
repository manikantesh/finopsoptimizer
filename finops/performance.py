"""
Performance optimization module for FinOpsOptimizer.

This module provides performance optimizations for large-scale deployments
including caching, parallel processing, and resource management.
"""

import asyncio
import concurrent.futures
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from functools import lru_cache
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from .config import Config


class PerformanceOptimizer:
    """
    Performance optimization utilities for FinOpsOptimizer.
    
    Provides caching, parallel processing, and resource management
    for large-scale deployments.
    """
    
    def __init__(self, config: Config):
        """
        Initialize PerformanceOptimizer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Cache settings
        self.cache_dir = Path(config.output_dir) / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Thread pool for parallel processing
        self.max_workers = config.performance.get('max_workers', 4)
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        )
        
        # Cache TTL (time to live) in seconds
        self.cache_ttl = config.performance.get('cache_ttl', 3600)  # 1 hour
        
        # Performance metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'parallel_tasks': 0,
            'total_execution_time': 0
        }
    
    def cache_key(self, prefix: str, **kwargs) -> str:
        """
        Generate a cache key.
        
        Args:
            prefix: Cache key prefix
            **kwargs: Key-value pairs to include in the cache key
            
        Returns:
            Cache key string
        """
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (dict, list)):
                key_parts.append(f"{k}={hash(json.dumps(v, sort_keys=True))}")
            else:
                key_parts.append(f"{k}={v}")
        
        return "_".join(key_parts)
    
    def get_cache_path(self, cache_key: str) -> Path:
        """
        Get cache file path for a cache key.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cache file path
        """
        return self.cache_dir / f"{cache_key}.json"
    
    def is_cache_valid(self, cache_path: Path) -> bool:
        """
        Check if cache is still valid.
        
        Args:
            cache_path: Path to cache file
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_path.exists():
            return False
        
        # Check file age
        file_age = time.time() - cache_path.stat().st_mtime
        return file_age < self.cache_ttl
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data if available and valid.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None if not available/valid
        """
        cache_path = self.get_cache_path(cache_key)
        
        if self.is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                self.metrics['cache_hits'] += 1
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return data
            except Exception as e:
                self.logger.warning(f"Failed to read cache file {cache_path}: {e}")
        
        self.metrics['cache_misses'] += 1
        self.logger.debug(f"Cache miss for key: {cache_key}")
        return None
    
    def set_cached_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Cache data with the given key.
        
        Args:
            cache_key: Cache key
            data: Data to cache
        """
        cache_path = self.get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            self.logger.debug(f"Cached data for key: {cache_key}")
        except Exception as e:
            self.logger.warning(f"Failed to write cache file {cache_path}: {e}")
    
    def clear_cache(self, prefix: Optional[str] = None) -> None:
        """
        Clear cache files.
        
        Args:
            prefix: Optional prefix to clear only specific cache files
        """
        if prefix:
            pattern = f"{prefix}_*.json"
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        
        self.logger.info(f"Cleared cache for prefix: {prefix or 'all'}")
    
    def parallel_execute(self, 
                        tasks: List[Callable],
                        timeout: Optional[int] = None) -> List[Any]:
        """
        Execute tasks in parallel.
        
        Args:
            tasks: List of callable tasks
            timeout: Optional timeout in seconds
            
        Returns:
            List of results from tasks
        """
        start_time = time.time()
        self.metrics['parallel_tasks'] += len(tasks)
        
        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            ) as executor:
                future_to_task = {
                    executor.submit(task): i 
                    for i, task in enumerate(tasks)
                }
                
                results = [None] * len(tasks)
                
                for future in concurrent.futures.as_completed(
                    future_to_task, timeout=timeout
                ):
                    task_index = future_to_task[future]
                    try:
                        results[task_index] = future.result()
                    except Exception as e:
                        self.logger.error(f"Task {task_index} failed: {e}")
                        results[task_index] = {'error': str(e)}
                
                execution_time = time.time() - start_time
                self.metrics['total_execution_time'] += execution_time
                
                self.logger.info(
                    f"Executed {len(tasks)} tasks in parallel in {execution_time:.2f}s"
                )
                
                return results
                
        except concurrent.futures.TimeoutError:
            self.logger.error(f"Parallel execution timed out after {timeout}s")
            return [{'error': 'timeout'}] * len(tasks)
    
    async def async_execute(self, 
                           tasks: List[Callable],
                           timeout: Optional[int] = None) -> List[Any]:
        """
        Execute tasks asynchronously.
        
        Args:
            tasks: List of async callable tasks
            timeout: Optional timeout in seconds
            
        Returns:
            List of results from tasks
        """
        start_time = time.time()
        self.metrics['parallel_tasks'] += len(tasks)
        
        try:
            if timeout:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=timeout
                )
            else:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error dicts
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append({'error': str(result)})
                else:
                    processed_results.append(result)
            
            execution_time = time.time() - start_time
            self.metrics['total_execution_time'] += execution_time
            
            self.logger.info(
                f"Executed {len(tasks)} tasks asynchronously in {execution_time:.2f}s"
            )
            
            return processed_results
            
        except asyncio.TimeoutError:
            self.logger.error(f"Async execution timed out after {timeout}s")
            return [{'error': 'timeout'}] * len(tasks)
    
    def batch_process(self, 
                     items: List[Any],
                     batch_size: int,
                     processor: Callable) -> List[Any]:
        """
        Process items in batches.
        
        Args:
            items: List of items to process
            batch_size: Size of each batch
            processor: Function to process each batch
            
        Returns:
            List of processed results
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = processor(batch)
            results.extend(batch_results)
            
            self.logger.debug(f"Processed batch {i//batch_size + 1}")
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        cache_hit_rate = 0
        if self.metrics['cache_hits'] + self.metrics['cache_misses'] > 0:
            cache_hit_rate = (
                self.metrics['cache_hits'] / 
                (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            )
        
        return {
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': cache_hit_rate,
            'parallel_tasks': self.metrics['parallel_tasks'],
            'total_execution_time': self.metrics['total_execution_time'],
            'max_workers': self.max_workers,
            'cache_ttl': self.cache_ttl
        }
    
    def optimize_memory_usage(self) -> None:
        """
        Optimize memory usage by clearing caches and garbage collection.
        """
        import gc
        
        # Clear old cache files
        current_time = time.time()
        for cache_file in self.cache_dir.glob("*.json"):
            if current_time - cache_file.stat().st_mtime > self.cache_ttl * 2:
                cache_file.unlink()
        
        # Force garbage collection
        gc.collect()
        
        self.logger.info("Memory optimization completed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.executor.shutdown(wait=True)


# Decorator for caching function results
def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Optional TTL override in seconds
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = self.cache_key(
                f"{prefix}_{func.__name__}",
                args=args,
                kwargs=kwargs
            )
            
            # Try to get cached result
            cached_result = self.get_cached_data(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(self, *args, **kwargs)
            self.set_cached_data(cache_key, result)
            
            return result
        
        return wrapper
    return decorator 