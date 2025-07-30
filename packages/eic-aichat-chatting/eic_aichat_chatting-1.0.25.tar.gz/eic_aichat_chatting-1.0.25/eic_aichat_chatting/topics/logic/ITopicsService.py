# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import TopicV1


class ITopicsService(ABC):

    @abstractmethod
    def get_topics(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def get_topic_by_id(self, context: Optional[IContext], topic_id: str) -> TopicV1:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def get_topic_by_name(self, context: Optional[IContext], name: str) -> TopicV1:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def create_topic(self, context: Optional[IContext], TopicV1: TopicV1) -> TopicV1:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def update_topic(self, context: Optional[IContext], TopicV1: TopicV1) -> TopicV1:
        raise NotImplementedError("Method is not implemented")

    @abstractmethod
    def delete_topic_by_id(self, context: Optional[IContext], topic_id: str) -> TopicV1:
        raise NotImplementedError("Method is not implemented")