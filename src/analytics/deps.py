from typing import Annotated
from fastapi import Depends
from db.uow import UnitOfWork, get_uow
from analytics.repository import RespRepository
from analytics.service import RespondentStatService
from redis_fastapi import CacheBackendDep
from api.deps import CacheDep

def get_resp_repo(uow: UnitOfWork = Depends(get_uow)):
    return RespRepository(uow)

def get_resp_service(cache: CacheDep, resp_repo: RespRepository = Depends(get_resp_repo)):
    return RespondentStatService(
        resp_repository=resp_repo,
        cache=cache,
    )

RespondentServiceDep = Annotated[RespondentStatService, Depends(get_resp_service)]