from fastapi import Request, HTTPException, Depends
import time
from utils.rate_limiter import rate_limiter


async def rate_limit_20_per_minute(request: Request):
    """
    Dependency for 20 requests per minute
    """
    max_requests = 20
    window_seconds = 60
    
    # Check if allowed
    allowed, remaining, reset_time = await rate_limiter.is_allowed(request)
    
    if not allowed:
        retry_after = reset_time - int(time.time())
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Maximum {max_requests} requests per minute",
                "retry_after": retry_after
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0"
            }
        )
    
    # Add rate limit info to request state (optional)
    request.state.rate_limit = {
        "limit": max_requests,
        "remaining": remaining,
        "reset": reset_time
    }
    
    # Return nothing - just passes if allowed
    return