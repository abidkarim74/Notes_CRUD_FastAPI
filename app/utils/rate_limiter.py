import time
from collections import defaultdict
from fastapi import Request
from typing import Dict, List
import asyncio
import hashlib


class SimpleRateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = asyncio.Lock()
        self.max_requests = 20  
        self.window_seconds = 60  
        self._start_cleanup_task()
    
    
    def _start_cleanup_task(self):
        async def cleanup():
            while True:
                await asyncio.sleep(300)  
                await self._clean_old_requests()
        
        asyncio.create_task(cleanup())
    
    
    async def _clean_old_requests(self):
        current_time = time.time()
        cutoff = current_time - self.window_seconds
        
        async with self.lock:
            keys_to_delete = []
            
            for user_key, timestamps in self.requests.items():
                self.requests[user_key] = [
                    ts for ts in timestamps if ts > cutoff
                ]
                
                if not self.requests[user_key]:
                    keys_to_delete.append(user_key)
            
            for key in keys_to_delete:
                del self.requests[key]
                
    
    def _get_user_key(self, request: Request) -> str:
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
              
                token_hash = hashlib.md5(token.encode()).hexdigest()[:8]
                return f"user:{token_hash}"
            
            except:
                pass
        
        client = request.client
        ip_address = client.host if client else "unknown"
        return f"ip:{ip_address}"
    
    
    async def is_allowed(self, request: Request) -> tuple:
        user_key = self._get_user_key(request)
        current_time = time.time()
        
        async with self.lock:
            timestamps = self.requests[user_key]
            
            cutoff = current_time - self.window_seconds
            valid_timestamps = [ts for ts in timestamps if ts > cutoff]
            
            if len(valid_timestamps) >= self.max_requests:
                oldest_timestamp = min(valid_timestamps)
                reset_time = int(oldest_timestamp + self.window_seconds)
                remaining = 0
                
                return False, remaining, reset_time
            
            valid_timestamps.append(current_time)
            self.requests[user_key] = valid_timestamps
            

            remaining = self.max_requests - len(valid_timestamps)
            reset_time = int(current_time + self.window_seconds)
            
            return True, remaining, reset_time
    
    
    async def get_rate_limit_info(self, request: Request) -> dict:
        user_key = self._get_user_key(request)
        current_time = time.time()
        
        async with self.lock:
            timestamps = self.requests.get(user_key, [])
            
            cutoff = current_time - self.window_seconds
            valid_timestamps = [ts for ts in timestamps if ts > cutoff]
            
            self.requests[user_key] = valid_timestamps
            
            current_count = len(valid_timestamps)
            remaining = max(0, self.max_requests - current_count)
            
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


rate_limiter = SimpleRateLimiter()