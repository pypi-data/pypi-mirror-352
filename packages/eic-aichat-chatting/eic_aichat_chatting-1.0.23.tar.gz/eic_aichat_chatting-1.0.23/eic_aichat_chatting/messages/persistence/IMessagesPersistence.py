# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import MessagesV1


class IMessagesPersistence(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def get_page_by_filter(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        pass

    def get_one_by_id(self, context: Optional[IContext], id: str) -> MessagesV1:
        pass

    def create(self, context: Optional[IContext], message: MessagesV1) -> MessagesV1:
        pass

    def update(self, context: Optional[IContext], message: MessagesV1) -> MessagesV1:
        pass

    def delete_by_id(self, context: Optional[IContext], id: str) -> MessagesV1:
        pass