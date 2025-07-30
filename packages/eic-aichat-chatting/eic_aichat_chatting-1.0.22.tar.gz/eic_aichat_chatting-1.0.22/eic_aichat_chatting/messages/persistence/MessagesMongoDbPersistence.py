# -*- coding: utf-8 -*-
from typing import Optional, Any

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams
from pip_services4_mongodb.persistence import IdentifiableMongoDbPersistence

from ..data import MessagesV1
from .IMessagesPersistence import IMessagesPersistence


class MessagesMongoDbPersistence(IdentifiableMongoDbPersistence, IMessagesPersistence):

    def __init__(self):
        super().__init__('messages')

        self._max_page_size = 1000

    def __compose_filter(self, filter_params: FilterParams):
        filter_params = filter_params or FilterParams()

        filters = []

        id = filter_params.get_as_nullable_string('id')
        if id is not None:
            filters.append({'_id': id})

        user_id = filter_params.get_as_nullable_string('user_id')
        if user_id is not None:
            filters.append({'user_id': user_id})

        topic_id = filter_params.get_as_nullable_string('topic_id')
        if topic_id is not None:
            filters.append({'topic_id': topic_id})

        return None if len(filters) < 1 else {'$and': filters}

    def get_page_by_filter(self, context: Optional[IContext], filter: Any, paging: PagingParams,
                           sort: Any = None, select: Any = None) -> DataPage:
        return super().get_page_by_filter(context, self.__compose_filter(filter), paging, None, None)
    
    def create(self, context: Optional[IContext], message: MessagesV1) -> MessagesV1:
        return super().create(context, message.to_dict())

    def update(self, context: Optional[IContext], message: MessagesV1) -> MessagesV1:
        return super().update(context, message.to_dict())

