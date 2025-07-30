# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict
from pip_services4_data.data import IStringIdentifiable


class MessagesV1(IStringIdentifiable):
    def __init__(self, id: str = None, user_id: str = None, topic_id: str = None, inquiry: str = None,
                response: str = None, timestamp: datetime = None):
        self.id = id
        self.user_id = user_id
        self.topic_id = topic_id
        self.inquiry = inquiry
        self.timestamp = timestamp or datetime.now()
        self.response = response

    def to_dict(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic_id': self.topic_id,
            'inquiry': self.inquiry,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'response': self.response,
        }
    