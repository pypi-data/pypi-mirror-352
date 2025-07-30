# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import TopicV1


class ITopicsPersistence(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def get_page_by_filter(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        pass

    def get_one_by_id(self, context: Optional[IContext], topic_id: str) -> TopicV1:
        pass

    def get_one_by_name(self, context: Optional[IContext], name: str) -> TopicV1:
        pass

    def create(self, context: Optional[IContext], topic: TopicV1) -> TopicV1:
        pass

    def update(self, context: Optional[IContext], topic: TopicV1) -> TopicV1:
        pass

    def delete_by_id(self, context: Optional[IContext], topic_id: str) -> TopicV1:
        pass