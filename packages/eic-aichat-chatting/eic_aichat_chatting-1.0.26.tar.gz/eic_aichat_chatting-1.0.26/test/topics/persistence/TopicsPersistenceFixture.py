# -*- coding: utf-8 -*-
from pip_services4_data.query import FilterParams, PagingParams

from aichatchatting.topics.data.Topic import Topic
from aichatchatting.topics.persistence.ITopicsPersistence import ITopicsPersistence

TOPIC1 = Topic(
    id='1',
    name='00001',
    type="Type1",
    site_id='1',
    content='ABC'
)

TOPIC2 = Topic(
    id='2',
    name='00001',
    type="Type2",
    site_id='1',
    content='XYZ'
)

TOPIC3 = Topic(
    id='3',
    name='00002',
    type="Type1",
    site_id='2',
    content='DEF'
)


class TopicsPersistenceFixture:
    _persistence: ITopicsPersistence

    def __init__(self, persistence: ITopicsPersistence):
        assert persistence is not None
        self._persistence = persistence

    def test_create_topics(self):
        # Create the first topic
        topic = self._persistence.create(None, TOPIC1)
        assert TOPIC1.name == topic.name
        assert TOPIC1.site_id == topic.site_id
        assert TOPIC1.type == topic.type
        assert topic.content is not None

        # Create the second topic
        topic = self._persistence.create(None, TOPIC2)
        assert TOPIC2.name == topic.name
        assert TOPIC2.site_id == topic.site_id
        assert TOPIC2.type == topic.type
        assert topic.content is not None

        # Create the third topic
        topic = self._persistence.create(None, TOPIC3)
        assert TOPIC3.name == topic.name
        assert TOPIC3.site_id == topic.site_id
        assert TOPIC3.type == topic.type
        assert topic.content is not None

    def test_crud_operations(self):
        # Create items
        self.test_create_topics()

        # Get all topics
        page = self._persistence.get_page_by_filter(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 3

        topic1: Topic = page.data[0]

        # Update the topic
        topic1.name = 'ABC'

        topic = self._persistence.update(None, topic1)
        assert topic1.id == topic.id
        assert 'ABC' == topic.name

        # Get topic by name
        topic = self._persistence.get_one_by_name(None, topic1.name)
        assert topic1.id == topic.id

        # Delete the topic
        topic = self._persistence.delete_by_id(None, topic1.id)
        assert topic1.id == topic.id

        # Try to get deleted topic
        topic = self._persistence.get_one_by_id(None, topic1.id)
        assert topic is None

    def test_get_with_filters(self):
        # Create items
        self.test_create_topics()

        # Filter by id
        page = self._persistence.get_page_by_filter(None, FilterParams.from_tuples('id', '1'), PagingParams())
        assert len(page.data) == 1

        # Filter by name
        page = self._persistence.get_page_by_filter(None,
                                                    FilterParams.from_tuples('names', '00001,00003'),
                                                    PagingParams())
        assert len(page.data) == 2

        # Filter by site_id
        page = self._persistence.get_page_by_filter(None,
                                                    FilterParams.from_tuples('site_id', '1'),
                                                    PagingParams())
        assert len(page.data) == 2