# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable, Descriptor
from pip_services4_data.keys import IdGenerator
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import TopicV1
from ..persistence import ITopicsPersistence
from .ITopicsService import ITopicsService


class TopicsService(ITopicsService, IConfigurable, IReferenceable):
    __persistence: ITopicsPersistence = None

    def configure(self, config: ConfigParams):
        pass

    def set_references(self, references: IReferences):
        self.__persistence = references.get_one_required(
            Descriptor('aichatchatting-topics', 'persistence', '*', '*', '1.0')
        )

    def get_topics(self, context: Optional[IContext], filter_params: FilterParams,
                   paging: PagingParams) -> DataPage:
        return self.__persistence.get_page_by_filter(context, filter_params, paging)

    def get_topic_by_id(self, context: Optional[IContext], topic_id: str) -> TopicV1:
        return self.__persistence.get_one_by_id(context, topic_id)

    def get_topic_by_name(self, context: Optional[IContext], name: str) -> TopicV1:
        return self.__persistence.get_one_by_name(context, name)

    def create_topic(self, context: Optional[IContext], topic: TopicV1) -> TopicV1:
        topic.id = topic.id or IdGenerator.next_long()
        topic.created_time = datetime.now()
        return self.__persistence.create(context, topic)

    def update_topic(self, context: Optional[IContext], topic: TopicV1) -> TopicV1:
        topic.updated_time = datetime.now()
        return self.__persistence.update(context, topic)

    def delete_topic_by_id(self, context: Optional[IContext], topic_id: str) -> TopicV1:
        return self.__persistence.delete_by_id(context, topic_id)
