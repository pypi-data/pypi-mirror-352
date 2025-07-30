# -*- coding: utf-8 -*-
from typing import Optional, Any, Callable

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams, SortParams
from pip_services4_persistence.persistence import IdentifiableMemoryPersistence

from ..data import TopicV1
from .ITopicsPersistence import ITopicsPersistence


class TopicsMemoryPersistence(IdentifiableMemoryPersistence, ITopicsPersistence):

    def __init__(self):
        super().__init__()

        self._max_page_size = 1000

    def __compose_filter(self, filter_params: FilterParams) -> Callable[[TopicV1], bool]:
        filter_params = filter_params or FilterParams()

        id = filter_params.get_as_nullable_string('id')
        owner_id = filter_params.get_as_nullable_string('owner_id')
        name = filter_params.get_as_nullable_string('name')
        model_id = filter_params.get_as_nullable_string('model_id')
        tailored_model_id = filter_params.get_as_nullable_string('tailored_model_id')
        names = filter_params.get_as_nullable_string('names')

        if isinstance(names, str):
            names = names.split(',')
        if not isinstance(names, list):
            names = None

        def filter_action(item: TopicV1) -> bool:
            if id is not None and item.id != id:
                return False
            if owner_id is not None and item.owner_id != owner_id:
                return False
            if model_id is not None and item.model_id != model_id:
                return False
            if tailored_model_id is not None and item.tailored_model_id != tailored_model_id:
                return False
            if name is not None and item.name != name:
                return False
            if names is not None and item.name not in names:
                return False
            return True

        return filter_action

    def get_page_by_filter(self, context: Optional[IContext], filter: FilterParams, paging: PagingParams,
                           sort: SortParams = None, select: Any = None) -> DataPage:
        return super().get_page_by_filter(context, self.__compose_filter(filter), paging, None, None)

    def get_one_by_name(self, context: Optional[IContext], name: str) -> TopicV1:
        filtered = list(filter(lambda item: item.name == name, self._items))
        item = None if len(filtered) < 1 else filtered[0]

        if item is None:
            self._logger.trace(context, "Cannot find topic with name=%s", str(name))
        else:
            self._logger.trace(context, "Found topic with name=%s", str(name))

        return item