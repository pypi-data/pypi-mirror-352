# -*- coding: utf-8 -*-
from pip_services4_components.refer import Descriptor
from pip_services4_components.build import Factory

from eic_aichat_chatting.topics.logic.TopicsService import TopicsService
from eic_aichat_chatting.topics.persistence.TopicsMemoryPersistence import TopicsMemoryPersistence
from eic_aichat_chatting.topics.persistence.TopicsMongoDbPersistence import TopicsMongoDbPersistence
from eic_aichat_chatting.chatprocessor.logic.BasicService import BasicService


from eic_aichat_chatting.messages.logic.MessagesService import MessagesService
from eic_aichat_chatting.messages.persistence.MessagesMemoryPersistence import MessagesMemoryPersistence
from eic_aichat_chatting.messages.persistence.MessagesMongoDbPersistence import MessagesMongoDbPersistence


class AIChatChattingFactory(Factory):
    __MemoryTopicsPersistenceDescriptor = Descriptor('aichatchatting-topics', 'persistence', 'memory', '*', '1.0')
    __MongoDbTopicsPersistenceDescriptor = Descriptor('aichatchatting-topics', 'persistence', 'mongodb', '*', '1.0')
    __ServiceTopicsDescriptor = Descriptor('aichatchatting-topics', 'service', 'default', '*', '1.0')

    __MemoryMessagesPersistenceDescriptor = Descriptor('aichatchatting-messages', 'persistence', 'memory', '*', '1.0')
    __MongoDbMessagesPersistenceDescriptor = Descriptor('aichatchatting-messages', 'persistence', 'mongodb', '*', '1.0')
    __ServiceMessagesDescriptor = Descriptor('aichatchatting-messages', 'service', 'default', '*', '1.0')

    __ChatprocessorServiceDescriptor = Descriptor("aichatchatting-chatprocessor", "service", "*", "*", "1.0")


    def __init__(self):
        super().__init__()

        self.register_as_type(self.__MemoryTopicsPersistenceDescriptor, TopicsMemoryPersistence)
        self.register_as_type(self.__MongoDbTopicsPersistenceDescriptor, TopicsMongoDbPersistence)
        self.register_as_type(self.__ServiceTopicsDescriptor, TopicsService)

        self.register_as_type(self.__MemoryMessagesPersistenceDescriptor, MessagesMemoryPersistence)
        self.register_as_type(self.__MongoDbMessagesPersistenceDescriptor, MessagesMongoDbPersistence)
        self.register_as_type(self.__ServiceMessagesDescriptor, MessagesService)

        self.register_as_type(self.__ChatprocessorServiceDescriptor, BasicService)
