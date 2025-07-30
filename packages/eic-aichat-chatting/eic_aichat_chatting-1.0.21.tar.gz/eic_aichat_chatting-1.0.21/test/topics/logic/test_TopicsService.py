# -*- coding: utf-8 -*-
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor
from pip_services4_data.query import PagingParams, FilterParams

from aichatchatting.topics.data.Topic import Topic
from aichatchatting.topics.logic.TopicsService import TopicsService
from aichatchatting.topics.persistence.TopicsMemoryPersistence import TopicsMemoryPersistence

TOPIC1 = Topic(
    id='1',
    name='00001',
    type="Type1",
    site_id='1',
    content='ABC'
)

TOPIC2 = Topic(
    id='2',
    name='00002',
    type="Type2",
    site_id='1',
    content='XYZ'
)


class TestTopicsService:
    persistence: TopicsMemoryPersistence
    service: TopicsService

    def setup_method(self):
        self.persistence = TopicsMemoryPersistence()
        self.persistence.configure(ConfigParams())

        self.service = TopicsService()
        self.service.configure(ConfigParams())

        references = References.from_tuples(
            Descriptor('aichatchatting-topics', 'persistence', 'memory', 'default', '1.0'), self.persistence,
            Descriptor('aichatchatting-topics', 'service', 'default', 'default', '1.0'), self.service
        )

        self.service.set_references(references)

        self.persistence.open(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        # Create the first topic
        topic = self.service.create_topic(None, TOPIC1)
        assert TOPIC1.name == topic.name
        assert TOPIC1.site_id == topic.site_id
        assert TOPIC1.type == topic.type
        assert topic.content is not None

        # Create the second topic
        topic = self.service.create_topic(None, TOPIC2)
        assert TOPIC2.name == topic.name
        assert TOPIC2.site_id == topic.site_id
        assert TOPIC2.type == topic.type
        assert topic.content is not None

        # Get all topics
        page = self.service.get_topics(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 2

        topic1: Topic = page.data[0]

        # Update the topic
        topic1.name = 'ABC'

        topic = self.service.update_topic(None, topic1)
        assert topic1.id == topic.id
        assert 'ABC' == topic.name

        # Get topic by name
        topic = self.service.get_topic_by_name(None, topic1.name)
        assert topic1.id == topic.id

        # Delete the topic
        topic = self.service.delete_topic_by_id(None, topic1.id)
        assert topic1.id == topic.id

        # Try to get deleted topic
        topic = self.service.get_topic_by_id(None, topic1.id)
        assert topic is None