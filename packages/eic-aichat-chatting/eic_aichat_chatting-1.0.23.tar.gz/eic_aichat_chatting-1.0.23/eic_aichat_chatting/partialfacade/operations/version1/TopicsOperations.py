# -*- coding: utf-8 -*-
import json

import bottle
from pip_services4_commons.convert import TypeCode
from pip_services4_components.refer import Descriptor, IReferences
from pip_services4_data.validate import ObjectSchema
from pip_services4_http.controller import RestOperations, RestController
from pip_services4_components.context import Context
from pip_services4_data.query import FilterParams, PagingParams

from eic_aichat_users.partialfacade.operations.version1.Authorize import AuthorizerV1

from eic_aichat_chatting.topics.data import TopicV1, TopicV1Schema
from eic_aichat_chatting.topics.logic.ITopicsService import ITopicsService

from eic_aichat_chatting.messages.data import MessagesV1, MessagesV1Schema
from eic_aichat_chatting.messages.logic.IMessagesService import IMessagesService


class TopicsOperations(RestOperations):
    def __init__(self):
        super().__init__()
        self._topics_service: ITopicsService = None
        self._messages_service: IMessagesService = None
        self._dependency_resolver.put("topics-service", Descriptor('aichatchatting-topics', 'service', '*', '*', '1.0'))
        self._dependency_resolver.put("messages-service", Descriptor('aichatchatting-messages', 'service', '*', '*', '1.0'))

    def configure(self, config):
        super().configure(config)

    def set_references(self, references: IReferences):
        super().set_references(references)
        self._topics_service = self._dependency_resolver.get_one_required('topics-service')
        self._messages_service = self._dependency_resolver.get_one_required('messages-service')

    def get_topics(self):
        context = Context.from_trace_id(self._get_trace_id())
        filter_params = self._get_filter_params()
        paging_params = self._get_paging_params()

        user_id = bottle.request.user_id
        filter_params.append({"owner_id": user_id})
        try:
            res = self._topics_service.get_topics(context, filter_params, paging_params)
            res.data = [topic.to_dict() for topic in res.data]
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def get_topic_by_id(self, topic_id):
        context = Context.from_trace_id(self._get_trace_id())
        paging_params = self._get_paging_params()
        try:
            res = self._topics_service.get_topic_by_id(context, topic_id)

            filter_params = FilterParams.from_tuples("topic_id", topic_id)
            messages = self._messages_service.get_messages(context, filter_params, paging_params)

            res.messages = messages.data
            res.total = messages.total
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def create_topic(self):
        context = Context.from_trace_id(self._get_trace_id())
        data = bottle.request.json
        topic = data if isinstance(data, dict) else json.loads(data)
        topic = None if not topic else TopicV1(**topic)
        topic.owner_id = bottle.request.user_id
        try:
            res = self._topics_service.create_topic(context, topic)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def update_topic(self):
        context = Context.from_trace_id(self._get_trace_id())
        data = bottle.request.json
        topic = data if isinstance(data, dict) else json.loads(data)
        topic = None if not topic else TopicV1(**topic)
        try:
            res = self._topics_service.update_topic(context, topic)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def delete_topic_by_id(self, topic_id):
        context = Context.from_trace_id(self._get_trace_id())
        try:
            res = self._topics_service.delete_topic_by_id(context, topic_id)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def register_routes(self, controller: RestController, auth: AuthorizerV1):
        controller.register_route_with_auth('get', '/topics', None, auth.signed(),
                                  self.get_topics)

        controller.register_route_with_auth('get', '/topics/<topic_id>', ObjectSchema(True)
                                  .with_required_property("topic_id", TypeCode.String), auth.signed(),
                                  self.get_topic_by_id)

        controller.register_route_with_auth('post', '/topics', ObjectSchema(True)
                                  .with_required_property("body", TopicV1Schema()), auth.signed(),
                                  self.create_topic)

        controller.register_route_with_auth('put', '/topics', ObjectSchema(True)
                                  .with_required_property("body", TopicV1Schema()), auth.signed(),
                                  self.update_topic)

        controller.register_route_with_auth('delete', '/topics/<topic_id>', ObjectSchema(True)
                                  .with_required_property("topic_id", TypeCode.String), auth.signed(),
                                  self.delete_topic_by_id)
