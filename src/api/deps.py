from typing import Annotated
from fastapi import Depends, Request
from core.cache import RedisCache


def get_cache(request: Request) -> RedisCache:
    return RedisCache(request.app.state.redis)


CacheDep = Annotated[RedisCache, Depends(get_cache)]