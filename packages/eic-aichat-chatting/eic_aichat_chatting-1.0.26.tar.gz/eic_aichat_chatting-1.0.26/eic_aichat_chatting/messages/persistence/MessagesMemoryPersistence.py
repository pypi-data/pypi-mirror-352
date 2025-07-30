# -*- coding: utf-8 -*-
from typing import Optional, Any, Callable

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams, SortParams
from pip_services4_persistence.persistence import IdentifiableMemoryPersistence

from ..data import MessagesV1
from .IMessagesPersistence import IMessagesPersistence


class MessagesMemoryPersistence(IdentifiableMemoryPersistence, IMessagesPersistence):

    def __init__(self):
        super().__init__()

        self._max_page_size = 1000

    def __compose_filter(self, filter_params: FilterParams) -> Callable[[MessagesV1], bool]:
        filter_params = filter_params or FilterParams()

        id = filter_params.get_as_nullable_string('id')
        user_id = filter_params.get_as_nullable_string('user_id')
        topic_id = filter_params.get_as_nullable_string('topic_id')

        def filter_action(item: MessagesV1) -> bool:
            if id is not None and item.id != id:
                return False
            if user_id is not None and item.user_id != user_id:
                return False
            if topic_id is not None and item.topic_id != topic_id:
                return False
            return True

        return filter_action

    def get_page_by_filter(self, context: Optional[IContext], filter: FilterParams, paging: PagingParams,
                           sort: SortParams = None, select: Any = None) -> DataPage:
        return super().get_page_by_filter(context, self.__compose_filter(filter), paging, None, None)
