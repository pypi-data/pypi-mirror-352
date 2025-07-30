# -*- coding: utf-8 -*-
from typing import Optional, Any

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams
from pip_services4_mongodb.persistence import IdentifiableMongoDbPersistence

from ..data import TopicV1
from .ITopicsPersistence import ITopicsPersistence


class TopicsMongoDbPersistence(IdentifiableMongoDbPersistence, ITopicsPersistence):

    def __init__(self):
        super().__init__('topics')

        self._max_page_size = 1000

    def __compose_filter(self, filter_params: FilterParams):
        filter_params = filter_params or FilterParams()

        filters = []

        id = filter_params.get_as_nullable_string('id')
        if id is not None:
            filters.append({'_id': id})

        owner_id = filter_params.get_as_nullable_string('owner_id')
        if owner_id is not None:
            filters.append({'owner_id': owner_id})

        model_id = filter_params.get_as_nullable_string('model_id')
        if model_id is not None:
            filters.append({'model_id': model_id})

        tailored_model_id = filter_params.get_as_nullable_string('tailored_model_id')
        if tailored_model_id is not None:
            filters.append({'tailored_model_id': tailored_model_id})

        name = filter_params.get_as_nullable_string('name')
        if name is not None:
            filters.append({'name': name})

        temp_names = filter_params.get_as_nullable_string('names')
        if temp_names is not None:
            names = temp_names.split(',')
            filters.append({'name': {'$in': names}})

        return None if len(filters) < 1 else {'$and': filters}

    def get_page_by_filter(self, context: Optional[IContext], filter: Any, paging: PagingParams,
                           sort: Any = None, select: Any = None) -> DataPage:
        return super().get_page_by_filter(context, self.__compose_filter(filter), paging, None, None)

    def get_one_by_name(self, context: Optional[IContext], name: str) -> TopicV1:
        criteria = {'name': name}
        item = self._collection.find_one(criteria)

        if item is None:
            self._logger.trace(context, "Cannot find topic with name=%s", str(name))
        else:
            self._logger.trace(context, "Found topic with name=%s", str(name))

        item = self._convert_to_public(item)
        return item