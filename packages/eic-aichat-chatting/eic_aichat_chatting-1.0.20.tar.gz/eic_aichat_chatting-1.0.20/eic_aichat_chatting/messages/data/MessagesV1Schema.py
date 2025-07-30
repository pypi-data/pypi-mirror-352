from pip_services4_commons.convert import TypeCode
from pip_services4_data.validate import ObjectSchema


class MessagesV1Schema(ObjectSchema):
    def __init__(self):
        super().__init__()

        self.with_optional_property('id', TypeCode.String)
        self.with_required_property('user_id', TypeCode.String)
        self.with_optional_property('topic_id', TypeCode.String)
        self.with_optional_property('inquiry', TypeCode.String)
        self.with_optional_property('timestamp', TypeCode.DateTime)
        self.with_optional_property('response', TypeCode.String)
