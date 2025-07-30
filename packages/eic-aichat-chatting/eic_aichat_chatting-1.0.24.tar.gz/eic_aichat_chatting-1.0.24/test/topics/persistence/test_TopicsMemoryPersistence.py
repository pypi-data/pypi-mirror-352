# -*- coding: utf-8 -*-
from aichatchatting.topics.persistence.TopicsMemoryPersistence import TopicsMemoryPersistence
from test.topics.persistence.TopicsPersistenceFixture import TopicsPersistenceFixture


class TestTopicsMemoryPersistence:
    persistence: TopicsMemoryPersistence
    fixture: TopicsPersistenceFixture

    def setup_method(self):
        self.persistence = TopicsMemoryPersistence()

        self.fixture = TopicsPersistenceFixture(self.persistence)

        self.persistence.open(None)
        self.persistence.clear(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_get_with_filters(self):
        self.fixture.test_get_with_filters()