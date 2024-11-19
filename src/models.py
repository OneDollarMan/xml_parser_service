from datetime import datetime
from sqlalchemy import Integer, Date, ForeignKey, Text, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class AnalyzeRequest(Base):
    __tablename__ = 'analyze_request'

    STATUS_CREATED = 'status_created'
    STATUS_FINISHED = 'status_finished'
    STATUS_ERROR = 'status_error'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(Text, server_default=STATUS_CREATED)
    report_url: Mapped[str] = mapped_column(Text)
    report_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    llm_result: Mapped[str | None] = mapped_column(Text, nullable=True)


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey('analyze_request.id'))
    name: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(Text)
