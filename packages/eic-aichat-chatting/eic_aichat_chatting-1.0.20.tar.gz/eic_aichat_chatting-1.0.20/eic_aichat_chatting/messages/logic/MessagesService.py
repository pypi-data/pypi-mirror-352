# -*- coding: utf-8 -*-
from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable, Descriptor
from pip_services4_data.keys import IdGenerator
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import MessagesV1
from ..persistence import IMessagesPersistence
from .IMessagesService import IMessagesService


class MessagesService(IMessagesService, IConfigurable, IReferenceable):
    __persistence: IMessagesPersistence = None

    def configure(self, config: ConfigParams):
        pass

    def set_references(self, references: IReferences):
        self.__persistence = references.get_one_required(
            Descriptor('aichatchatting-messages', 'persistence', '*', '*', '1.0')
        )

    def get_messages(self, context: Optional[IContext], filter_params: FilterParams,
                   paging: PagingParams) -> DataPage:
        return self.__persistence.get_page_by_filter(context, filter_params, paging)

    def get_message_by_id(self, context: Optional[IContext], message_id: str) -> MessagesV1:
        return self.__persistence.get_one_by_id(context, message_id)

    def create_message(self, context: Optional[IContext], MessagesV1: MessagesV1) -> MessagesV1:
        MessagesV1.id = MessagesV1.id or IdGenerator.next_long()
        return self.__persistence.create(context, MessagesV1)

    def update_message(self, context: Optional[IContext], MessagesV1: MessagesV1) -> MessagesV1:
        return self.__persistence.update(context, MessagesV1)

    def delete_message_by_id(self, context: Optional[IContext], message_id: str) -> MessagesV1:
        return self.__persistence.delete_by_id(context, message_id)
