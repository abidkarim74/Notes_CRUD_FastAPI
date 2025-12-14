import time
from collections import defaultdict
from fastapi import Request, HTTPException
from typing import Dict, List
import asyncio


class SimpleRateLimiter:
    """
    Simple in-memory rate limiter
    20 requests per minute per user
    """
    
    def __init__(self):
        # Store request timestamps per user
        # Format: {"user:123": [timestamp1, timestamp2, ...]}
        self.requests: Dict[str, List[float]] = defaultdict(list)
        
        # Lock for thread safety
        self.lock = asyncio.Lock()
        
        # Rate limit configuration
        self.max_requests = 20  # 20 requests
        self.window_seconds = 60  # per minute
        
        # Optional: Cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task to clean old requests"""
        async def cleanup():
            while True:
                await asyncio.sleep(300)  # Clean every 5 minutes
                await self._clean_old_requests()
        
        # Run cleanup in background
        asyncio.create_task(cleanup())
    
    async def _clean_old_requests(self):
        """Remove old request timestamps"""
        current_time = time.time()
        cutoff = current_time - self.window_seconds
        
        async with self.lock:
            # Remove empty entries and old timestamps
            keys_to_delete = []
            
            for user_key, timestamps in self.requests.items():
                # Filter out old timestamps
                self.requests[user_key] = [
                    ts for ts in timestamps if ts > cutoff
                ]
                
                # Mark empty lists for deletion
                if not self.requests[user_key]:
                    keys_to_delete.append(user_key)
            
            # Delete empty entries
            for key in keys_to_delete:
                del self.requests[key]
    
    def _get_user_key(self, request: Request) -> str:
        """
        Get unique identifier for user
        Uses JWT user_id if available, otherwise IP address
        """
        # Try to get user_id from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                # Use token as identifier (or extract user_id properly)
                # In real app, decode JWT to get user_id
                # For now, use token hash
                import hashlib
                token_hash = hashlib.md5(token.encode()).hexdigest()[:8]
                return f"user:{token_hash}"
            except:
                pass
        
        # Fallback to IP address
        client = request.client
        ip_address = client.host if client else "unknown"
        return f"ip:{ip_address}"
    
    async def is_allowed(self, request: Request) -> tuple:
        """
        Check if request is allowed
        
        Returns: (is_allowed, remaining_requests, reset_time)
        """
        user_key = self._get_user_key(request)
        current_time = time.time()
        
        async with self.lock:
            # Get user's request timestamps
            timestamps = self.requests[user_key]
            
            # Remove timestamps outside the window
            cutoff = current_time - self.window_seconds
            valid_timestamps = [ts for ts in timestamps if ts > cutoff]
            
            # Check if limit exceeded
            if len(valid_timestamps) >= self.max_requests:
                # Calculate when oldest request will expire
                oldest_timestamp = min(valid_timestamps)
                reset_time = int(oldest_timestamp + self.window_seconds)
                remaining = 0
                return False, remaining, reset_time
            
            # Add current request
            valid_timestamps.append(current_time)
            self.requests[user_key] = valid_timestamps
            
            # Calculate remaining requests
            remaining = self.max_requests - len(valid_timestamps)
            reset_time = int(current_time + self.window_seconds)
            
            return True, remaining, reset_time
    
    async def get_rate_limit_info(self, request: Request) -> dict:
        """Get current rate limit information"""
        user_key = self._get_user_key(request)
        current_time = time.time()
        
        async with self.lock:
            timestamps = self.requests.get(user_key, [])
            
            # Filter old timestamps
            cutoff = current_time - self.window_seconds
            valid_timestamps = [ts for ts in timestamps if ts > cutoff]
            
            # Update stored timestamps
            self.requests[user_key] = valid_timestamps
            
            # Calculate stats
            current_count = len(valid_timestamps)
            remaining = max(0, self.max_requests - current_count)
            
            # Calculate reset time
            if valid_timestamps:
                oldest = min(valid_timestamps)
                reset_time = int(oldest + self.window_seconds)
            else:
                reset_time = int(current_time + self.window_seconds)
            
            return {
                "limit": self.max_requests,
                "remaining": remaining,
                "reset": reset_time,
                "window": f"{self.window_seconds}s",
                "current": current_count
            }


# Create global instance
rate_limiter = SimpleRateLimiter()