from abc import ABCMeta
from typing import Any, Iterable, Optional, Union

from sqlalchemy import true
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Query
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.database.models.base import Base
from app.database.tools.decorators import check_operational
from app.tools.exceptions import DbError, DbOperationalError


class Service(metaclass=ABCMeta):

    def __init__(self, session: sessionmaker, table: Base):
        self._table = table
        self._session: sessionmaker = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _commit(self) -> None:
        try:
            self._session.commit()
        except OperationalError as error:
            raise DbOperationalError(f"{error}") from error
        except SQLAlchemyError as error:
            self._session.rollback()
            raise DbError(error) from error

    def _filter(self, column_name: str, value: Optional[Union[str, Iterable]], table: Optional[Base] = None) -> Any:
        table = table or self._table
        if isinstance(value, Iterable) and not isinstance(value, str):
            return getattr(table, column_name).in_(value)
        return (getattr(table, column_name) == value)   # pylint: disable=superfluous-parens

    def columns(self) -> Iterable:
        return self._table.__table__.columns.keys() if self._table else []

    def delete(self, **kwargs) -> None:
        for item in self.list(**kwargs):
            self._session.delete(item)

        self._commit()

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def list(self, *order_by, additional_filters: Optional[Any] = None, limit: Optional[int] = None, page: int = 0, **kwargs):
        return self.query(*order_by, filters=self.format_filters(additional_filters=additional_filters, **kwargs),
                          limit=limit, page=page)

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2),
           stop=stop_after_attempt(2))
    def list_or(self, *order_by, additional_filters: Optional[Any] = None, limit: Optional[int] = None, page: int = 0, **kwargs):
        return self.query(*order_by,
                          filters=self.format_filters_or(additional_filters=additional_filters, **kwargs),
                          limit=limit, page=page)

    @check_operational
    def query(self, *order_by, session: Optional[sessionmaker] = None, table: Optional[Base] = None, filters: Optional[Any] = None,
              limit: Optional[int] = None, page: int = 0) -> Query:
        session = session or self._session
        query = session.query(table or self._table)
        if len(order_by) > 0:
            query = query.order_by(*order_by)
        if filters is not None:
            query = query.filter(filters)
        if page and limit:
            query = query.offset(page * limit).limit(limit)
        elif limit:
            query = query.limit(limit)
        return query

    def format_filters(self, additional_filters=None, **kwargs) -> Any:
        filters = additional_filters or true()

        for column_name, filter_value in kwargs.items():
            filters = filters & self._filter(column_name=column_name, value=filter_value)
        return filters

    def insert(self, items: Union[Iterable, str]):
        method = 'add_all' if isinstance(items, Iterable) and not isinstance(items, str) else 'add'
        getattr(self._session, method)(items)
        self._commit()

    @check_operational
    def intersect(self, session: Optional[sessionmaker] = None, table: Optional[Base] = None, filters: Optional[Iterable] = None):
        session = session or self._session
        query = session.query(table or self._table)
        for inter_filter in filters or []:
            query = query.intersect(session.query(table or self._table).filter(inter_filter))
        return query

    @staticmethod
    def set_attribute(obj, **attributes):
        for name, value in attributes.items():
            if value is not None:
                setattr(obj, name, value)

    @retry(reraise=True, retry=retry_if_exception_type(DbOperationalError), wait=wait_fixed(2), stop=stop_after_attempt(2))
    def update(self, entry_id, **attributes):
        entry = self.get(entry_id)
        Service.set_attribute(entry, **attributes)
        self._commit()
        return self.get(entry_id)

    def get(self, entry_id):
        raise NotImplementedError