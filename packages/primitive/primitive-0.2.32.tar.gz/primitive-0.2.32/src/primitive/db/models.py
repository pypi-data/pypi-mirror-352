from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, Query, mapped_column

from .base import Base
from .sqlite import Session

T = TypeVar("T", bound="Base")


class Manager(Generic[T]):
    def __init__(self, model_cls_lambda: Callable[[], Type[T]]) -> None:
        self.model_cls_lambda = model_cls_lambda
        self.filters: Dict[str, Any] = {}

    def create(self, **kwargs) -> T:
        with Session() as session:
            model = self.model_cls_lambda()
            obj = model(**kwargs)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def filter_by(self, **kwargs) -> "Manager[T]":
        self.filters = kwargs
        return self

    def exists(self) -> bool:
        with Session() as session:
            model = self.model_cls_lambda()
            query = session.query(model)
            query.filter_by(**self.filters)
            self.filters.clear()
            return query.count() > 0

    def all(self) -> List[T]:
        with Session() as session:
            model = self.model_cls_lambda()
            query = session.query(model)
            query.filter_by(**self.filters)
            self.filters.clear()
            return query.all()

    def first(self) -> Union[T, None]:
        with Session() as session:
            model = self.model_cls_lambda()
            query = session.query(model)
            query.filter_by(**self.filters)
            self.filters.clear()
            return query.first()

    def update(self, update: Dict[Any, Any]) -> Query[T]:
        with Session() as session:
            model = self.model_cls_lambda()
            query = session.query(model).filter_by(**self.filters)

            if query.count() > 0:
                query.update(update)
                session.commit()
                return query
            else:
                raise ValueError(f"Update failed, {model.__name__} not found")

    def delete(self) -> None:
        with Session() as session:
            model = self.model_cls_lambda()
            query = session.query(model).filter_by(**self.filters)

            if query.count() > 0:
                query.delete()
                session.commit()
            else:
                raise ValueError(f"Delete failed, {model.__name__} not found")


class JobRun(Base):
    __tablename__ = "JobRun"

    id = Column(Integer, primary_key=True)
    job_run_id: Mapped[str] = mapped_column(String, nullable=False)
    pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    objects: Manager["JobRun"] = Manager(lambda: JobRun)

    def __repr__(self):
        return f"<JobRun(id={self.id} job_run_id={self.job_run_id}, pid={self.pid})>"
