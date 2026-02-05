"""Rate limiter for LinkedIn Premium (token bucket algorithm)."""
import time
import asyncio
from typing import Dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from src.config import settings
from src.utils.logger import logger


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: int
    tokens: float = field(default=0)
    last_refill: datetime = field(default_factory=datetime.utcnow)
    refill_rate: float = field(default=0)  # tokens per second
    
    def __post_init__(self):
        """Initialize tokens to capacity."""
        self.tokens = float(self.capacity)
    
    def refill(self) -> None:
        """Refill tokens based on time elapsed."""
        now = datetime.utcnow()
        elapsed = (now - self.last_refill).total_seconds()
        new_tokens = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
    
    async def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens. Returns True if successful.
        Waits if not enough tokens are available.
        """
        self.refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        # Calculate wait time
        tokens_needed = tokens - self.tokens
        wait_time = tokens_needed / self.refill_rate
        
        logger.info(
            "rate_limit_waiting",
            tokens_needed=tokens_needed,
            wait_seconds=wait_time,
        )
        
        await asyncio.sleep(wait_time)
        self.refill()
        self.tokens -= tokens
        return True


class RateLimiter:
    """
    Rate limiter for LinkedIn Premium.
    - Daily limit: 40 requests
    - Hourly limit: 10 requests
    - Min delay between requests: 10-15 seconds
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        # Daily bucket: 40 requests per day
        daily_refill_rate = settings.linkedin_daily_limit / (24 * 60 * 60)
        self.daily_bucket = TokenBucket(
            capacity=settings.linkedin_daily_limit,
            refill_rate=daily_refill_rate,
        )
        
        # Hourly bucket: 10 requests per hour
        hourly_refill_rate = settings.linkedin_hourly_limit / (60 * 60)
        self.hourly_bucket = TokenBucket(
            capacity=settings.linkedin_hourly_limit,
            refill_rate=hourly_refill_rate,
        )
        
        self.last_request_time: datetime = datetime.utcnow()
        
        # Regional delays (seconds)
        self.region_delays: Dict[str, int] = {
            "Eastern_Europe": 12,
            "Far_East": 15,
        }
    
    async def acquire(self, region: str = "Eastern_Europe") -> None:
        """
        Acquire permission to make a request.
        Enforces daily limit, hourly limit, and minimum delays.
        """
        # Enforce minimum delay since last request
        min_delay = self.region_delays.get(region, settings.linkedin_min_delay_seconds)
        elapsed = (datetime.utcnow() - self.last_request_time).total_seconds()
        
        if elapsed < min_delay:
            wait_time = min_delay - elapsed
            logger.info(
                "rate_limit_min_delay",
                region=region,
                wait_seconds=wait_time,
            )
            await asyncio.sleep(wait_time)
        
        # Consume from both buckets
        await self.daily_bucket.consume(1)
        await self.hourly_bucket.consume(1)
        
        self.last_request_time = datetime.utcnow()
        
        logger.info(
            "rate_limit_acquired",
            region=region,
            daily_tokens_remaining=self.daily_bucket.tokens,
            hourly_tokens_remaining=self.hourly_bucket.tokens,
        )
    
    def get_status(self) -> Dict[str, float]:
        """Get current rate limiter status."""
        self.daily_bucket.refill()
        self.hourly_bucket.refill()
        
        return {
            "daily_tokens_remaining": self.daily_bucket.tokens,
            "daily_capacity": self.daily_bucket.capacity,
            "hourly_tokens_remaining": self.hourly_bucket.tokens,
            "hourly_capacity": self.hourly_bucket.capacity,
        }


# Global rate limiter instance
linkedin_rate_limiter = RateLimiter()
