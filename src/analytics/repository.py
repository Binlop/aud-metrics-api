from sqlalchemy import select, func
from db.uow import UnitOfWork
from analytics.models import RespondentStat

class RespRepository:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_respondents(self, sql: str):
        stmt = (
            select(
                RespondentStat.respondent,
                func.avg(RespondentStat.weight).label("mean_weigth")
                )
            .where(sql)
            .group_by(RespondentStat.respondent)
        )
        res = await self.uow.db.execute(stmt)
        return res.all() 