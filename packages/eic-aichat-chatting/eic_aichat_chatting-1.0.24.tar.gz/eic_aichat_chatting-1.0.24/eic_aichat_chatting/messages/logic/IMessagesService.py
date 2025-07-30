# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import MessagesV1


class IMessagesService(ABC):

    @abstractmethod
    def get_messages(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def get_message_by_id(self, context: Optional[IContext], message_id: str) -> MessagesV1:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def create_message(self, context: Optional[IContext], MessagesV1: MessagesV1) -> MessagesV1:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def update_message(self, context: Optional[IContext], MessagesV1: MessagesV1) -> MessagesV1:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def delete_message_by_id(self, context: Optional[IContext], message_id: str) -> MessagesV1:
        raise NotImplementedError("Method is not implemented")