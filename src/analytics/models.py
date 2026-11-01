from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column 
from sqlalchemy import Integer, Date, Numeric, Index
from db.session import Base

class RespondentStat(Base):
    __tablename__ = "respondent_stat"
    __table_args__ = (
        Index("ix_respondent_date", "respondent", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    respondent: Mapped[int] = mapped_column(Integer)
    sex: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer, index=True)
    weight:  Mapped[Decimal] = mapped_column(Numeric(30, 20))

    def __str__(self):
        return f'Respondent {self.id}'